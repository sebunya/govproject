# Use Case: Mark Supervisor Review
# Prototype simulation only. No live Government registry access.

from nilegov_stack.application.ports import ServiceRequestRepository


class MarkSupervisorReview:
    """Application Service to route a case to supervisor review."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str, supervisor_id: str, timestamp: float) -> None:
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request with ID {request_id} not found.")

        request.mark_supervisor_review(supervisor_id, timestamp)
        self.repository.save(request)
