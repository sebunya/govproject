# Unit Tests for NileGov Consent Records Foundation
# Prototype simulation only. No live Government registry access.

import pytest
import time
from unittest.mock import MagicMock, patch
from nilegov_stack.domain.consent import ConsentRecord, ConsentPurpose, ConsentChannel, ConsentStatus
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.application.create_consent_record import CreateConsentRecord
from nilegov_stack.application.withdraw_consent import WithdrawConsent
from nilegov_stack.application.check_active_consent import CheckActiveConsent
from nilegov_stack.application.list_citizen_consent_records import ListCitizenConsentRecords
from nilegov_stack.application.list_request_consent_records import ListRequestConsentRecords
from nilegov_stack.infrastructure.repositories.consent_record_repository import InMemoryConsentRecordRepository
from nilegov_stack.infrastructure.repositories.service_request_repository import InMemoryServiceRequestRepository
from nilegov_stack.infrastructure.repositories.frappe_consent_record_repository import FrappeConsentRecordRepository
from nilegov_stack.application.run_simulated_identity_check import RunSimulatedIdentityCheck
from nilegov_stack.application.verify_payment import VerifyPayment


def test_consent_record_domain_creation_success():
    """Verifies that a valid ConsentRecord domain aggregate can be created with all fields."""
    record = ConsentRecord(
        consent_record_id="CON-001",
        citizen_profile_id="CP-001",
        consent_purpose=ConsentPurpose.SERVICE_PROCESSING,
        consent_channel=ConsentChannel.PORTAL,
        consent_status=ConsentStatus.GRANTED,
        consent_timestamp=1700000000.0,
        service_request_id="req_001",
        expiry_time=1800000000.0,
        recorded_by="officer_demo",
        notes="Demo consent notes",
        ip_address="127.0.0.1",
        user_agent="Mozilla/5.0"
    )

    assert record.consent_record_id == "CON-001"
    assert record.citizen_profile_id == "CP-001"
    assert record.consent_purpose == ConsentPurpose.SERVICE_PROCESSING
    assert record.consent_channel == ConsentChannel.PORTAL
    assert record.consent_status == ConsentStatus.GRANTED
    assert record.consent_timestamp == 1700000000.0
    assert record.service_request_id == "req_001"
    assert record.expiry_time == 1800000000.0
    assert record.recorded_by == "officer_demo"
    assert record.notes == "Demo consent notes"
    assert record.ip_address == "127.0.0.1"
    assert record.user_agent == "Mozilla/5.0"


def test_consent_record_invalid_fields():
    """Verifies that invalid fields raise ValueErrors in domain initialization."""
    with pytest.raises(ValueError, match="Consent Record ID cannot be empty"):
        ConsentRecord("", "CP-001", ConsentPurpose.SERVICE_PROCESSING, ConsentChannel.PORTAL)

    with pytest.raises(ValueError, match="Citizen Profile ID cannot be empty"):
        ConsentRecord("CON-001", "", ConsentPurpose.SERVICE_PROCESSING, ConsentChannel.PORTAL)

    with pytest.raises(ValueError, match="Invalid consent purpose"):
        ConsentRecord("CON-001", "CP-001", "Invalid Purpose", ConsentChannel.PORTAL)

    with pytest.raises(ValueError, match="Invalid consent channel"):
        ConsentRecord("CON-001", "CP-001", ConsentPurpose.SERVICE_PROCESSING, "Invalid Channel")

    with pytest.raises(ValueError, match="Invalid consent status"):
        ConsentRecord("CON-001", "CP-001", ConsentPurpose.SERVICE_PROCESSING, ConsentChannel.PORTAL, consent_status="Invalid Status")


def test_consent_record_withdraw():
    """Verifies that consent can be withdrawn, updating status and timestamp."""
    record = ConsentRecord(
        consent_record_id="CON-001",
        citizen_profile_id="CP-001",
        consent_purpose=ConsentPurpose.SERVICE_PROCESSING,
        consent_channel=ConsentChannel.PORTAL
    )
    
    assert record.consent_status == ConsentStatus.GRANTED
    assert record.withdrawal_timestamp is None
    
    withdraw_time = 1700000100.0
    record.withdraw(withdraw_time)
    
    assert record.consent_status == ConsentStatus.WITHDRAWN
    assert record.withdrawal_timestamp == withdraw_time


