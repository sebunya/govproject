# Evidence Document Entity for NileGov Stack
# Prototype simulation only. No live Government registry access.

import time
from typing import Optional

class EvidenceDocumentType:
    POLICE_LETTER = "Police Letter Placeholder"
    AFFIDAVIT = "Affidavit Placeholder"
    SUPPORTING_ID = "Supporting ID Placeholder"
    PAYMENT_RECEIPT = "Payment Receipt Placeholder"
    APPLICATION_FORM = "Application Form Placeholder"
    OTHER = "Other Supporting Document"

class EvidenceUploadChannel:
    WEB_FORM = "Web Form"
    OFFICER_ASSISTED = "Officer Assisted"
    PORTAL = "Portal"
    EMAIL = "Email"
    WHATSAPP = "WhatsApp"
    OTHER = "Other"

class EvidenceVerificationStatus:
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    REQUIRES_REPLACEMENT = "Requires Replacement"
    NOT_REQUIRED = "Not Required"
    DEMO_PLACEHOLDER = "Demo Placeholder"

class EvidenceDocument:
    """Represents a validated attachment (evidence) associated with a Service Request."""
    def __init__(
        self,
        evidence_document_id: str,
        citizen_profile_id: str,
        service_request_id: str,
        document_type: str,
        document_title: str,
        file: str,
        upload_channel: str,
        uploaded_by: str,
        uploaded_at: float,
        consent_record_id: Optional[str] = None,
        verification_status: str = EvidenceVerificationStatus.SUBMITTED,
        verified_by: Optional[str] = None,
        verified_timestamp: Optional[float] = None,
        officer_notes: Optional[str] = None,
        disclaimer: str = "Prototype simulation only. No live Government registry access.",
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ):
        self.evidence_document_id = evidence_document_id
        self.citizen_profile_id = citizen_profile_id
        self.service_request_id = service_request_id
        self.document_type = document_type
        self.document_title = document_title
        self.file = file
        self.upload_channel = upload_channel
        self.uploaded_by = uploaded_by
        self.uploaded_at = uploaded_at
        self.consent_record_id = consent_record_id
        self.verification_status = verification_status
        self.verified_by = verified_by
        self.verified_timestamp = verified_timestamp
        self.officer_notes = officer_notes
        self.disclaimer = disclaimer
        
        now = time.time()
        self.created_at = created_at if created_at is not None else now
        self.updated_at = updated_at if updated_at is not None else now

    def verify(self, verified_by: str, timestamp: float, status: str, notes: Optional[str] = None) -> None:
        """Updates the verification status and records verification metadata."""
        valid_statuses = {
            EvidenceVerificationStatus.SUBMITTED,
            EvidenceVerificationStatus.UNDER_REVIEW,
            EvidenceVerificationStatus.ACCEPTED,
            EvidenceVerificationStatus.REJECTED,
            EvidenceVerificationStatus.REQUIRES_REPLACEMENT,
            EvidenceVerificationStatus.NOT_REQUIRED,
            EvidenceVerificationStatus.DEMO_PLACEHOLDER
        }
        if status not in valid_statuses:
            raise ValueError(f"Invalid verification status: {status}")

        self.verification_status = status
        self.verified_by = verified_by
        self.verified_timestamp = timestamp
        if notes is not None:
            self.officer_notes = notes
        self.updated_at = timestamp

    def add_officer_note(self, note: str, timestamp: float) -> None:
        """Appends or updates officer notes on the evidence document."""
        if not note:
            raise ValueError("Note content cannot be empty.")
        if self.officer_notes:
            self.officer_notes += f"\n[{timestamp}] {note}"
        else:
            self.officer_notes = note
        self.updated_at = timestamp
