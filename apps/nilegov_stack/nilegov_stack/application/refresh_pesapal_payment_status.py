# Use case: Refresh Pesapal Payment Status
# Digi-Verse Uganda Limited

import time
from typing import Optional
from nilegov_stack.application.ports import PaymentRecordRepository, ServiceRequestRepository, ConsentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord, PaymentStatus, PaymentVerificationStatus
from nilegov_stack.domain.service_request import WorkflowStatus
from nilegov_stack.domain.consent import ConsentPurpose, ConsentStatus
from nilegov_stack.infrastructure.integrations.pesapal_api_client import PesapalApiClient


class RefreshPesapalPaymentStatus:
    """Application Service to request payment status from Pesapal API 3.0 and synchronize records."""

    def __init__(
        self,
        payment_repo: PaymentRecordRepository,
        api_client: PesapalApiClient,
        service_repo: Optional[ServiceRequestRepository] = None,
        consent_repo: Optional[ConsentRecordRepository] = None
    ):
        self.payment_repo = payment_repo
        self.api_client = api_client
        self.service_repo = service_repo
        self.consent_repo = consent_repo

    def execute(self, payment_id: str, verified_by: str = "system", timestamp: Optional[float] = None) -> str:
        record = self.payment_repo.get_by_id(payment_id)
        if not record:
            raise ValueError(f"Payment Record {payment_id} not found.")

        if not record.provider_order_tracking_id:
            raise ValueError(f"Payment Record {payment_id} lacks provider_order_tracking_id.")

        curr_time = timestamp or time.time()

        # 1. Fetch from Pesapal API
        auth_token = self.api_client.request_token()
        status_res = self.api_client.get_transaction_status(auth_token.token, record.provider_order_tracking_id)

        # 2. Evaluate consent
        consent_granted = True
        consent_record_id = None
        consent_status_str = "Missing"

        if self.consent_repo and record.citizen_profile_id:
            from nilegov_stack.application.check_active_consent import CheckActiveConsent
            checker = CheckActiveConsent(self.consent_repo)
            consent_granted = checker.execute(
                profile_id=record.citizen_profile_id,
                purpose=ConsentPurpose.PAYMENT_VERIFICATION,
                current_time=curr_time
            )

            consents = self.consent_repo.get_by_citizen_profile(record.citizen_profile_id)
            matching_consent = None
            for c in consents:
                if c.consent_purpose == ConsentPurpose.PAYMENT_VERIFICATION:
                    matching_consent = c
                    break

            if matching_consent:
                consent_record_id = matching_consent.consent_record_id
                consent_status_str = matching_consent.consent_status
                if matching_consent.consent_status in (ConsentStatus.WITHDRAWN, ConsentStatus.EXPIRED):
                    consent_granted = False

        record.consent_record_id = consent_record_id

        # 3. Map status and apply rules
        self.api_client.map_transaction_status_to_payment_record(
            payment_record=record,
            status_result=status_res,
            timestamp=curr_time,
            checker_name=verified_by
        )

        # 4. Consent override if status COMPLETED (code 1) but consent was withdrawn/missing
        if status_res.status_code == 1 and not consent_granted:
            record.flag_for_review(curr_time)
            if consent_status_str in (ConsentStatus.WITHDRAWN, ConsentStatus.EXPIRED):
                record.failure_reason = f"Consent {consent_status_str.lower()}."
            else:
                record.failure_reason = "Consent missing."

        # Save payment record updates
        self.payment_repo.save(record)

        # 5. Synchronize with Service Request
        if self.service_repo:
            req = self.service_repo.get_by_id(record.service_request_id)
            if req:
                mapped_status = "Pending"
                if record.payment_status == PaymentStatus.VERIFIED:
                    mapped_status = "Verified"
                elif record.payment_status == PaymentStatus.FAILED:
                    mapped_status = "Failed"
                elif record.payment_status == PaymentStatus.CANCELLED:
                    mapped_status = "Not Required"

                req.update_payment_status(mapped_status, record.amount, curr_time)

                if record.payment_status == PaymentStatus.VERIFIED:
                    req.update_status(WorkflowStatus.PAYMENT_VERIFIED, verified_by, curr_time)

                self.service_repo.save(req)

        return record.payment_status
