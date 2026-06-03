# Use Case: List Unassigned Requests
# Prototype simulation only. No live Government registry access.

from typing import List
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.application.ports import ServiceRequestRepository


class ListUnassignedRequests:
    """Application Service to list all unassigned service requests."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self) -> List[ServiceRequest]:
        all_requests = self.repository.get_all()
        return [
            req for req in all_requests
            if not req.assigned_officer_id and req.assignment_status == "Unassigned"
        ]
