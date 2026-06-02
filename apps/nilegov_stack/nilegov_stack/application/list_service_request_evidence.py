# Use Case: List Service Request Evidence
# Prototype simulation only. No live Government registry access.

from typing import List
from nilegov_stack.domain.evidence import EvidenceDocument
from nilegov_stack.application.ports import EvidenceDocumentRepository


class ListServiceRequestEvidence:
    """Application Service to list all evidence documents associated with a Service Request."""

    def __init__(self, repository: EvidenceDocumentRepository):
        self.repository = repository

    def execute(self, service_request_id: str) -> List[EvidenceDocument]:
        return self.repository.get_by_service_request(service_request_id)