def test_consent_record_is_active():
    """Verifies active status checks factoring status and expiry date constraints."""
    record = ConsentRecord(
        consent_record_id="CON-001",
        citizen_profile_id="CP-001",
        consent_purpose=ConsentPurpose.SERVICE_PROCESSING,
        consent_channel=ConsentChannel.PORTAL,
        expiry_time=1700000200.0
    )
    
    # Active before expiry
    assert record.is_active(1700000100.0) is True
    
    # Inactive after expiry
    assert record.is_active(1700000300.0) is False
    
    # Inactive if withdrawn
    record.withdraw(1700000150.0)
    assert record.is_active(1700000180.0) is False


def test_use_cases_with_in_memory():
    """Verifies creation, withdrawal, active checks, and listing use cases."""
    repo = InMemoryConsentRecordRepository()
    
    create_uc = CreateConsentRecord(repo)
    record = create_uc.execute(
        consent_record_id="CON-1",
        citizen_profile_id="CP-1",
        consent_purpose=ConsentPurpose.SERVICE_PROCESSING,
        consent_channel=ConsentChannel.PORTAL
    )
    
    assert repo.get_by_id("CON-1") == record
    
    check_uc = CheckActiveConsent(repo)
    assert check_uc.execute("CP-1", ConsentPurpose.SERVICE_PROCESSING, time.time()) is True
    assert check_uc.execute("CP-1", ConsentPurpose.IDENTITY_VERIFICATION, time.time()) is False
    
    withdraw_uc = WithdrawConsent(repo)
    updated = withdraw_uc.execute("CON-1", time.time())
    assert updated.consent_status == ConsentStatus.WITHDRAWN
    assert check_uc.execute("CP-1", ConsentPurpose.SERVICE_PROCESSING, time.time()) is False
    
    # List by profile
    list_uc = ListCitizenConsentRecords(repo)
    assert len(list_uc.execute("CP-1")) == 1


def test_run_verification_checks_active_consent():
    """Verifies simulated NIRA/payment checks evaluate active consent and flag/adjust workflow status."""
    req_repo = InMemoryServiceRequestRepository()
    consent_repo = InMemoryConsentRecordRepository()
    
    # Seed request
    nin = NIN("CF900000000000")
    request = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID",
        citizen_profile_id="CP-001"
    )
    req_repo.save(request)
    
    # 1. Identity Check with NO consent seeded -> fails/warns
    mock_identity_gw = MagicMock()
    mock_identity_gw.verify_identity.return_value = {
        "success": True,
        "result": "Matched",
        "message": "NIRA Simulated Identity Verified"
    }
    
    uc_identity = RunSimulatedIdentityCheck(req_repo, mock_identity_gw, consent_repo)
    res = uc_identity.execute("req_001", actor="officer_demo", timestamp=1700000000.0)
    
    # Should flag to Requires Review because consent is not active/granted
    assert res == "Requires Review"
    
    # 2. Add granted consent and re-run -> matches
    consent_record = ConsentRecord(
        consent_record_id="CON-1",
        citizen_profile_id="CP-001",
        consent_purpose=ConsentPurpose.IDENTITY_VERIFICATION,
        consent_channel=ConsentChannel.PORTAL,
        consent_status=ConsentStatus.GRANTED
    )
    consent_repo.save(consent_record)
    
    res = uc_identity.execute("req_001", actor="officer_demo", timestamp=1700000000.0)
    assert res == "Matched"


@patch("frappe.db.exists")
@patch("frappe.new_doc")
@patch("frappe.get_doc")
def test_frappe_consent_repository_save(mock_get_doc, mock_new_doc, mock_exists):
    """Verifies FrappeConsentRecordRepository maps domain state to Frappe document correctly."""
    mock_exists.return_value = False
    mock_doc = MagicMock()
    mock_new_doc.return_value = mock_doc
    
    repo = FrappeConsentRecordRepository()
    record = ConsentRecord(
        consent_record_id="CON-1",
        citizen_profile_id="CP-001",
        consent_purpose=ConsentPurpose.SERVICE_PROCESSING,
        consent_channel=ConsentChannel.PORTAL,
        consent_status=ConsentStatus.GRANTED,
        consent_timestamp=1700000000.0
    )
    
    repo.save(record)
    
    mock_exists.assert_called_once_with("NileGov Consent Record", "CON-1")
    mock_new_doc.assert_called_once_with("NileGov Consent Record")
    assert mock_doc.consent_record_id == "CON-1"
    assert mock_doc.citizen_profile == "CP-001"
    assert mock_doc.consent_purpose == ConsentPurpose.SERVICE_PROCESSING
    assert mock_doc.consent_channel == ConsentChannel.PORTAL
    assert mock_doc.consent_status == ConsentStatus.GRANTED
    mock_doc.save.assert_called_once()
