# Unit Tests for NileGov Citizen Profile Foundation
# Prototype simulation only. No live Government registry access.

import pytest
from unittest.mock import MagicMock, patch
from nilegov_stack.domain.citizen import CitizenProfile, PreferredContactChannel, CitizenProfileStatus
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.application.create_citizen_profile import CreateCitizenProfile
from nilegov_stack.application.update_citizen_contact import UpdateCitizenContact
from nilegov_stack.application.get_citizen_profile import GetCitizenProfile
from nilegov_stack.application.list_citizen_service_requests import ListCitizenServiceRequests
from nilegov_stack.infrastructure.repositories.citizen_profile_repository import InMemoryCitizenProfileRepository
from nilegov_stack.infrastructure.repositories.service_request_repository import InMemoryServiceRequestRepository
from nilegov_stack.infrastructure.repositories.frappe_citizen_profile_repository import FrappeCitizenProfileRepository


def test_citizen_profile_domain_creation_success():
    """Verifies that a valid CitizenProfile domain aggregate can be created with all fields."""
    nin = NIN("CF900000000000")
    profile = CitizenProfile(
        citizen_profile_id="CP-001",
        full_name="Demo Citizen A",
        phone="+256780000000",
        location="Ntinda, Kampala",
        email="demo.citizen.a@example.test",
        division_or_area="Ntinda Division",
        preferred_contact_channel=PreferredContactChannel.SMS,
        status=CitizenProfileStatus.ACTIVE,
        nin=nin
    )
    
    assert profile.citizen_profile_id == "CP-001"
    assert profile.full_name == "Demo Citizen A"
    assert profile.phone == "+256780000000"
    assert profile.location == "Ntinda, Kampala"
    assert profile.email == "demo.citizen.a@example.test"
    assert profile.division_or_area == "Ntinda Division"
    assert profile.preferred_contact_channel == PreferredContactChannel.SMS
    assert profile.status == CitizenProfileStatus.ACTIVE
    assert profile.nin == nin


def test_citizen_profile_optional_nin():
    """Verifies that CitizenProfile does not require a NIN."""
    profile = CitizenProfile(
        citizen_profile_id="CP-002",
        full_name="No ID Citizen",
        phone="+256772000001",
        location="Bukoto, Kampala",
        nin=None # optional NIN
    )
    
    assert profile.nin is None
    assert profile.full_name == "No ID Citizen"


def test_citizen_profile_invalid_creation_fields():
    """Verifies that missing required fields in CitizenProfile raise ValueError."""
    with pytest.raises(ValueError, match="Citizen Profile ID cannot be empty"):
        CitizenProfile("", "Name", "+256780000000", "Kampala")
        
    with pytest.raises(ValueError, match="Full name cannot be empty"):
        CitizenProfile("CP-001", "", "+256780000000", "Kampala")
        
    with pytest.raises(ValueError, match="Location cannot be empty"):
        CitizenProfile("CP-001", "Name", "+256780000000", "")
        
    with pytest.raises(ValueError, match="Phone number format.*is invalid"):
        CitizenProfile("CP-001", "Name", "invalid-phone", "Kampala")


def test_citizen_profile_update_contact_details():
    """Verifies that updating contact details modifies fields and validates format."""
    profile = CitizenProfile(
        citizen_profile_id="CP-001",
        full_name="Demo Citizen A",
        phone="+256780000000",
        location="Ntinda, Kampala"
    )
    
    profile.update_contact_details("+256701000002", "new.email@example.test", PreferredContactChannel.EMAIL)
    assert profile.phone == "+256701000002"
    assert profile.email == "new.email@example.test"
    assert profile.preferred_contact_channel == PreferredContactChannel.EMAIL
    
    with pytest.raises(ValueError, match="Phone number format.*is invalid"):
        profile.update_contact_details("bad-phone")


def test_citizen_profile_safe_demo_validation():
    """Verifies that safe linter blocks non-demo email domains."""
    profile = CitizenProfile(
        citizen_profile_id="CP-001",
        full_name="Demo Citizen A",
        phone="+256780000000",
        location="Ntinda, Kampala",
        email="demo.citizen.a@live-production.com" # non-test domain
    )
    
    with pytest.raises(ValueError, match="Production email domains are prohibited"):
        profile.validate_safe_demo_data()


def test_in_memory_repository_operations():
    """Verifies save, get_by_id, and get_by_nin in the in-memory repository."""
    repo = InMemoryCitizenProfileRepository()
    nin = NIN("CF900000000000")
    profile = CitizenProfile(
        citizen_profile_id="CP-001",
        full_name="Demo Citizen A",
        phone="+256780000000",
        location="Ntinda, Kampala",
        nin=nin
    )
    
    repo.save(profile)
    
    retrieved = repo.get_by_id("CP-001")
    assert retrieved == profile
    
    retrieved_by_nin = repo.get_by_nin("CF900000000000")
    assert retrieved_by_nin == profile
    
    assert repo.get_by_id("non-existent") is None
    assert repo.get_by_nin("CF900000000009") is None


