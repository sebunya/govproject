# In-memory Consent Record Repository
# Digi-Verse Uganda Limited

from typing import Dict, Optional, List
from nilegov_stack.application.ports import ConsentRecordRepository
from nilegov_stack.domain.consent import ConsentRecord


class InMemoryConsentRecordRepository(ConsentRecordRepository):
    """In-memory implementation of the ConsentRecordRepository port for testing."""

    def __init__(self):
        self._records: Dict[str, ConsentRecord] = {}

    def save(self, consent_record: ConsentRecord) -> None:
        self._records[consent_record.consent_record_id] = consent_record

    def get_by_id(self, consent_id: str) -> Optional[ConsentRecord]:
        return self._records.get(consent_id)

    def get_by_citizen_profile(self, profile_id: str) -> List[ConsentRecord]:
        results = []
        for record in self._records.values():
            if record.citizen_profile_id == profile_id:
                results.append(record)
        return results

    def get_by_service_request(self, request_id: str) -> List[ConsentRecord]:
        results = []
        for record in self._records.values():
            if record.service_request_id == request_id:
                results.append(record)
        return results
