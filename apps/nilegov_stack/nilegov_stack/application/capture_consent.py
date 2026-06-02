# Use Case: Capture Consent
# Digi-Verse Uganda Limited

from nilegov_stack.application.ports import ServiceRequestRepository


class CaptureConsent:
    """Application Service verifying and registering citizen legal consent."""
    
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, request_id: str) -> None:
        """Executes the consent capture verification use case."""
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request {request_id} not found.")
            
        request.capture_consent()
        self.repository.save(request)
