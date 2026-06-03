# Use Case: List Consent Records by Service Request
# Digi-Verse Uganda Limited

from typing import List
from nilegov_stack.domain.consent import ConsentRecord
from nilegov_stack.application.ports import ConsentRecordRepository


class ListRequestConsentRecords:
    """Application Service to list all consent records linked to a service request."""

    def __init__(self, repository: ConsentRecordRepository):
        self.repository = repository

    def execute(self, request_id: str) -> List[ConsentRecord]:
        return self.repository.get_by_service_request(request_id)
