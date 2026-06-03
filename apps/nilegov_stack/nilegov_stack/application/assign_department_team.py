# Use Case: Assign Department/Team Queue
# Prototype simulation only. No live Government registry access.

from typing import Optional
from nilegov_stack.application.ports import ServiceRequestRepository


class AssignDepartmentTeam:
    """Application Service to route a service request to a department/team queue."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str, department: str, team: Optional[str], timestamp: float) -> None:
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request with ID {request_id} not found.")

        request.assign_to_department(department, team, timestamp)
        self.repository.save(request)
