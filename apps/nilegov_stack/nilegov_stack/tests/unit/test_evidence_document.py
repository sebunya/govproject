# Unit Tests for NileGov Evidence & Document Foundation
# Prototype simulation only. No live Government registry access.

import pytest
import time
from unittest.mock import MagicMock, patch
from nilegov_stack.domain.evidence import (
    EvidenceDocument,
    EvidenceDocumentType,
    EvidenceUploadChannel,
    EvidenceVerificationStatus
)
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.application.create_evidence_document import CreateEvidenceDocument
from nilegov_stack.application.verify_evidence_document import VerifyEvidenceDocument
from nilegov_stack.application.list_service_request_evidence import ListServiceRequestEvidence
from nilegov_stack.application.list_citizen_profile_evidence import ListCitizenProfileEvidence
from nilegov_stack.infrastructure.repositories.evidence_document_repository import InMemoryEvidenceDocumentRepository
from nilegov_stack.infrastructure.repositories.frappe_evidence_document_repository import FrappeEvidenceDocumentRepository


def test_evidence_document_domain_creation_success():
    """Verifies that an EvidenceDocument domain aggregate can be created with all fields."""
    doc = EvidenceDocument(
        evidence_document_id="EVI-001",
        citizen_profile_id="CP-001",
        service_request_id="req_001",
        document_type=EvidenceDocumentType.POLICE_LETTER,
        document_title="Ntinda Police Letter of Loss",
        file="demo-police-letter-placeholder.pdf",
        upload_channel=EvidenceUploadChannel.WEB_FORM,
        uploaded_by="Administrator",
        uploaded_at=1700000000.0,
        consent_record_id="CON-001",
        verification_status=EvidenceVerificationStatus.SUBMITTED,
        verified_by="officer_demo",
        verified_timestamp=1700000100.0,
        officer_notes="Placeholder verified successfully.",
        disclaimer="Prototype simulation only."
    )

    assert doc.evidence_document_id == "EVI-001"
    assert doc.citizen_profile_id == "CP-001"
    assert doc.service_request_id == "req_001"
    assert doc.document_type == EvidenceDocumentType.POLICE_LETTER
    assert doc.document_title == "Ntinda Police Letter of Loss"
    assert doc.file == "demo-police-letter-placeholder.pdf"
    assert doc.upload_channel == EvidenceUploadChannel.WEB_FORM
    assert doc.uploaded_by == "Administrator"
    assert doc.uploaded_at == 1700000000.0
    assert doc.consent_record_id == "CON-001"
    assert doc.verification_status == EvidenceVerificationStatus.SUBMITTED
    assert doc.verified_by == "officer_demo"
    assert doc.verified_timestamp == 1700000100.0
    assert doc.officer_notes == "Placeholder verified successfully."
    assert doc.disclaimer == "Prototype simulation only."


def test_evidence_document_verify_status_transition():
    """Verifies status transitions and metadata updates during verification."""
    doc = EvidenceDocument(
        evidence_document_id="EVI-001",
        citizen_profile_id="CP-001",
        service_request_id="req_001",
        document_type=EvidenceDocumentType.POLICE_LETTER,
        document_title="Ntinda Police Letter of Loss",
        file="demo-police-letter-placeholder.pdf",
        upload_channel=EvidenceUploadChannel.WEB_FORM,
        uploaded_by="Administrator",
        uploaded_at=1700000000.0
    )

    assert doc.verification_status == EvidenceVerificationStatus.SUBMITTED
    
    verify_time = 1700000200.0
    doc.verify(
        verified_by="officer_demo",
        timestamp=verify_time,
        status=EvidenceVerificationStatus.ACCEPTED,
        notes="All details match."
    )

    assert doc.verification_status == EvidenceVerificationStatus.ACCEPTED
    assert doc.verified_by == "officer_demo"
    assert doc.verified_timestamp == verify_time
    assert doc.officer_notes == "All details match."


def test_evidence_document_invalid_verification_status():
    """Verifies that invalid verification statuses are rejected."""
    doc = EvidenceDocument(
        evidence_document_id="EVI-001",
        citizen_profile_id="CP-001",
        service_request_id="req_001",
        document_type=EvidenceDocumentType.POLICE_LETTER,
        document_title="Ntinda Police Letter of Loss",
        file="demo-police-letter-placeholder.pdf",
        upload_channel=EvidenceUploadChannel.WEB_FORM,
        uploaded_by="Administrator",
        uploaded_at=1700000000.0
    )

    with pytest.raises(ValueError, match="Invalid verification status"):
        doc.verify("officer_demo", 1700000200.0, "INVALID_STATUS")


