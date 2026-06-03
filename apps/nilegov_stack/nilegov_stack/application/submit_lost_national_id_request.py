# Use Case: Submit Lost National ID Request
# Digi-Verse Uganda Limited

from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.application.ports import ServiceRequestRepository


class SubmitLostNationalIDRequest:
    """Application Service orchestrating the intake submission of lost ID replacements."""
    
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(
        self,
        request_id: str,
        reference_no: str,
        nin_str: str,
        citizen_name: str,
        phone_number: str,
        location: str,
        description: str,
        email: str = None,
        created_at: float = None
    ) -> ServiceRequest:
        """Executes the request creation use case."""
        nin = NIN(nin_str)
        request = ServiceRequest(
            request_id=request_id,
            reference_no=reference_no,
            citizen_nin=nin,
            citizen_name=citizen_name,
            phone_number=phone_number,
            location=location,
            description=description,
            email=email,
            created_at=created_at
        )
        self.repository.save(request)
        return request
