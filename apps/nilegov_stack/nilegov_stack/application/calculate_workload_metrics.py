# Use Case: Calculate Workload Metrics
# Prototype simulation only. No live Government registry access.

from typing import Dict, Any
from nilegov_stack.application.ports import ServiceRequestRepository


class CalculateWorkloadMetrics:
    """Application Service compiling volume metrics for queues and officer workloads."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self) -> Dict[str, Any]:
        """Aggregates unassigned, assigned, supervisor, officer, and department queue counts."""
        all_requests = self.repository.get_all()

        unassigned_count = 0
        assigned_count = 0
        supervisor_review_count = 0
        officer_workloads: Dict[str, int] = {}
        department_queues: Dict[str, int] = {
            "National ID Replacement Desk": 0,
            "Citizen Services Desk": 0,
            "Verification Desk": 0,
            "Payment Review Desk": 0,
            "Supervisor Review Queue": 0,
            "Completed Cases Queue": 0
        }

        for req in all_requests:
            # Count by status
            if req.assignment_status == "Unassigned" and not req.assigned_officer_id:
                unassigned_count += 1
            else:
                assigned_count += 1

            if req.supervisor_review_required or req.assignment_status == "Supervisor Review":
                supervisor_review_count += 1

            # Count by officer
            if req.assigned_officer_id:
                officer_workloads[req.assigned_officer_id] = officer_workloads.get(req.assigned_officer_id, 0) + 1

            # Count by queue_name
            q_name = req.queue_name or "National ID Replacement Desk"
            department_queues[q_name] = department_queues.get(q_name, 0) + 1

        return {
            "total_cases": len(all_requests),
            "unassigned_cases": unassigned_count,
            "assigned_cases": assigned_count,
            "supervisor_review_cases": supervisor_review_count,
            "officer_workloads": officer_workloads,
            "department_queues": department_queues
        }
