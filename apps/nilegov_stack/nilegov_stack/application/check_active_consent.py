# Use Case: Check Active Consent
# Digi-Verse Uganda Limited

from nilegov_stack.application.ports import ConsentRecordRepository


class CheckActiveConsent:
    """Application Service to check if a citizen has active granted consent for a specific purpose."""

    def __init__(self, repository: ConsentRecordRepository):
        self.repository = repository

    def execute(self, profile_id: str, purpose: str, current_time: float) -> bool:
        records = self.repository.get_by_citizen_profile(profile_id)
        for record in records:
            if record.consent_purpose == purpose and record.is_active(current_time):
                return True
        return False
