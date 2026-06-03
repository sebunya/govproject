# Use Case: Get Citizen Profile
# Digi-Verse Uganda Limited

from typing import Optional
from nilegov_stack.domain.citizen import CitizenProfile
from nilegov_stack.application.ports import CitizenProfileRepository


class GetCitizenProfile:
    """Application Service to retrieve a citizen profile by ID."""
    
    def __init__(self, repository: CitizenProfileRepository):
        self.repository = repository

    def execute(self, profile_id: str) -> Optional[CitizenProfile]:
        return self.repository.get_by_id(profile_id)
