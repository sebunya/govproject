# NileGov Payments Domain Aggregate & Constants
# Digi-Verse Uganda Limited

import time
from typing import Optional, List, Dict, Any


class PaymentPurpose:
    NATIONAL_ID_REPLACEMENT = "National ID Replacement Fee"
    SERVICE_PROCESSING = "Service Processing Fee"
    DOCUMENT_REPLACEMENT = "Document Replacement Fee"
    OTHER_GOVERNMENT_SERVICE = "Other Government Service Fee"
    NOT_APPLICABLE = "Not Applicable"

    ALL_PURPOSES = (
        NATIONAL_ID_REPLACEMENT,
        SERVICE_PROCESSING,
        DOCUMENT_REPLACEMENT,
        OTHER_GOVERNMENT_SERVICE,
        NOT_APPLICABLE
    )


class PaymentChannel:
    MOBILE_MONEY = "Simulated Mobile Money"
    CARD = "Simulated Card"
    BANK = "Simulated Bank"
    CASH_OFFICE = "Simulated Cash Office"
    NOT_APPLICABLE = "Not Applicable"

    ALL_CHANNELS = (
        MOBILE_MONEY,
        CARD,
        BANK,
        CASH_OFFICE,
        NOT_APPLICABLE
    )


class PaymentStatus:
    NOT_REQUIRED = "Not Required"
    PENDING = "Pending"
    SUBMITTED = "Submitted"
    VERIFIED = "Verified"
    FAILED = "Failed"
    REVERSED = "Reversed"
    CANCELLED = "Cancelled"

    ALL_STATUSES = (
        NOT_REQUIRED,
        PENDING,
        SUBMITTED,
        VERIFIED,
        FAILED,
        REVERSED,
        CANCELLED
    )


class PaymentVerificationStatus:
    NOT_CHECKED = "Not Checked"
    PENDING_VERIFICATION = "Pending Verification"
    SIMULATED_VERIFIED = "Simulated Verified"
    SIMULATED_FAILED = "Simulated Failed"
    REQUIRES_REVIEW = "Requires Review"
    NOT_APPLICABLE = "Not Applicable"

    ALL_STATUSES = (
        NOT_CHECKED,
        PENDING_VERIFICATION,
        SIMULATED_VERIFIED,
        SIMULATED_FAILED,
        REQUIRES_REVIEW,
        NOT_APPLICABLE
    )


class ReceiptStatus:
    NOT_REQUIRED = "Not Required"
    RECEIPT_PENDING = "Receipt Pending"
    RECEIPT_READY = "Receipt Ready"
    SIMULATED_RECEIPT_GENERATED = "Simulated Receipt Generated"
    CANCELLED = "Cancelled"

    ALL_STATUSES = (
        NOT_REQUIRED,
        RECEIPT_PENDING,
        RECEIPT_READY,
        SIMULATED_RECEIPT_GENERATED,
        CANCELLED
    )


class ReconciliationStatus:
    NOT_REQUIRED = "Not Required"
    PENDING_RECONCILIATION = "Pending Reconciliation"
    RECONCILED = "Reconciled"
    MISMATCH = "Mismatch"
    REQUIRES_REVIEW = "Requires Review"

    ALL_STATUSES = (
        NOT_REQUIRED,
        PENDING_RECONCILIATION,
        RECONCILED,
        MISMATCH,
        REQUIRES_REVIEW
    )


class PaymentProvider:
    SIMULATED = "Simulated"
    PESAPAL_SANDBOX = "Pesapal Sandbox"
    PESAPAL_LIVE = "Pesapal Live"

    ALL_PROVIDERS = (
        SIMULATED,
        PESAPAL_SANDBOX,
        PESAPAL_LIVE
    )


