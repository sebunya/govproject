# Use Case: Run Simulated Identity Check
# Digi-Verse Uganda Limited

import time
from typing import Optional
from nilegov_stack.application.ports import ServiceRequestRepository, IdentityVerificationGateway, ConsentRecordRepository


class RunSimulatedIdentityCheck:
    """Application Service orchestrating the simulated NIRA database verification check."""
    
    def __init__(
        self,
        repository: ServiceRequestRepository,
        gateway: IdentityVerificationGateway,
        consent_repository: Optional[ConsentRecordRepository] = None
    ):
        self.repository = repository
        self.gateway = gateway
        self.consent_repository = consent_repository

    def execute(self, request_id: str, actor: str = "Officer", timestamp: float = None) -> str:
        """Executes the simulated identity check use case, returning verification result status."""
        request = self.repository.get_by_id(request_id)
        if not request:
            raise ValueError(f"Service Request {request_id} not found.")
            
        if not timestamp:
            timestamp = time.time()
            
        # Check active consent if repository is supplied
        consent_granted = True
        if self.consent_repository and request.citizen_profile_id:
            from nilegov_stack.application.check_active_consent import CheckActiveConsent
            from nilegov_stack.domain.consent import ConsentPurpose
            checker = CheckActiveConsent(self.consent_repository)
            consent_granted = checker.execute(
                profile_id=request.citizen_profile_id,
                purpose=ConsentPurpose.IDENTITY_VERIFICATION,
                current_time=timestamp
            )
            
        # Call the simulation registry gateway port
        result = self.gateway.verify_identity(str(request.citizen_nin))
        verification_result = result.get("result", "Requires Review")
        
        # If consent is not granted, we record it as a simulated warning but do not hard block the workflow
        if not consent_granted:
            verification_result = "Requires Review"
            
        request.trigger_identity_verification(verification_result, actor, timestamp)
        self.repository.save(request)
        return verification_result
