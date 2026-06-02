# Use Case: Calculate Dashboard Metrics
# Digi-Verse Uganda Limited

from typing import Dict, Any, List
from nilegov_stack.application.ports import ServiceRequestRepository
from nilegov_stack.domain.service_request import WorkflowStatus


class CalculateDashboardMetrics:
    """Application Service compiling read-only SLA and volume stats for leadership."""
    
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_ids: List[str]) -> Dict[str, Any]:
        """Calculates volume, status groupings, and SLA metrics."""
        total_requests = len(request_ids)
        
        submitted = 0
        under_review = 0
        payment_pending = 0
        approved = 0
        ready_for_collection = 0
        closed = 0
        rejected = 0
        information_required = 0
        overdue = 0
        
        for request_id in request_ids:
            request = self.repository.get_by_id(request_id)
            if not request:
                continue
                
            status = request.status
            if status == WorkflowStatus.SUBMITTED:
                submitted += 1
            elif status == WorkflowStatus.UNDER_REVIEW:
                under_review += 1
            elif status == WorkflowStatus.INFORMATION_REQUIRED:
                information_required += 1
            elif status == WorkflowStatus.PAYMENT_PENDING:
                payment_pending += 1
            elif status == WorkflowStatus.APPROVED:
                approved += 1
            elif status == WorkflowStatus.READY_FOR_COLLECTION:
                ready_for_collection += 1
            elif status == WorkflowStatus.CLOSED:
                closed += 1
            elif status == WorkflowStatus.REJECTED:
                rejected += 1
                
            if request.sla_status == "Overdue":
                overdue += 1

        return {
            "total_requests": total_requests,
            "submitted": submitted,
            "under_review": under_review,
            "information_required": information_required,
            "payment_pending": payment_pending,
            "approved": approved,
            "ready_for_collection": ready_for_collection,
            "closed": closed,
            "rejected": rejected,
            "overdue": overdue
        }
