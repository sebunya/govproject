# Use Case: Close Case
# Digi-Verse Uganda Limited

import time
from nilegov_stack.application.ports import ServiceRequestRepository
from nilegov_stack.domain.service_request import WorkflowStatus


class CloseCase:
    """Application Service validating resolutions and archiving service requests."""
    
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str, note: str, approved: bool, actor: str = "Officer", timestamp: float = None) -> None:
        """Executes the case closing/rejection use case."""
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request {request_id} not found.")
            
        if not timestamp:
            timestamp = time.time()
            
        request.closure_notes = note
        if approved:
            request.decision = "Approved"
            request.update_status(WorkflowStatus.APPROVED, actor, timestamp)
            request.update_status(WorkflowStatus.READY_FOR_COLLECTION, actor, timestamp)
            request.update_status(WorkflowStatus.CLOSED, actor, timestamp)
        else:
            request.decision = "Rejected"
            request.update_status(WorkflowStatus.REJECTED, actor, timestamp)
            
        self.repository.save(request)
