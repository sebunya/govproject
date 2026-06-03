# Use Case: Supervisor Review
# Digi-Verse Uganda Limited

import time
from nilegov_stack.application.ports import ServiceRequestRepository


class SupervisorReview:
    """Application Service enabling supervisors to resolve escalated cases."""
    
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str, supervisor_id: str, actor: str = "Supervisor", timestamp: float = None) -> None:
        """Executes the supervisor review transition use case."""
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request {request_id} not found.")
            
        if not timestamp:
            timestamp = time.time()
            
        request.assigned_supervisor_id = supervisor_id
        request.add_note(f"Supervisor review started by {supervisor_id}.", actor, timestamp)
        self.repository.save(request)
