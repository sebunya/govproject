# Use Case: Assign Case
# Digi-Verse Uganda Limited

from nilegov_stack.application.ports import ServiceRequestRepository


class AssignCase:
    """Application Service assigning verified service requests to active desk officers."""
    
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str, officer_id: str) -> None:
        """Executes the case assignment use case."""
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request {request_id} not found.")
            
        request.assign_officer(officer_id)
        self.repository.save(request)
