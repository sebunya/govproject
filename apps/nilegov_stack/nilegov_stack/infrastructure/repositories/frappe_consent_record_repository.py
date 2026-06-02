# Frappe-based Consent Record Repository
# Prototype simulation only. No live Government registry access.

try:
    import frappe
except ImportError:
    frappe = None

from typing import Optional, List
from nilegov_stack.application.ports import ConsentRecordRepository
from nilegov_stack.domain.consent import ConsentRecord, ConsentStatus


class FrappeConsentRecordRepository(ConsentRecordRepository):
    """Frappe-based repository for persisting and loading Consent Record aggregates."""

    def _check_frappe(self):
        if not frappe:
            raise ImportError("Frappe framework is not loaded in this environment.")

    def save(self, consent_record: ConsentRecord) -> None:
        self._check_frappe()

        # Load or create document
        if frappe.db.exists("NileGov Consent Record", consent_record.consent_record_id):
            doc = frappe.get_doc("NileGov Consent Record", consent_record.consent_record_id)
        else:
            doc = frappe.new_doc("NileGov Consent Record")
            doc.consent_record_id = consent_record.consent_record_id

        doc.citizen_profile = consent_record.citizen_profile_id
        doc.consent_purpose = consent_record.consent_purpose
        doc.consent_channel = consent_record.consent_channel
        doc.consent_status = consent_record.consent_status
        doc.service_request = consent_record.service_request_id
        doc.notes = consent_record.notes
        doc.recorded_by = consent_record.recorded_by
        doc.ip_address = consent_record.ip_address
        doc.user_agent = consent_record.user_agent

        # Convert timestamps / dates
        if consent_record.consent_timestamp:
            doc.consent_given_at = frappe.utils.get_datetime(consent_record.consent_timestamp)
        if consent_record.expiry_time:
            doc.expiry_date = frappe.utils.get_datetime(consent_record.expiry_time).date()
        if consent_record.withdrawal_timestamp:
            doc.withdrawal_timestamp = frappe.utils.get_datetime(consent_record.withdrawal_timestamp)

        doc.save(ignore_permissions=True)
        frappe.db.commit()

    def get_by_id(self, consent_id: str) -> Optional[ConsentRecord]:
        self._check_frappe()
        if not frappe.db.exists("NileGov Consent Record", consent_id):
            return None

        doc = frappe.get_doc("NileGov Consent Record", consent_id)
        return self._map_doc_to_aggregate(doc)

    def get_by_citizen_profile(self, profile_id: str) -> List[ConsentRecord]:
        self._check_frappe()
        record_ids = frappe.get_all(
            "NileGov Consent Record",
            filters={"citizen_profile": profile_id},
            pluck="name"
        )
        results = []
        for cid in record_ids:
            rec = self.get_by_id(cid)
            if rec:
                results.append(rec)
        return results

    def get_by_service_request(self, request_id: str) -> List[ConsentRecord]:
        self._check_frappe()
        record_ids = frappe.get_all(
            "NileGov Consent Record",
            filters={"service_request": request_id},
            pluck="name"
        )
        results = []
        for cid in record_ids:
            rec = self.get_by_id(cid)
            if rec:
                results.append(rec)
        return results

    def _map_doc_to_aggregate(self, doc) -> ConsentRecord:
        consent_time = frappe.utils.get_timestamp(doc.consent_given_at) if doc.consent_given_at else None
        expiry_time = frappe.utils.get_timestamp(doc.expiry_date) if doc.expiry_date else None
        withdrawal_time = frappe.utils.get_timestamp(doc.withdrawal_timestamp) if doc.withdrawal_timestamp else None

        record = ConsentRecord(
            consent_record_id=doc.consent_record_id,
            citizen_profile_id=doc.citizen_profile,
            consent_purpose=doc.consent_purpose,
            consent_channel=doc.consent_channel,
            consent_status=doc.consent_status or ConsentStatus.GRANTED,
            consent_timestamp=consent_time,
            service_request_id=doc.service_request,
            expiry_time=expiry_time,
            withdrawal_timestamp=withdrawal_time,
            recorded_by=doc.recorded_by,
            notes=doc.notes,
            ip_address=doc.ip_address,
            user_agent=doc.user_agent,
            created_at=frappe.utils.get_timestamp(doc.creation),
            updated_at=frappe.utils.get_timestamp(doc.modified)
        )
        return record
