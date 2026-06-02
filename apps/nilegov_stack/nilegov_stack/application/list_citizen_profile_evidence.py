# Use Case: List Citizen Profile Evidence
# Prototype simulation only. No live Government registry access.

from typing import List
from nilegov_stack.domain.evidence import EvidenceDocument
from nilegov_stack.application.ports import EvidenceDocumentRepository


class ListCitizenProfileEvidence:
    """Application Service to list all evidence documents associated with a Citizen Profile."""

    def __init__(self, repository: EvidenceDocumentRepository):
        self.repository = repository

    def execute(self, citizen_profile_id: str) -> List[EvidenceDocument]:
        return self.repository.get_by_citizen_profile(citizen_profile_id)
