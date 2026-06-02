# Use case: Generate Reporting Snapshot
# Digi-Verse Uganda Limited
# Prototype reporting snapshot only. Metrics are calculated from fictional demo data and are not official government statistics.

import time
from typing import Dict, List, Optional, Any
from nilegov_stack.application.ports import (
    ServiceRequestRepository,
    ServiceCatalogueRepository,
    EvidenceDocumentRepository,
    PaymentRecordRepository,
    NotificationEventRepository,
    ReportingSnapshotRepository
)
from nilegov_stack.domain.reporting_snapshot import ReportingSnapshot


class GenerateReportingSnapshot:
    """Application Service to compile deterministic M&E metrics and persist a ReportingSnapshot."""

    def __init__(
        self,
        request_repo: ServiceRequestRepository,
        catalogue_repo: ServiceCatalogueRepository,
        evidence_repo: EvidenceDocumentRepository,
        payment_repo: PaymentRecordRepository,
        notification_repo: NotificationEventRepository,
        snapshot_repo: ReportingSnapshotRepository
    ):
        self.request_repo = request_repo
        self.catalogue_repo = catalogue_repo
        self.evidence_repo = evidence_repo
        self.payment_repo = payment_repo
        self.notification_repo = notification_repo
        self.snapshot_repo = snapshot_repo

    def execute(
        self,
        snapshot_id: str,
        snapshot_name: str,
        period_start: float,
        period_end: float,
        generated_by: str,
        timestamp: Optional[float] = None
    ) -> ReportingSnapshot:
        curr_time = timestamp or time.time()

        # 1. Gather all source data safely
        requests = self.request_repo.get_all() or []
        catalogue_items = self.catalogue_repo.get_all() or []
        payments = self.payment_repo.get_all() or []
        notifications = self.notification_repo.get_all() or []

        # Aggregate evidence documents per service request since EvidenceDocumentRepository lacks get_all()
        evidences = []
        for req in requests:
            req_evidences = self.evidence_repo.get_by_service_request(req.request_id) or []
            evidences.extend(req_evidences)

        # 2. Service Catalogue metrics
        total_services = len(catalogue_items)
        active_services = sum(1 for c in catalogue_items if getattr(c, "active_status", "") == "Active")
        demo_services = sum(1 for c in catalogue_items if getattr(c, "active_status", "") == "Demo Only")

        # 3. Service Requests metrics
        total_requests = 0
        requests_by_status: Dict[str, int] = {}
        requests_by_service: Dict[str, int] = {}
        requests_by_queue: Dict[str, int] = {}
        requests_by_location: Dict[str, int] = {}
        
        within_sla = 0
        at_risk = 0
        overdue = 0
        escalated = 0

        # Workload metrics
        officer_workloads: Dict[str, int] = {}

        for req in requests:
            total_requests += 1

            # Status breakdown
            status = req.status or "Submitted"
            requests_by_status[status] = requests_by_status.get(status, 0) + 1

            # Service breakdown
            service_code = req.service_type or "Unknown"
            requests_by_service[service_code] = requests_by_service.get(service_code, 0) + 1

            # Queue breakdown
            queue = req.queue_name or "Unassigned Queue"
            requests_by_queue[queue] = requests_by_queue.get(queue, 0) + 1

            # Location breakdown
            loc = req.location or "Unknown"
            requests_by_location[loc] = requests_by_location.get(loc, 0) + 1

            # SLA and Escalation state
            sla_state = getattr(req, "sla_state", "Within SLA") or "Within SLA"
            if sla_state == "Within SLA" or sla_state == "Met" or sla_state == "Not Applicable":
                within_sla += 1
            elif sla_state == "At Risk" or getattr(req, "at_risk_flag", False):
                at_risk += 1
            elif sla_state == "Overdue" or getattr(req, "overdue_flag", False) or getattr(req, "sla_status", "") == "Overdue":
                overdue += 1

            esc_state = getattr(req, "escalation_state", "Not Escalated") or "Not Escalated"
            if esc_state == "Escalated" or req.assignment_status == "Supervisor Review":
                escalated += 1

            # Workload
            officer = getattr(req, "assigned_officer_id", None) or getattr(req, "assigned_officer", None)
            if officer:
                officer_workloads[officer] = officer_workloads.get(officer, 0) + 1

        # 4. Evidence completeness & document status counts
        evidence_complete = 0
        evidence_incomplete = 0
        evidence_rejected = 0
        evidence_requiring_replacement = 0

        for ev in evidences:
            status = getattr(ev, "verification_status", "") or getattr(ev, "status", "")
            if status == "Rejected":
                evidence_rejected += 1
            elif status == "Requires Replacement":
                evidence_requiring_replacement += 1

        for req in requests:
            req_docs = [getattr(ev, "document_type", "") for ev in evidences if ev.service_request_id == req.request_id and (getattr(ev, "verification_status", "") == "Accepted" or getattr(ev, "status", "") == "Accepted")]
            item = next((c for c in catalogue_items if c.service_code == req.service_type), None)
            if item and item.required_documents:
                missing = [doc for doc in item.required_documents if doc not in req_docs]
                if len(missing) == 0:
                    evidence_complete += 1
                else:
                    evidence_incomplete += 1
            else:
                # If no catalog item or no required documents, it is technically complete
                evidence_complete += 1

        # 5. Payment metrics
        pay_pending = 0
        pay_submitted = 0
        pay_verified = 0
        pay_failed = 0
        pay_reversed = 0
        total_value = 0.0

        for pay in payments:
            status = getattr(pay, "payment_status", "") or "Pending"
            if status == "Pending":
                pay_pending += 1
            elif status == "Submitted":
                pay_submitted += 1
            elif status == "Verified":
                pay_verified += 1
                total_value += float(pay.amount or 0.0)
            elif status == "Failed":
                pay_failed += 1
            elif status == "Reversed":
                pay_reversed += 1

        payment_val_sum = {
            "total_simulated_payment_value": total_value,
            "payment_pending_count": pay_pending,
            "payment_submitted_count": pay_submitted,
            "payment_verified_count": pay_verified,
            "payment_failed_count": pay_failed,
            "payment_reversed_count": pay_reversed
        }

        # 6. Notification metrics
        notif_draft = 0
        notif_queued = 0
        notif_sent = 0
        notif_failed = 0
        notif_cancelled = 0
        notif_not_required = 0

        for notif in notifications:
            status = getattr(notif, "delivery_status", "") or "Draft"
            if status == "Draft":
                notif_draft += 1
            elif status == "Queued":
                notif_queued += 1
            elif status == "Simulated Sent" or status == "Sent":
                notif_sent += 1
            elif status == "Simulated Failed" or status == "Failed":
                notif_failed += 1
            elif status == "Cancelled":
                notif_cancelled += 1
            elif status == "Not Required":
                notif_not_required += 1

        # Compile snapshot
        snapshot = ReportingSnapshot(
            reporting_snapshot_id=snapshot_id,
            snapshot_name=snapshot_name,
            reporting_period_start=period_start,
            reporting_period_end=period_end,
            generated_at=curr_time,
            generated_by=generated_by,
            source_dataset="Seeded Fictional Demo Data" if len(requests) > 0 else "Empty Dataset",
            total_requests=total_requests,
            total_services=total_services,
            active_services=active_services,
            demo_services=demo_services,
            requests_by_status=requests_by_status,
            requests_by_service=requests_by_service,
            requests_by_queue=requests_by_queue,
            requests_by_location=requests_by_location,
            within_sla_count=within_sla,
            at_risk_count=at_risk,
            overdue_count=overdue,
            escalated_count=escalated,
            evidence_complete_count=evidence_complete,
            evidence_incomplete_count=evidence_incomplete,
            evidence_rejected_count=evidence_rejected,
            evidence_requiring_replacement_count=evidence_requiring_replacement,
            payment_pending_count=pay_pending,
            payment_verified_count=pay_verified,
            payment_failed_count=pay_failed,
            notification_draft_count=notif_draft,
            notification_queued_count=notif_queued,
            notification_simulated_sent_count=notif_sent,
            notification_failed_count=notif_failed,
            notification_cancelled_count=notif_cancelled,
            notification_not_required_count=notif_not_required,
            officer_workload_summary=officer_workloads,
            payment_value_summary=payment_val_sum,
            created_at=curr_time,
            updated_at=curr_time
        )

        self.snapshot_repo.save(snapshot)
        return snapshot
