# Use Case: List Requests by Officer
# Prototype simulation only. No live Government registry access.

from typing import List
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.application.ports import ServiceRequestRepository


class ListRequestsByOfficer:
    """Application Service to list all service requests assigned to a specific officer."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, officer_id: str) -> List[ServiceRequest]:
        all_requests = self.repository.get_all()
        return [
            req for req in all_requests
            if req.assigned_officer_id == officer_id
        ]
