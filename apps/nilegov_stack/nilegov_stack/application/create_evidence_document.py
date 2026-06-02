# Use Case: Create Evidence Document
# Prototype simulation only. No live Government registry access.

from typing import Optional
from nilegov_stack.domain.evidence import EvidenceDocument, EvidenceVerificationStatus
from nilegov_stack.application.ports import EvidenceDocumentRepository


class CreateEvidenceDocument:
    """Application Service to create and register an evidence document."""

    def __init__(self, repository: EvidenceDocumentRepository):
        self.repository = repository

    def execute(
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
        disclaimer: Optional[str] = None,
        created_at: Optional[float] = None
    ) -> EvidenceDocument:
        kwargs = {
            "evidence_document_id": evidence_document_id,
            "citizen_profile_id": citizen_profile_id,
            "service_request_id": service_request_id,
            "document_type": document_type,
            "document_title": document_title,
            "file": file,
            "upload_channel": upload_channel,
            "uploaded_by": uploaded_by,
            "uploaded_at": uploaded_at,
            "consent_record_id": consent_record_id,
            "verification_status": verification_status,
            "verified_by": verified_by,
            "verified_timestamp": verified_timestamp,
            "officer_notes": officer_notes,
            "created_at": created_at,
            "updated_at": created_at
        }
        if disclaimer is not None:
            kwargs["disclaimer"] = disclaimer

        doc = EvidenceDocument(**kwargs)
        self.repository.save(doc)
        return doc
