# Use Case: Reassign Officer
# Prototype simulation only. No live Government registry access.

from nilegov_stack.application.ports import ServiceRequestRepository


class ReassignOfficer:
    """Application Service to reassign a service request to a different officer with a reason."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str, new_officer_id: str, reason: str, timestamp: float) -> None:
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request with ID {request_id} not found.")

        request.reassign_to_officer(new_officer_id, reason, timestamp)
        self.repository.save(request)
