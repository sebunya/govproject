# Use Case: Create Citizen Profile
# Digi-Verse Uganda Limited

from typing import Optional
from nilegov_stack.domain.citizen import CitizenProfile, PreferredContactChannel, CitizenProfileStatus
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.application.ports import CitizenProfileRepository


class CreateCitizenProfile:
    """Application Service to create and persist a new Citizen Profile."""
    
    def __init__(self, repository: CitizenProfileRepository):
        self.repository = repository

    def execute(
        self,
        citizen_profile_id: str,
        full_name: str,
        phone: str,
        location: str,
        email: Optional[str] = None,
        division_or_area: Optional[str] = None,
        preferred_contact_channel: str = PreferredContactChannel.PHONE,
        status: str = CitizenProfileStatus.ACTIVE,
        nin_str: Optional[str] = None,
        created_at: Optional[float] = None
    ) -> CitizenProfile:
        nin = NIN(nin_str) if nin_str else None
        
        profile = CitizenProfile(
            citizen_profile_id=citizen_profile_id,
            full_name=full_name,
            phone=phone,
            location=location,
            email=email,
            division_or_area=division_or_area,
            preferred_contact_channel=preferred_contact_channel,
            status=status,
            nin=nin,
            created_at=created_at,
            updated_at=created_at
        )
        
        # Verify safe demo data
        profile.validate_safe_demo_data()
        
        self.repository.save(profile)
        return profile
