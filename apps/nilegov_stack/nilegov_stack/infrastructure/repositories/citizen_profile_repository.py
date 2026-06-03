# In-memory Citizen Profile Repository
# Digi-Verse Uganda Limited

from typing import Dict, Optional
from nilegov_stack.application.ports import CitizenProfileRepository
from nilegov_stack.domain.citizen import CitizenProfile


class InMemoryCitizenProfileRepository(CitizenProfileRepository):
    """In-memory implementation of the CitizenProfileRepository port for testing."""
    
    def __init__(self):
        self._profiles: Dict[str, CitizenProfile] = {}

    def save(self, profile: CitizenProfile) -> None:
        self._profiles[profile.citizen_profile_id] = profile

    def get_by_id(self, profile_id: str) -> Optional[CitizenProfile]:
        return self._profiles.get(profile_id)

    def get_by_nin(self, nin: str) -> Optional[CitizenProfile]:
        for profile in self._profiles.values():
            if profile.nin and str(profile.nin) == nin:
                return profile
        return None
