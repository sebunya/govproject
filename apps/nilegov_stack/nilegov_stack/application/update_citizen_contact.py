# Use Case: Update Citizen Contact Details
# Digi-Verse Uganda Limited

from typing import Optional
from nilegov_stack.domain.citizen import CitizenProfile
from nilegov_stack.application.ports import CitizenProfileRepository


class UpdateCitizenContact:
    """Application Service to update a citizen profile's contact information."""
    
    def __init__(self, repository: CitizenProfileRepository):
        self.repository = repository

    def execute(
        self,
        profile_id: str,
        phone: str,
        email: Optional[str] = None,
        preferred_contact_channel: Optional[str] = None,
        updated_at: Optional[float] = None
    ) -> CitizenProfile:
        profile = self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Citizen profile not found: {profile_id}")
            
        profile.update_contact_details(
            phone=phone,
            email=email,
            preferred_contact_channel=preferred_contact_channel
        )
        
        if updated_at:
            profile.updated_at = updated_at
            
        self.repository.save(profile)
        return profile
