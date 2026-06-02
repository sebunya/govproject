# Reporting Snapshot Domain Model
# Digi-Verse Uganda Limited
# Prototype reporting snapshot only. Metrics are calculated from fictional demo data and are not official government statistics.

import time
from typing import Dict, Optional, Any

class ReportingSnapshot:
    """Domain aggregate representing an M&E Reporting Snapshot compiled at a point in time."""

    DISCLAIMER = "Prototype reporting snapshot only. Metrics are calculated from fictional demo data and are not official government statistics."

    def __init__(
        self,
        reporting_snapshot_id: str,
        snapshot_name: str,
        reporting_period_start: float,
        reporting_period_end: float,
        generated_at: float,
        generated_by: str,
        source_dataset: str,
        total_requests: int,
        total_services: int,
        active_services: int,
        demo_services: int,
        requests_by_status: Dict[str, int],
        requests_by_service: Dict[str, int],
        requests_by_queue: Dict[str, int],
        requests_by_location: Dict[str, int],
        within_sla_count: int,
        at_risk_count: int,
        overdue_count: int,
        escalated_count: int,
        evidence_complete_count: int,
        evidence_incomplete_count: int,
        evidence_rejected_count: int = 0,
        evidence_requiring_replacement_count: int = 0,
        payment_pending_count: int = 0,
        payment_verified_count: int = 0,
        payment_failed_count: int = 0,
        notification_draft_count: int = 0,
        notification_queued_count: int = 0,
        notification_simulated_sent_count: int = 0,
        notification_failed_count: int = 0,
        notification_cancelled_count: int = 0,
        notification_not_required_count: int = 0,
        officer_workload_summary: Dict[str, int] = None,
        payment_value_summary: Dict[str, float] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ):
        self.reporting_snapshot_id = reporting_snapshot_id
        
        if not snapshot_name:
            raise ValueError("Snapshot name is required.")
        self.snapshot_name = snapshot_name
        
        if reporting_period_start > reporting_period_end:
            raise ValueError("Reporting period start must be before end.")
        self.reporting_period_start = reporting_period_start
        self.reporting_period_end = reporting_period_end
        
        self.generated_at = generated_at
        self.generated_by = generated_by
        self.source_dataset = source_dataset
        
        if total_requests < 0:
            raise ValueError("Total requests cannot be negative.")
        self.total_requests = total_requests
        
        self.total_services = total_services
        self.active_services = active_services
        self.demo_services = demo_services
        
        self.requests_by_status = requests_by_status or {}
        self.requests_by_service = requests_by_service or {}
        self.requests_by_queue = requests_by_queue or {}
        self.requests_by_location = requests_by_location or {}
        
        self.within_sla_count = within_sla_count
        self.at_risk_count = at_risk_count
        self.overdue_count = overdue_count
        self.escalated_count = escalated_count
        
        self.evidence_complete_count = evidence_complete_count
        self.evidence_incomplete_count = evidence_incomplete_count
        self.evidence_rejected_count = evidence_rejected_count
        self.evidence_requiring_replacement_count = evidence_requiring_replacement_count
        
        self.payment_pending_count = payment_pending_count
        self.payment_verified_count = payment_verified_count
        self.payment_failed_count = payment_failed_count
        
        self.notification_draft_count = notification_draft_count
        self.notification_queued_count = notification_queued_count
        self.notification_simulated_sent_count = notification_simulated_sent_count
        self.notification_failed_count = notification_failed_count
        self.notification_cancelled_count = notification_cancelled_count
        self.notification_not_required_count = notification_not_required_count
        
        self.officer_workload_summary = officer_workload_summary or {}
        self.payment_value_summary = payment_value_summary or {}
        
        self.disclaimer = self.DISCLAIMER
        self.created_at = created_at or time.time()
        self.updated_at = updated_at or self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the aggregate properties to a dictionary."""
        return {
            "reporting_snapshot_id": self.reporting_snapshot_id,
            "snapshot_name": self.snapshot_name,
            "reporting_period_start": self.reporting_period_start,
            "reporting_period_end": self.reporting_period_end,
            "generated_at": self.generated_at,
            "generated_by": self.generated_by,
            "source_dataset": self.source_dataset,
            "total_requests": self.total_requests,
            "total_services": self.total_services,
            "active_services": self.active_services,
            "demo_services": self.demo_services,
            "requests_by_status": self.requests_by_status,
            "requests_by_service": self.requests_by_service,
            "requests_by_queue": self.requests_by_queue,
            "requests_by_location": self.requests_by_location,
            "within_sla_count": self.within_sla_count,
            "at_risk_count": self.at_risk_count,
            "overdue_count": self.overdue_count,
            "escalated_count": self.escalated_count,
            "evidence_complete_count": self.evidence_complete_count,
            "evidence_incomplete_count": self.evidence_incomplete_count,
            "evidence_rejected_count": self.evidence_rejected_count,
            "evidence_requiring_replacement_count": self.evidence_requiring_replacement_count,
            "payment_pending_count": self.payment_pending_count,
            "payment_verified_count": self.payment_verified_count,
            "payment_failed_count": self.payment_failed_count,
            "notification_draft_count": self.notification_draft_count,
            "notification_queued_count": self.notification_queued_count,
            "notification_simulated_sent_count": self.notification_simulated_sent_count,
            "notification_failed_count": self.notification_failed_count,
            "notification_cancelled_count": self.notification_cancelled_count,
            "notification_not_required_count": self.notification_not_required_count,
            "officer_workload_summary": self.officer_workload_summary,
            "payment_value_summary": self.payment_value_summary,
            "disclaimer": self.disclaimer,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
