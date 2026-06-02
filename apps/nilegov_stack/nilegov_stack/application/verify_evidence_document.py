# Use Case: Verify Evidence Document
# Prototype simulation only. No live Government registry access.

from typing import Optional
from nilegov_stack.domain.evidence import EvidenceDocument
from nilegov_stack.application.ports import EvidenceDocumentRepository


class VerifyEvidenceDocument:
    """Application Service to update the verification status of an evidence document."""

    def __init__(self, repository: EvidenceDocumentRepository):
        self.repository = repository

    def execute(
        self,
        evidence_document_id: str,
        verified_by: str,
        timestamp: float,
        status: str,
        notes: Optional[str] = None
    ) -> EvidenceDocument:
        doc = self.repository.get_by_id(evidence_document_id)
        if not doc:
            raise ValueError(f"Evidence document with ID {evidence_document_id} not found.")

        doc.verify(
            verified_by=verified_by,
            timestamp=timestamp,
            status=status,
            notes=notes
        )
        self.repository.save(doc)
        return doc