def test_evidence_document_add_officer_note():
    """Verifies that officer notes can be appended or added correctly."""
    doc = EvidenceDocument(
        evidence_document_id="EVI-001",
        citizen_profile_id="CP-001",
        service_request_id="req_001",
        document_type=EvidenceDocumentType.POLICE_LETTER,
        document_title="Ntinda Police Letter of Loss",
        file="demo-police-letter-placeholder.pdf",
        upload_channel=EvidenceUploadChannel.WEB_FORM,
        uploaded_by="Administrator",
        uploaded_at=1700000000.0
    )

    assert doc.officer_notes is None

    doc.add_officer_note("First note", 1700000200.0)
    assert doc.officer_notes == "First note"

    doc.add_officer_note("Second note", 1700000300.0)
    assert "First note" in doc.officer_notes
    assert "Second note" in doc.officer_notes
    assert "1700000300.0" in doc.officer_notes

    with pytest.raises(ValueError, match="Note content cannot be empty"):
        doc.add_officer_note("", 1700000400.0)


def test_evidence_use_cases_with_in_memory():
    """Verifies create, verify, and list use cases using InMemoryEvidenceDocumentRepository."""
    repo = InMemoryEvidenceDocumentRepository()

    # Create Use Case
    create_uc = CreateEvidenceDocument(repo)
    doc = create_uc.execute(
        evidence_document_id="EVI-1",
        citizen_profile_id="CP-1",
        service_request_id="req-1",
        document_type=EvidenceDocumentType.POLICE_LETTER,
        document_title="Ntinda Police Letter",
        file="demo-police-letter-placeholder.pdf",
        upload_channel=EvidenceUploadChannel.WEB_FORM,
        uploaded_by="Administrator",
        uploaded_at=1700000000.0
    )

    assert repo.get_by_id("EVI-1") == doc

    # Verify Use Case
    verify_uc = VerifyEvidenceDocument(repo)
    updated = verify_uc.execute(
        evidence_document_id="EVI-1",
        verified_by="officer_demo",
        timestamp=1700000500.0,
        status=EvidenceVerificationStatus.ACCEPTED,
        notes="Verified ok."
    )
    assert updated.verification_status == EvidenceVerificationStatus.ACCEPTED
    assert updated.verified_by == "officer_demo"

    # List Use Cases
    list_sr_uc = ListServiceRequestEvidence(repo)
    sr_list = list_sr_uc.execute("req-1")
    assert len(sr_list) == 1
    assert sr_list[0] == doc

    list_cp_uc = ListCitizenProfileEvidence(repo)
    cp_list = list_cp_uc.execute("CP-1")
    assert len(cp_list) == 1
    assert cp_list[0] == doc

    # Verify error on non-existent document
    with pytest.raises(ValueError, match="not found"):
        verify_uc.execute("EVI-NONEXISTENT", "officer_demo", 1700000500.0, EvidenceVerificationStatus.ACCEPTED)


@patch("frappe.db.exists")
@patch("frappe.new_doc")
@patch("frappe.get_doc")
def test_frappe_evidence_repository_save(mock_get_doc, mock_new_doc, mock_exists):
    """Verifies FrappeEvidenceDocumentRepository maps domain state to Frappe document correctly."""
    mock_exists.return_value = False
    mock_doc = MagicMock()
    mock_new_doc.return_value = mock_doc

    repo = FrappeEvidenceDocumentRepository()
    doc = EvidenceDocument(
        evidence_document_id="EVI-1",
        citizen_profile_id="CP-001",
        service_request_id="req_001",
        document_type=EvidenceDocumentType.POLICE_LETTER,
        document_title="Ntinda Police Letter",
        file="demo-police-letter-placeholder.pdf",
        upload_channel=EvidenceUploadChannel.WEB_FORM,
        uploaded_by="Administrator",
        uploaded_at=1700000000.0,
        consent_record_id="CON-1"
    )

    repo.save(doc)

    mock_exists.assert_called_once_with("NileGov Evidence Document", "EVI-1")
    mock_new_doc.assert_called_once_with("NileGov Evidence Document")
    
    assert mock_doc.evidence_document_id == "EVI-1"
    assert mock_doc.citizen_profile == "CP-001"
    assert mock_doc.service_request == "req_001"
    assert mock_doc.consent_record == "CON-1"
    assert mock_doc.document_type == EvidenceDocumentType.POLICE_LETTER
    assert mock_doc.document_title == "Ntinda Police Letter"
    assert mock_doc.file == "demo-police-letter-placeholder.pdf"
    
    mock_doc.save.assert_called_once()
