# Use Case: List Requests by Department/Team Queue
# Prototype simulation only. No live Government registry access.

from typing import List
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.application.ports import ServiceRequestRepository


class ListRequestsByDepartment:
    """Application Service to list all service requests in a specific department queue."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, department: str) -> List[ServiceRequest]:
        all_requests = self.repository.get_all()
        return [
            req for req in all_requests
            if req.assigned_department == department or req.queue_name == department
        ]
