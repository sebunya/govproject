# Use Case: List Consent Records by Citizen Profile
# Digi-Verse Uganda Limited

from typing import List
from nilegov_stack.domain.consent import ConsentRecord
from nilegov_stack.application.ports import ConsentRecordRepository


class ListCitizenConsentRecords:
    """Application Service to list all consent records linked to a citizen profile."""

    def __init__(self, repository: ConsentRecordRepository):
        self.repository = repository

    def execute(self, profile_id: str) -> List[ConsentRecord]:
        return self.repository.get_by_citizen_profile(profile_id)
