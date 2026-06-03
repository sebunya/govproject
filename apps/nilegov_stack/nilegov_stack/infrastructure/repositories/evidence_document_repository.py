# In-memory Evidence Document Repository
# Prototype simulation only. No live Government registry access.

from typing import Dict, Optional, List
from nilegov_stack.application.ports import EvidenceDocumentRepository
from nilegov_stack.domain.evidence import EvidenceDocument


class InMemoryEvidenceDocumentRepository(EvidenceDocumentRepository):
    """In-memory implementation of the EvidenceDocumentRepository port for testing."""

    def __init__(self):
        self._records: Dict[str, EvidenceDocument] = {}

    def save(self, evidence_document: EvidenceDocument) -> None:
        self._records[evidence_document.evidence_document_id] = evidence_document

    def get_by_id(self, evidence_id: str) -> Optional[EvidenceDocument]:
        return self._records.get(evidence_id)

    def get_by_citizen_profile(self, profile_id: str) -> List[EvidenceDocument]:
        results = []
        for record in self._records.values():
            if record.citizen_profile_id == profile_id:
                results.append(record)
        return results

    def get_by_service_request(self, request_id: str) -> List[EvidenceDocument]:
        results = []
        for record in self._records.values():
            if record.service_request_id == request_id:
                results.append(record)
        return results
