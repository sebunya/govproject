# Use Case: Return Case to Officer
# Prototype simulation only. No live Government registry access.

from nilegov_stack.application.ports import ServiceRequestRepository


class ReturnCaseToOfficer:
    """Application Service to return a case from supervisor review back to the assigned officer."""

    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str, timestamp: float) -> None:
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request with ID {request_id} not found.")

        request.return_to_officer(timestamp)
        self.repository.save(request)
