# Use Case: Create Payment Record
# Prototype simulation only. No live payment processed.

import time
from typing import Optional
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord, PaymentPurpose, PaymentChannel, PaymentStatus, PaymentVerificationStatus


class CreatePaymentRecord:
    """Application Service to initialize a simulated government payment record."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(
        self,
        payment_id: str,
        service_request_id: str,
        amount: float,
        purpose: str = PaymentPurpose.NATIONAL_ID_REPLACEMENT,
        channel: str = PaymentChannel.MOBILE_MONEY,
        citizen_profile_id: Optional[str] = None,
        consent_record_id: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> PaymentRecord:
        if not timestamp:
            timestamp = time.time()

        record = PaymentRecord(
            payment_record_id=payment_id,
            service_request_id=service_request_id,
            amount=amount,
            payment_purpose=purpose,
            payment_channel=channel,
            payment_status=PaymentStatus.PENDING,
            verification_status=PaymentVerificationStatus.NOT_CHECKED,
            citizen_profile_id=citizen_profile_id,
            consent_record_id=consent_record_id,
            created_at=timestamp
        )

        self.repository.save(record)
        return record
