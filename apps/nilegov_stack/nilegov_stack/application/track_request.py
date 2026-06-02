# Use Case: Track Request
# Digi-Verse Uganda Limited

from typing import Dict, Any
from nilegov_stack.application.ports import ServiceRequestRepository


class TrackRequest:
    """Application Service validating progress checkpoints for citizens."""
    
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def execute(self, reference_no: str) -> Dict[str, Any]:
        """Queries reference numbers and returns citizen-visible progress tracking payloads."""
        request = self.repository.get_by_reference(reference_no)
        if not request:
            return {"found": False, "message": "Reference number not found."}
            
        return {
            "found": True,
            "reference_no": request.reference_no,
            "status": request.status,
            "has_consent": request.has_consent,
            "identity_verified": request.identity_verified
        }
