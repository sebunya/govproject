# Use Case: Assign Officer
# Prototype simulation only. No live Government registry access.

from nilegov_stack.application.ports import ServiceRequestRepository


class AssignOfficer:
    """Application Service to assign a service request to an officer."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str, officer_id: str, timestamp: float) -> None:
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request with ID {request_id} not found.")

        request.assign_to_officer(officer_id, timestamp)
        self.repository.save(request)
