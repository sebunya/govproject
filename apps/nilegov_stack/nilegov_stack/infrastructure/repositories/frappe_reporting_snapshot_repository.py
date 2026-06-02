# Frappe-based Reporting Snapshot Repository
# Prototype reporting snapshot only. Metrics are calculated from fictional demo data and are not official government statistics.

try:
    import frappe
except ImportError:
    frappe = None

from typing import Optional, List
import json
from nilegov_stack.application.ports import ReportingSnapshotRepository
from nilegov_stack.domain.reporting_snapshot import ReportingSnapshot


class FrappeReportingSnapshotRepository(ReportingSnapshotRepository):
    """Frappe-based repository mapping for ReportingSnapshot aggregates.
    
    Note: Real database persistence is deferred to Hetzner deployment.
    This serves as a mockable adapter for unit tests and local simulations.
    """

    def __init__(self):
        # Fallback storage if frappe is missing or tables are not initialized
        self._in_memory = {}

    def _check_frappe(self):
        if not frappe:
            return False
        try:
            return bool(frappe.db.table_exists("NileGov Reporting Snapshot"))
        except Exception:
            return False

    def save(self, snapshot: ReportingSnapshot) -> None:
        if self._check_frappe():
            # If table exists in target Frappe environment, save document
            if frappe.db.exists("NileGov Reporting Snapshot", snapshot.reporting_snapshot_id):
                doc = frappe.get_doc("NileGov Reporting Snapshot", snapshot.reporting_snapshot_id)
            else:
                doc = frappe.new_doc("NileGov Reporting Snapshot")
                doc.reporting_snapshot_id = snapshot.reporting_snapshot_id

            doc.snapshot_name = snapshot.snapshot_name
            doc.reporting_period_start = snapshot.reporting_period_start
            doc.reporting_period_end = snapshot.reporting_period_end
            doc.generated_at = snapshot.generated_at
            doc.generated_by = snapshot.generated_by
            doc.source_dataset = snapshot.source_dataset
            doc.total_requests = snapshot.total_requests
            doc.total_services = snapshot.total_services
            doc.active_services = snapshot.active_services
            doc.demo_services = snapshot.demo_services
            
            # Serialize dictionaries as JSON strings
            doc.requests_by_status = json.dumps(snapshot.requests_by_status)
            doc.requests_by_service = json.dumps(snapshot.requests_by_service)
            doc.requests_by_queue = json.dumps(snapshot.requests_by_queue)
            doc.requests_by_location = json.dumps(snapshot.requests_by_location)
            
            doc.within_sla_count = snapshot.within_sla_count
            doc.at_risk_count = snapshot.at_risk_count
            doc.overdue_count = snapshot.overdue_count
            doc.escalated_count = snapshot.escalated_count
            
            doc.evidence_complete_count = snapshot.evidence_complete_count
            doc.evidence_incomplete_count = snapshot.evidence_incomplete_count
            doc.payment_pending_count = snapshot.payment_pending_count
            doc.payment_verified_count = snapshot.payment_verified_count
            doc.payment_failed_count = snapshot.payment_failed_count
            
            doc.notification_queued_count = snapshot.notification_queued_count
            doc.notification_simulated_sent_count = snapshot.notification_simulated_sent_count
            doc.notification_failed_count = snapshot.notification_failed_count
            
            doc.officer_workload_summary = json.dumps(snapshot.officer_workload_summary)
            doc.payment_value_summary = json.dumps(snapshot.payment_value_summary)
            
            doc.disclaimer = snapshot.disclaimer
            doc.save(ignore_permissions=True)
            frappe.db.commit()
        else:
            self._in_memory[snapshot.reporting_snapshot_id] = snapshot

    def get_by_id(self, snapshot_id: str) -> Optional[ReportingSnapshot]:
        if self._check_frappe():
            if not frappe.db.exists("NileGov Reporting Snapshot", snapshot_id):
                return None
            doc = frappe.get_doc("NileGov Reporting Snapshot", snapshot_id)
            
            # Deserialize JSON fields
            req_status = json.loads(doc.requests_by_status) if doc.requests_by_status else {}
            req_service = json.loads(doc.requests_by_service) if doc.requests_by_service else {}
            req_queue = json.loads(doc.requests_by_queue) if doc.requests_by_queue else {}
            req_loc = json.loads(doc.requests_by_location) if doc.requests_by_location else {}
            workload = json.loads(doc.officer_workload_summary) if doc.officer_workload_summary else {}
            payments = json.loads(doc.payment_value_summary) if doc.payment_value_summary else {}
            
            created_ts = None
            if doc.creation:
                created_ts = frappe.utils.get_timestamp(doc.creation)

            updated_ts = None
            if doc.modified:
                updated_ts = frappe.utils.get_timestamp(doc.modified)

            return ReportingSnapshot(
                reporting_snapshot_id=doc.reporting_snapshot_id or doc.name,
                snapshot_name=doc.snapshot_name,
                reporting_period_start=float(doc.reporting_period_start),
                reporting_period_end=float(doc.reporting_period_end),
                generated_at=float(doc.generated_at),
                generated_by=doc.generated_by,
                source_dataset=doc.source_dataset,
                total_requests=int(doc.total_requests),
                total_services=int(doc.total_services),
                active_services=int(doc.active_services),
                demo_services=int(doc.demo_services),
                requests_by_status=req_status,
                requests_by_service=req_service,
                requests_by_queue=req_queue,
                requests_by_location=req_loc,
                within_sla_count=int(doc.within_sla_count),
                at_risk_count=int(doc.at_risk_count),
                overdue_count=int(doc.overdue_count),
                escalated_count=int(doc.escalated_count),
                evidence_complete_count=int(doc.evidence_complete_count),
                evidence_incomplete_count=int(doc.evidence_incomplete_count),
                payment_pending_count=int(doc.payment_pending_count),
                payment_verified_count=int(doc.payment_verified_count),
                payment_failed_count=int(doc.payment_failed_count),
                notification_queued_count=int(doc.notification_queued_count),
                notification_simulated_sent_count=int(doc.notification_simulated_sent_count),
                notification_failed_count=int(doc.notification_failed_count),
                officer_workload_summary=workload,
                payment_value_summary=payments,
                created_at=created_ts,
                updated_at=updated_ts
            )
        else:
            return self._in_memory.get(snapshot_id)

    def get_all(self) -> List[ReportingSnapshot]:
        if self._check_frappe():
            records = frappe.get_all("NileGov Reporting Snapshot", pluck="name")
            results = []
            for rid in records:
                snap = self.get_by_id(rid)
                if snap:
                    results.append(snap)
            return results
        else:
            return list(self._in_memory.values())
