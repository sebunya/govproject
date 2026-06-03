# Use Case: Verify Payment
# Digi-Verse Uganda Limited

import time
from typing import Optional
from nilegov_stack.application.ports import ServiceRequestRepository, PaymentVerificationGateway, ConsentRecordRepository
from nilegov_stack.domain.service_request import WorkflowStatus


class VerifyPayment:
    """Application Service orchestrating simulated payment verification check."""
    
    def __init__(
        self,
        repository: ServiceRequestRepository,
        gateway: PaymentVerificationGateway,
        consent_repository: Optional[ConsentRecordRepository] = None
    ):
        self.repository = repository
        self.gateway = gateway
        self.consent_repository = consent_repository

    def execute(self, request_id: str, actor: str = "Officer", timestamp: float = None) -> str:
        """Executes the payment verification use case."""
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
                purpose=ConsentPurpose.PAYMENT_VERIFICATION,
                current_time=timestamp
            )
            
        result = self.gateway.verify_payment(request.reference_no)
        payment_status = result.get("status", "Failed")
        amount = result.get("amount", 0.0)
        
        # If consent is not granted, we default the payment check to Pending
        if not consent_granted:
            payment_status = "Pending"
            
        request.update_payment_status(payment_status, amount, timestamp)
        
        if payment_status == "Verified":
            request.update_status(WorkflowStatus.PAYMENT_VERIFIED, actor, timestamp)
            
        self.repository.save(request)
        return payment_status
