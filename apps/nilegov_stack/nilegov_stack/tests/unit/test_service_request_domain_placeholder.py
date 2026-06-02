# Service Request Domain Rules Unit Test
# Digi-Verse Uganda Limited

import pytest
import time
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.exceptions import WorkflowTransitionException
from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus


def test_service_request_initialization():
    """Verifies default request constructor fields."""
    nin = NIN("CF123456789012")
    request = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256780000000",
        location="Ntinda, Kampala",
        description="Lost my ID near the clinic."
    )
    
    assert request.request_id == "req_001"
    assert request.reference_no == "NGS-NIRA-2026-0001"
    assert request.citizen_nin == nin
    assert request.citizen_name == "Demo Citizen A"
    assert request.phone_number == "+256780000000"
    assert request.location == "Ntinda, Kampala"
    assert request.description == "Lost my ID near the clinic."
    assert request.status == WorkflowStatus.SUBMITTED
    assert request.identity_status == "Requires Review"
    assert request.payment_status == "Not Required"
    assert len(request.events) == 1
  

def test_valid_submission_workflow_path():
    """Verifies standard citizen intake progression."""
    nin = NIN("CF123456789012")
    request = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256780000000",
        location="Ntinda, Kampala",
        description="Lost my ID."
    )
    
    # Initial status is Submitted
    assert request.status == WorkflowStatus.SUBMITTED
    
    # 1. Simulated registry verification
    now = time.time()
    request.trigger_identity_verification("Matched", "System", now)
    assert request.identity_status == "Matched"
    assert request.identity_timestamp == now
    assert request.identity_by == "System"
    
    # 2. Officer sets to Under Review
    request.update_status(WorkflowStatus.UNDER_REVIEW, "Officer", now)
    assert request.status == WorkflowStatus.UNDER_REVIEW
    
    # 3. Request Payment
    request.update_payment_status("Pending", 50000.0, now)
    request.update_status(WorkflowStatus.PAYMENT_PENDING, "Officer", now)
    assert request.payment_status == "Pending"
    assert request.status == WorkflowStatus.PAYMENT_PENDING
    
    # 4. Verify Payment
    request.update_payment_status("Verified", 50000.0, now)
    request.update_status(WorkflowStatus.PAYMENT_VERIFIED, "Officer", now)
    assert request.payment_status == "Verified"
    assert request.status == WorkflowStatus.PAYMENT_VERIFIED
    
    # 5. Approve Case
    request.update_status(WorkflowStatus.APPROVED, "Officer", now)
    assert request.status == WorkflowStatus.APPROVED
    
    # 6. Set to Ready for Collection
    request.update_status(WorkflowStatus.READY_FOR_COLLECTION, "Officer", now)
    assert request.status == WorkflowStatus.READY_FOR_COLLECTION
    
    # 7. Close request
    request.update_status(WorkflowStatus.CLOSED, "Officer", now)
    assert request.status == WorkflowStatus.CLOSED
    

def test_invalid_transition_raises_exception():
    """Verifies that out-of-order transitions are blocked."""
    nin = NIN("CF123456789012")
    request = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256780000000",
        location="Ntinda, Kampala",
        description="Lost my ID."
    )
    
    # Attempting to verify payment directly from Submitted must fail
    with pytest.raises(WorkflowTransitionException):
        request.update_status(WorkflowStatus.PAYMENT_VERIFIED, "Officer", time.time())