def test_use_cases_with_in_memory():
    """Verifies CreateCitizenProfile, UpdateCitizenContact, GetCitizenProfile use cases."""
    repo = InMemoryCitizenProfileRepository()
    
    create_uc = CreateCitizenProfile(repo)
    profile = create_uc.execute(
        citizen_profile_id="CP-100",
        full_name="Test Citizen",
        phone="+256772000001",
        location="Kampala",
        email="test@example.test"
    )
    
    assert repo.get_by_id("CP-100") == profile
    
    get_uc = GetCitizenProfile(repo)
    assert get_uc.execute("CP-100") == profile
    
    update_uc = UpdateCitizenContact(repo)
    updated = update_uc.execute("CP-100", phone="+256701000002", email="updated@example.test")
    assert updated.phone == "+256701000002"
    assert updated.email == "updated@example.test"
    assert repo.get_by_id("CP-100").phone == "+256701000002"


def test_service_request_linkage():
    """Verifies that ServiceRequest can link to CitizenProfile and be retrieved."""
    req_repo = InMemoryServiceRequestRepository()
    nin = NIN("CF900000000000")
    
    request = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256780000000",
        location="Ntinda, Kampala",
        description="Lost ID",
        citizen_profile_id="CP-001" # linkage
    )
    
    req_repo.save(request)
    
    list_uc = ListCitizenServiceRequests(req_repo)
    requests = list_uc.execute("CP-001")
    
    assert len(requests) == 1
    assert requests[0].request_id == "req_001"
    assert requests[0].citizen_profile_id == "CP-001"
    assert requests[0].status == "Submitted" # Workflow status is unchanged


@patch("frappe.db.exists")
@patch("frappe.new_doc")
@patch("frappe.get_doc")
def test_frappe_citizen_repository_save_new(mock_get_doc, mock_new_doc, mock_exists):
    """Verifies FrappeCitizenProfileRepository maps domain state to new Frappe document correctly."""
    mock_exists.return_value = False
    mock_doc = MagicMock()
    mock_new_doc.return_value = mock_doc
    
    repo = FrappeCitizenProfileRepository()
    profile = CitizenProfile(
        citizen_profile_id="CP-001",
        full_name="Demo Citizen A",
        phone="+256780000000",
        location="Ntinda, Kampala",
        email="demo.citizen.a@example.test",
        nin=NIN("CF900000000000")
    )
    
    repo.save(profile)
    
    mock_exists.assert_called_once_with("NileGov Citizen Profile", "CP-001")
    mock_new_doc.assert_called_once_with("NileGov Citizen Profile")
    assert mock_doc.citizen_profile_id == "CP-001"
    assert mock_doc.full_name == "Demo Citizen A"
    assert mock_doc.phone == "+256780000000"
    assert mock_doc.location == "Ntinda, Kampala"
    assert mock_doc.email == "demo.citizen.a@example.test"
    assert mock_doc.nin == "CF900000000000"
    mock_doc.save.assert_called_once()


@patch("frappe.db.exists")
@patch("frappe.get_doc")
def test_frappe_citizen_repository_get_by_id(mock_get_doc, mock_exists):
    """Verifies FrappeCitizenProfileRepository get maps Frappe document fields to domain aggregate."""
    mock_exists.return_value = True
    
    mock_doc = MagicMock()
    mock_doc.citizen_profile_id = "CP-001"
    mock_doc.full_name = "Demo Citizen A"
    mock_doc.phone = "+256780000000"
    mock_doc.location = "Ntinda, Kampala"
    mock_doc.email = "demo.citizen.a@example.test"
    mock_doc.division_or_area = "Ntinda Division"
    mock_doc.preferred_contact_channel = "SMS"
    mock_doc.status = "Active"
    mock_doc.nin = "CF900000000000"
    mock_doc.creation = "2026-06-01 23:10:00"
    mock_doc.modified = "2026-06-02 10:00:00"
    
    mock_get_doc.return_value = mock_doc
    
    repo = FrappeCitizenProfileRepository()
    profile = repo.get_by_id("CP-001")
    
    assert profile is not None
    assert profile.citizen_profile_id == "CP-001"
    assert profile.full_name == "Demo Citizen A"
    assert profile.preferred_contact_channel == PreferredContactChannel.SMS
    assert profile.status == CitizenProfileStatus.ACTIVE
    assert str(profile.nin) == "CF900000000000"
