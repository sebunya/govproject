# Frappe-based Payment Record Repository
# Prototype simulation only. No live payment processed.

try:
    import frappe
except ImportError:
    frappe = None

from typing import Optional, List
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord


class FrappePaymentRecordRepository(PaymentRecordRepository):
    """Frappe-based repository for persisting and loading Payment Record aggregates."""

    def _check_frappe(self):
        if not frappe:
            raise ImportError("Frappe framework is not loaded in this environment.")

    def save(self, payment_record: PaymentRecord) -> None:
        self._check_frappe()

        # Load or create document
        if frappe.db.exists("NileGov Payment Record", payment_record.payment_record_id):
            doc = frappe.get_doc("NileGov Payment Record", payment_record.payment_record_id)
        else:
            doc = frappe.new_doc("NileGov Payment Record")
            doc.payment_record_id = payment_record.payment_record_id

        doc.service_request = payment_record.service_request_id
        doc.citizen_profile = payment_record.citizen_profile_id
        doc.consent_record = payment_record.consent_record_id
        doc.amount = payment_record.amount
        doc.currency = payment_record.currency
        doc.payment_purpose = payment_record.payment_purpose
        doc.payment_channel = payment_record.payment_channel
        doc.payment_status = payment_record.payment_status
        doc.simulated_transaction_reference = payment_record.simulated_transaction_reference
        doc.verification_status = payment_record.verification_status
        
        if payment_record.verification_timestamp:
            doc.verification_timestamp = frappe.utils.get_datetime(payment_record.verification_timestamp)
        else:
            doc.verification_timestamp = None

        doc.verified_by = payment_record.verified_by
        doc.receipt_status = payment_record.receipt_status
        doc.receipt_reference = payment_record.receipt_reference
        doc.reconciliation_status = payment_record.reconciliation_status
        doc.failure_reason = payment_record.failure_reason
        doc.triggered_by_event = payment_record.triggered_by_event
        doc.disclaimer = payment_record.disclaimer

        doc.provider = payment_record.provider
        doc.provider_mode = payment_record.provider_mode
        doc.provider_order_tracking_id = payment_record.provider_order_tracking_id
        doc.provider_merchant_reference = payment_record.provider_merchant_reference
        doc.provider_redirect_url = payment_record.provider_redirect_url
        doc.provider_payment_method = payment_record.provider_payment_method
        doc.provider_confirmation_code = payment_record.provider_confirmation_code
        doc.provider_status_code = payment_record.provider_status_code
        doc.provider_status_description = payment_record.provider_status_description

        if payment_record.provider_status_checked_at:
            doc.provider_status_checked_at = frappe.utils.get_datetime(payment_record.provider_status_checked_at)
        else:
            doc.provider_status_checked_at = None

        doc.provider_ipn_id = payment_record.provider_ipn_id

        if payment_record.provider_callback_received_at:
            doc.provider_callback_received_at = frappe.utils.get_datetime(payment_record.provider_callback_received_at)
        else:
            doc.provider_callback_received_at = None

        if payment_record.provider_ipn_received_at:
            doc.provider_ipn_received_at = frappe.utils.get_datetime(payment_record.provider_ipn_received_at)
        else:
            doc.provider_ipn_received_at = None

        doc.provider_masked_account = payment_record.provider_masked_account

        doc.save(ignore_permissions=True)
        frappe.db.commit()

    def get_by_id(self, payment_id: str) -> Optional[PaymentRecord]:
        self._check_frappe()
        if not frappe.db.exists("NileGov Payment Record", payment_id):
            return None

        doc = frappe.get_doc("NileGov Payment Record", payment_id)
        return self._map_doc_to_aggregate(doc)

    def get_by_service_request(self, request_id: str) -> List[PaymentRecord]:
        self._check_frappe()
        records = frappe.get_all(
            "NileGov Payment Record",
            filters={"service_request": request_id},
            pluck="name"
        )
        results = []
        for rid in records:
            p = self.get_by_id(rid)
            if p:
                results.append(p)
        return results

    def get_by_citizen_profile(self, profile_id: str) -> List[PaymentRecord]:
        self._check_frappe()
        records = frappe.get_all(
            "NileGov Payment Record",
            filters={"citizen_profile": profile_id},
            pluck="name"
        )
        results = []
        for rid in records:
            p = self.get_by_id(rid)
            if p:
                results.append(p)
        return results

    def get_by_status(self, status: str) -> List[PaymentRecord]:
        self._check_frappe()
        records = frappe.get_all(
            "NileGov Payment Record",
            filters={"payment_status": status},
            pluck="name"
        )
        results = []
        for rid in records:
            p = self.get_by_id(rid)
            if p:
                results.append(p)
        return results

    def get_by_reconciliation_status(self, status: str) -> List[PaymentRecord]:
        self._check_frappe()
        records = frappe.get_all(
            "NileGov Payment Record",
            filters={"reconciliation_status": status},
            pluck="name"
        )
        results = []
        for rid in records:
            p = self.get_by_id(rid)
            if p:
                results.append(p)
        return results

    def get_all(self) -> List[PaymentRecord]:
        self._check_frappe()
        records = frappe.get_all("NileGov Payment Record", pluck="name")
        results = []
        for rid in records:
            p = self.get_by_id(rid)
            if p:
                results.append(p)
        return results

    def _map_doc_to_aggregate(self, doc) -> PaymentRecord:
        verification_ts = None
        if doc.verification_timestamp:
            verification_ts = frappe.utils.get_timestamp(doc.verification_timestamp)

        created_ts = None
        if doc.creation:
            created_ts = frappe.utils.get_timestamp(doc.creation)

        updated_ts = None
        if doc.modified:
            updated_ts = frappe.utils.get_timestamp(doc.modified)

        provider_status_checked_ts = None
        if doc.get("provider_status_checked_at"):
            provider_status_checked_ts = frappe.utils.get_timestamp(doc.provider_status_checked_at)

        provider_callback_received_ts = None
        if doc.get("provider_callback_received_at"):
            provider_callback_received_ts = frappe.utils.get_timestamp(doc.provider_callback_received_at)

        provider_ipn_received_ts = None
        if doc.get("provider_ipn_received_at"):
            provider_ipn_received_ts = frappe.utils.get_timestamp(doc.provider_ipn_received_at)

        return PaymentRecord(
            payment_record_id=doc.payment_record_id or doc.name,
            service_request_id=doc.service_request,
            citizen_profile_id=doc.citizen_profile,
            consent_record_id=doc.consent_record,
            amount=float(doc.amount or 0.0),
            currency=doc.currency or "UGX",
            payment_purpose=doc.payment_purpose or "National ID Replacement Fee",
            payment_channel=doc.payment_channel or "Simulated Mobile Money",
            payment_status=doc.payment_status or "Pending",
            simulated_transaction_reference=doc.simulated_transaction_reference or "",
            verification_status=doc.verification_status or "Not Checked",
            verification_timestamp=verification_ts,
            verified_by=doc.verified_by,
            receipt_status=doc.receipt_status or "Receipt Pending",
            receipt_reference=doc.receipt_reference,
            reconciliation_status=doc.reconciliation_status or "Pending Reconciliation",
            failure_reason=doc.failure_reason,
            triggered_by_event=doc.triggered_by_event,
            created_at=created_ts,
            updated_at=updated_ts,
            provider=doc.get("provider") or "Simulated",
            provider_mode=doc.get("provider_mode"),
            provider_order_tracking_id=doc.get("provider_order_tracking_id"),
            provider_merchant_reference=doc.get("provider_merchant_reference"),
            provider_redirect_url=doc.get("provider_redirect_url"),
            provider_payment_method=doc.get("provider_payment_method"),
            provider_confirmation_code=doc.get("provider_confirmation_code"),
            provider_status_code=doc.get("provider_status_code"),
            provider_status_description=doc.get("provider_status_description"),
            provider_status_checked_at=provider_status_checked_ts,
            provider_ipn_id=doc.get("provider_ipn_id"),
            provider_callback_received_at=provider_callback_received_ts,
            provider_ipn_received_at=provider_ipn_received_ts,
            provider_masked_account=doc.get("provider_masked_account")
        )
