# Use Case: List Service Requests Linked to Citizen Profile
# Digi-Verse Uganda Limited

from typing import List
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.application.ports import ServiceRequestRepository


class ListCitizenServiceRequests:
    """Application Service to list all service requests linked to a citizen profile."""
    
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, profile_id: str) -> List[ServiceRequest]:
        return self.repository.get_by_citizen_profile(profile_id)
