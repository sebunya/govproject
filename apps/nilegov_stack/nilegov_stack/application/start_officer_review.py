# Use Case: Start Officer Review
# Digi-Verse Uganda Limited

from nilegov_stack.application.ports import ServiceRequestRepository
from nilegov_stack.domain.service_request import WorkflowStatus


class StartOfficerReview:
    """Application Service initiating desk reviews and setting SLA metrics."""
    
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str, deadline: float, actor: str = "Officer", timestamp: float = None) -> None:
        """Executes the start review use case, calculating SLA deadlines."""
        import time
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request {request_id} not found.")
            
        if not timestamp:
            timestamp = time.time()
            
        request.sla_deadline = deadline
        request.update_status(WorkflowStatus.UNDER_REVIEW, actor, timestamp)
        self.repository.save(request)
