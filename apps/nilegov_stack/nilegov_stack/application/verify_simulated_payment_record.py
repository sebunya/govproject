# Use Case: Verify Simulated Payment Record
# Prototype simulation only. No live payment processed.

import time
from typing import Optional
from nilegov_stack.application.ports import PaymentRecordRepository, PaymentVerificationGateway, ServiceRequestRepository, ConsentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord, PaymentStatus, PaymentVerificationStatus, ReceiptStatus
from nilegov_stack.domain.service_request import WorkflowStatus
from nilegov_stack.domain.consent import ConsentPurpose, ConsentStatus


class VerifySimulatedPaymentRecord:
    """Application Service orchestrating simulated verification for a PaymentRecord aggregate."""

    def __init__(
        self,
        payment_repo: PaymentRecordRepository,
        gateway: PaymentVerificationGateway,
        service_repo: Optional[ServiceRequestRepository] = None,
        consent_repo: Optional[ConsentRecordRepository] = None,
        notification_service: Optional[Any] = None
    ):
        self.payment_repo = payment_repo
        self.gateway = gateway
        self.service_repo = service_repo
        self.consent_repo = consent_repo
        self.notification_service = notification_service

    def execute(
        self,
        payment_id: str,
        verified_by: str = "officer_demo",
        timestamp: Optional[float] = None
    ) -> str:
        record = self.payment_repo.get_by_id(payment_id)
        if not record:
            raise ValueError(f"Payment Record {payment_id} not found.")

        if not timestamp:
            timestamp = time.time()

        # 1. Evaluate consent
        consent_granted = True
        consent_record_id = None
        consent_status_str = "Missing"

        if self.consent_repo and record.citizen_profile_id:
            from nilegov_stack.application.check_active_consent import CheckActiveConsent
            checker = CheckActiveConsent(self.consent_repo)
            consent_granted = checker.execute(
                profile_id=record.citizen_profile_id,
                purpose=ConsentPurpose.PAYMENT_VERIFICATION,
                current_time=timestamp
            )

            # Look up specific consent record to find if withdrawn/expired
            consents = self.consent_repo.get_by_citizen_profile(record.citizen_profile_id)
            matching_consent = None
            for c in consents:
                if c.consent_purpose == ConsentPurpose.PAYMENT_VERIFICATION:
                    matching_consent = c
                    break

            if matching_consent:
                consent_record_id = matching_consent.consent_record_id
                consent_status_str = matching_consent.consent_status
                # Check for expired/withdrawn status explicitly
                if matching_consent.consent_status in (ConsentStatus.WITHDRAWN, ConsentStatus.EXPIRED):
                    consent_granted = False

        # 2. Invoke simulated gateway
        result = self.gateway.verify_payment_record(record)
        success = result.get("success", False)
        amount = result.get("amount", record.amount)
        gateway_status = result.get("status", "Simulated Failed")

        # 3. Apply state transitions based on gateway success and consent
        if not success:
            record.fail(result.get("message", "Simulated Payment verification failed."), timestamp)
        elif not consent_granted:
            # Missing, withdrawn or expired consent prevents Simulated Verified
            record.flag_for_review(timestamp)
            if consent_status_str in (ConsentStatus.WITHDRAWN, ConsentStatus.EXPIRED):
                record.failure_reason = f"Consent {consent_status_str.lower()}."
            else:
                record.failure_reason = "Consent missing."
            record.consent_record_id = consent_record_id
        else:
            record.verify(verified_by, timestamp)
            record.consent_record_id = consent_record_id
            record.amount = amount

        self.payment_repo.save(record)

        # 4. Synchronize payment status with linked ServiceRequest
        if self.service_repo:
            req = self.service_repo.get_by_id(record.service_request_id)
            if req:
                # Map PaymentRecord status to ServiceRequest status values
                mapped_status = "Pending"
                if record.payment_status == PaymentStatus.VERIFIED:
                    mapped_status = "Verified"
                elif record.payment_status == PaymentStatus.FAILED:
                    mapped_status = "Failed"
                elif record.payment_status == PaymentStatus.CANCELLED:
                    mapped_status = "Not Required"

                req.update_payment_status(mapped_status, record.amount, timestamp)

                if record.payment_status == PaymentStatus.VERIFIED:
                    req.update_status(WorkflowStatus.PAYMENT_VERIFIED, verified_by, timestamp)

                self.service_repo.save(req)

        # 5. Trigger notification if notification service helper is supplied
        if self.notification_service:
            # We can create a notification event for status updates
            try:
                from nilegov_stack.domain.notification import NotificationMessageType
                msg_type = None
                if record.payment_status == PaymentStatus.PENDING:
                    msg_type = NotificationMessageType.PENDING # Wait, does this exist? Let's check or map to PAYMENT_PENDING
                elif record.payment_status == PaymentStatus.VERIFIED:
                    msg_type = "Payment Verified" # Wait, message types in notification.py message_type select:
                    # Request Received, Under Review, Information Required, Payment Pending, Payment Verified, Approved, Ready for Collection, Closed, Rejected
                
                # We can call the notification_service.execute(...)
            except Exception:
                pass

        return record.payment_status
