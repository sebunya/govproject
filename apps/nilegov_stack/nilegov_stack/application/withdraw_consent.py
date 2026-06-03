# Use Case: Withdraw Consent
# Digi-Verse Uganda Limited

from nilegov_stack.domain.consent import ConsentRecord
from nilegov_stack.application.ports import ConsentRecordRepository


class WithdrawConsent:
    """Application Service to withdraw citizen consent."""

    def __init__(self, repository: ConsentRecordRepository):
        self.repository = repository

    def execute(self, consent_id: str, timestamp: float) -> ConsentRecord:
        record = self.repository.get_by_id(consent_id)
        if not record:
            raise ValueError(f"Consent record not found: {consent_id}")
            
        record.withdraw(timestamp)
        self.repository.save(record)
        return record
