# Use Case: Request More Information
# Digi-Verse Uganda Limited

import time
from nilegov_stack.application.ports import ServiceRequestRepository, NotificationGateway
from nilegov_stack.domain.service_request import WorkflowStatus


class RequestMoreInformation:
    """Application Service triggering citizen updates on clarification queries."""
    
    def __init__(self, repository: ServiceRequestRepository, notification: NotificationGateway):
        self.repository = repository
        self.notification = notification

    def execute(self, request_id: str, query_details: str, actor: str = "Officer", timestamp: float = None) -> None:
        """Executes the request more information use case."""
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request {request_id} not found.")
            
        if not timestamp:
            timestamp = time.time()
            
        request.update_status(WorkflowStatus.INFORMATION_REQUIRED, actor, timestamp)
        self.repository.save(request)
        
        # Send SMS/email alerts to applicant citizen
        phone = getattr(request, "phone_number", "+256700000000")
        self.notification.send_sms(phone, f"NileGov Info Update required: {query_details}")
