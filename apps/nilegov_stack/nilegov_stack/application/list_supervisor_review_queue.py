# Use Case: List Supervisor Review Queue
# Prototype simulation only. No live Government registry access.

from typing import List
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.application.ports import ServiceRequestRepository


class ListSupervisorReviewQueue:
    """Application Service to list all requests currently in the Supervisor Review queue."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self) -> List[ServiceRequest]:
        all_requests = self.repository.get_all()
        return [
            req for req in all_requests
            if req.supervisor_review_required or req.assignment_status == "Supervisor Review"
        ]
