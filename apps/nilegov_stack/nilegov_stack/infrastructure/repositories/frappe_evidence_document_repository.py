# Frappe-based Evidence Document Repository
# Prototype simulation only. No live Government registry access.

try:
    import frappe
except ImportError:
    frappe = None

from typing import Optional, List
from nilegov_stack.application.ports import EvidenceDocumentRepository
from nilegov_stack.domain.evidence import EvidenceDocument, EvidenceVerificationStatus


class FrappeEvidenceDocumentRepository(EvidenceDocumentRepository):
    """Frappe-based repository for persisting and loading Evidence Document aggregates."""

    def _check_frappe(self):
        if not frappe:
            raise ImportError("Frappe framework is not loaded in this environment.")

    def save(self, evidence_document: EvidenceDocument) -> None:
        self._check_frappe()

        # Load or create document
        if frappe.db.exists("NileGov Evidence Document", evidence_document.evidence_document_id):
            doc = frappe.get_doc("NileGov Evidence Document", evidence_document.evidence_document_id)
        else:
            doc = frappe.new_doc("NileGov Evidence Document")
            doc.evidence_document_id = evidence_document.evidence_document_id

        doc.citizen_profile = evidence_document.citizen_profile_id
        doc.service_request = evidence_document.service_request_id
        doc.consent_record = evidence_document.consent_record_id
        doc.document_type = evidence_document.document_type
        doc.document_title = evidence_document.document_title
        doc.file = evidence_document.file
        doc.upload_channel = evidence_document.upload_channel
        doc.uploaded_by = evidence_document.uploaded_by
        doc.verification_status = evidence_document.verification_status
        doc.verified_by = evidence_document.verified_by
        doc.visibility = "Citizen and Officer"
        doc.officer_notes = evidence_document.officer_notes
        doc.disclaimer = evidence_document.disclaimer

        # Convert timestamps
        if evidence_document.uploaded_at:
            doc.uploaded_at = frappe.utils.get_datetime(evidence_document.uploaded_at)
        if evidence_document.verified_timestamp:
            doc.verified_timestamp = frappe.utils.get_datetime(evidence_document.verified_timestamp)

        doc.save(ignore_permissions=True)
        frappe.db.commit()

    def get_by_id(self, evidence_id: str) -> Optional[EvidenceDocument]:
        self._check_frappe()
        if not frappe.db.exists("NileGov Evidence Document", evidence_id):
            return None

        doc = frappe.get_doc("NileGov Evidence Document", evidence_id)
        return self._map_doc_to_aggregate(doc)

    def get_by_citizen_profile(self, profile_id: str) -> List[EvidenceDocument]:
        self._check_frappe()
        record_ids = frappe.get_all(
            "NileGov Evidence Document",
            filters={"citizen_profile": profile_id},
            pluck="name"
        )
        results = []
        for rid in record_ids:
            rec = self.get_by_id(rid)
            if rec:
                results.append(rec)
        return results

    def get_by_service_request(self, request_id: str) -> List[EvidenceDocument]:
        self._check_frappe()
        record_ids = frappe.get_all(
            "NileGov Evidence Document",
            filters={"service_request": request_id},
            pluck="name"
        )
        results = []
        for rid in record_ids:
            rec = self.get_by_id(rid)
            if rec:
                results.append(rec)
        return results

    def _map_doc_to_aggregate(self, doc) -> EvidenceDocument:
        upload_time = frappe.utils.get_timestamp(doc.uploaded_at) if doc.uploaded_at else None
        verified_time = frappe.utils.get_timestamp(doc.verified_timestamp) if doc.verified_timestamp else None

        record = EvidenceDocument(
            evidence_document_id=doc.evidence_document_id,
            citizen_profile_id=doc.citizen_profile,
            service_request_id=doc.service_request,
            consent_record_id=doc.consent_record,
            document_type=doc.document_type,
            document_title=doc.document_title,
            file=doc.file,
            upload_channel=doc.upload_channel or "Web Form",
            uploaded_by=doc.uploaded_by,
            uploaded_at=upload_time,
            verification_status=doc.verification_status or EvidenceVerificationStatus.SUBMITTED,
            verified_by=doc.verified_by,
            verified_timestamp=verified_time,
            officer_notes=doc.officer_notes,
            disclaimer=doc.disclaimer or "Prototype simulation only. No live Government registry access.",
            created_at=frappe.utils.get_timestamp(doc.creation),
            updated_at=frappe.utils.get_timestamp(doc.modified)
        )
        return record
