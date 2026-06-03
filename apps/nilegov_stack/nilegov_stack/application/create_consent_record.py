# Use Case: Create Consent Record
# Digi-Verse Uganda Limited

from typing import Optional
from nilegov_stack.domain.consent import ConsentRecord, ConsentStatus
from nilegov_stack.application.ports import ConsentRecordRepository


class CreateConsentRecord:
    """Application Service to create and record citizen consent."""

    def __init__(self, repository: ConsentRecordRepository):
        self.repository = repository

    def execute(
        self,
        consent_record_id: str,
        citizen_profile_id: str,
        consent_purpose: str,
        consent_channel: str,
        consent_status: str = ConsentStatus.GRANTED,
        consent_timestamp: Optional[float] = None,
        service_request_id: Optional[str] = None,
        expiry_time: Optional[float] = None,
        recorded_by: Optional[str] = None,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        created_at: Optional[float] = None
    ) -> ConsentRecord:
        record = ConsentRecord(
            consent_record_id=consent_record_id,
            citizen_profile_id=citizen_profile_id,
            consent_purpose=consent_purpose,
            consent_channel=consent_channel,
            consent_status=consent_status,
            consent_timestamp=consent_timestamp,
            service_request_id=service_request_id,
            expiry_time=expiry_time,
            recorded_by=recorded_by,
            notes=notes,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=created_at,
            updated_at=created_at
        )
        self.repository.save(record)
        return record