class PaymentRecord:
    """Domain aggregate representing a simulated government payment record."""

    DISCLAIMER = "Prototype simulation only. No live payment was processed."

    def __init__(
        self,
        payment_record_id: str,
        service_request_id: str,
        amount: float,
        payment_purpose: str = PaymentPurpose.NATIONAL_ID_REPLACEMENT,
        payment_channel: str = PaymentChannel.MOBILE_MONEY,
        payment_status: str = PaymentStatus.PENDING,
        simulated_transaction_reference: str = "",
        verification_status: str = PaymentVerificationStatus.NOT_CHECKED,
        citizen_profile_id: Optional[str] = None,
        consent_record_id: Optional[str] = None,
        currency: str = "UGX",
        receipt_status: str = ReceiptStatus.RECEIPT_PENDING,
        reconciliation_status: str = ReconciliationStatus.PENDING_RECONCILIATION,
        verification_timestamp: Optional[float] = None,
        verified_by: Optional[str] = None,
        receipt_reference: Optional[str] = None,
        failure_reason: Optional[str] = None,
        triggered_by_event: Optional[str] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        provider: str = PaymentProvider.SIMULATED,
        provider_mode: Optional[str] = None,
        provider_order_tracking_id: Optional[str] = None,
        provider_merchant_reference: Optional[str] = None,
        provider_redirect_url: Optional[str] = None,
        provider_payment_method: Optional[str] = None,
        provider_confirmation_code: Optional[str] = None,
        provider_status_code: Optional[str] = None,
        provider_status_description: Optional[str] = None,
        provider_status_checked_at: Optional[float] = None,
        provider_ipn_id: Optional[str] = None,
        provider_callback_received_at: Optional[float] = None,
        provider_ipn_received_at: Optional[float] = None,
        provider_masked_account: Optional[str] = None
    ):
        self.payment_record_id = payment_record_id
        
        if not service_request_id:
            raise ValueError("Service Request ID is required.")
        self.service_request_id = service_request_id
        
        if amount < 0.0:
            raise ValueError("Amount cannot be negative.")
        self.amount = amount
        
        if payment_purpose not in PaymentPurpose.ALL_PURPOSES:
            raise ValueError(f"Invalid payment purpose: {payment_purpose}")
        self.payment_purpose = payment_purpose

        if payment_channel not in PaymentChannel.ALL_CHANNELS:
            raise ValueError(f"Invalid payment channel: {payment_channel}")
        self.payment_channel = payment_channel

        if payment_status not in PaymentStatus.ALL_STATUSES:
            raise ValueError(f"Invalid payment status: {payment_status}")
        self.payment_status = payment_status

        self.simulated_transaction_reference = simulated_transaction_reference

        if verification_status not in PaymentVerificationStatus.ALL_STATUSES:
            raise ValueError(f"Invalid verification status: {verification_status}")
        self.verification_status = verification_status

        self.citizen_profile_id = citizen_profile_id
        self.consent_record_id = consent_record_id
        self.currency = currency

        if receipt_status not in ReceiptStatus.ALL_STATUSES:
            raise ValueError(f"Invalid receipt status: {receipt_status}")
        self.receipt_status = receipt_status

        if reconciliation_status not in ReconciliationStatus.ALL_STATUSES:
            raise ValueError(f"Invalid reconciliation status: {reconciliation_status}")
        self.reconciliation_status = reconciliation_status

        if provider not in PaymentProvider.ALL_PROVIDERS:
            raise ValueError(f"Invalid provider: {provider}")
        self.provider = provider

        self.provider_mode = provider_mode
        self.provider_order_tracking_id = provider_order_tracking_id
        self.provider_merchant_reference = provider_merchant_reference
        self.provider_redirect_url = provider_redirect_url
        self.provider_payment_method = provider_payment_method
        self.provider_confirmation_code = provider_confirmation_code
        self.provider_status_code = provider_status_code
        self.provider_status_description = provider_status_description
        self.provider_status_checked_at = provider_status_checked_at
        self.provider_ipn_id = provider_ipn_id
        self.provider_callback_received_at = provider_callback_received_at
        self.provider_ipn_received_at = provider_ipn_received_at
        self.provider_masked_account = provider_masked_account

        self.verification_timestamp = verification_timestamp
        self.verified_by = verified_by
        self.receipt_reference = receipt_reference
        self.failure_reason = failure_reason
        self.triggered_by_event = triggered_by_event
        self.disclaimer = self.DISCLAIMER
        self.created_at = created_at or time.time()
        self.updated_at = updated_at or self.created_at

    def submit(self, reference: str, timestamp: float):
        """Transitions payment from Pending to Submitted."""
        if self.payment_status != PaymentStatus.PENDING:
            raise ValueError(f"Cannot submit a payment in state: {self.payment_status}")
        if not reference:
            raise ValueError("Transaction reference is required for submission.")
        self.payment_status = PaymentStatus.SUBMITTED
        self.simulated_transaction_reference = reference
        self.verification_status = PaymentVerificationStatus.PENDING_VERIFICATION
        self.updated_at = timestamp

    def verify(self, verified_by: str, timestamp: float):
        """Transitions payment to Verified status."""
        if self.payment_status not in (PaymentStatus.SUBMITTED, PaymentStatus.PENDING):
            raise ValueError(f"Cannot verify a payment in state: {self.payment_status}")
        self.payment_status = PaymentStatus.VERIFIED
        self.verification_status = PaymentVerificationStatus.SIMULATED_VERIFIED
        self.verification_timestamp = timestamp
        self.verified_by = verified_by
        self.receipt_status = ReceiptStatus.RECEIPT_READY
        self.reconciliation_status = ReconciliationStatus.PENDING_RECONCILIATION
        self.updated_at = timestamp

    def fail(self, reason: str, timestamp: float):
        """Transitions payment to Failed status."""
        self.payment_status = PaymentStatus.FAILED
        self.verification_status = PaymentVerificationStatus.SIMULATED_FAILED
        self.failure_reason = reason
        self.updated_at = timestamp

    def flag_for_review(self, timestamp: float):
        """Flags verification as requiring review."""
        self.verification_status = PaymentVerificationStatus.REQUIRES_REVIEW
        self.reconciliation_status = ReconciliationStatus.REQUIRES_REVIEW
        self.updated_at = timestamp

    def reverse(self, timestamp: float):
        """Reverses a verified payment."""
        if self.payment_status != PaymentStatus.VERIFIED:
            raise ValueError("Only verified payments can be reversed.")
        self.payment_status = PaymentStatus.REVERSED
        self.reconciliation_status = ReconciliationStatus.REQUIRES_REVIEW
        self.updated_at = timestamp

    def cancel(self, timestamp: float):
        """Cancels a pending payment."""
        if self.payment_status in (PaymentStatus.VERIFIED, PaymentStatus.REVERSED):
            raise ValueError("Cannot cancel a completed/reversed payment.")
        self.payment_status = PaymentStatus.CANCELLED
        self.receipt_status = ReceiptStatus.CANCELLED
        self.updated_at = timestamp

    def mark_receipt_ready(self, timestamp: float):
        """Marks receipt status as ready."""
        self.receipt_status = ReceiptStatus.RECEIPT_READY
        self.updated_at = timestamp

    def generate_receipt(self, receipt_ref: str, timestamp: float):
        """Simulates receipt generation."""
        if not receipt_ref:
            raise ValueError("Receipt reference is required.")
        self.receipt_status = ReceiptStatus.SIMULATED_RECEIPT_GENERATED
        self.receipt_reference = receipt_ref
        self.updated_at = timestamp

    def reconcile(self, status: str, timestamp: float):
        """Performs reconciliation update."""
        if status not in ReconciliationStatus.ALL_STATUSES:
            raise ValueError(f"Invalid reconciliation status: {status}")
        self.reconciliation_status = status
        self.updated_at = timestamp
