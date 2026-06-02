# Pass 2 End-to-End Integration Demo Test
# Digi-Verse Uganda Limited

import pytest
import time
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.service_request import WorkflowStatus
from nilegov_stack.infrastructure.repositories import InMemoryServiceRequestRepository
from nilegov_stack.infrastructure.integrations import (
    SimulatedIdentityVerificationGateway,
    SimulatedPaymentVerificationGateway
)
from nilegov_stack.infrastructure.notifications import SimulatedNotificationGateway
from nilegov_stack.application import (
    SubmitLostNationalIDRequest,
    RunSimulatedIdentityCheck,
    StartOfficerReview,
    RequestMoreInformation,
    EscalateCase,
    SupervisorReview,
    CloseCase,
    CalculateDashboardMetrics,
    VerifyPayment
)


def test_pass2_lost_id_replacement_demo_flow():
    """Validates the exact Pass 2 end-to-end lost National ID replacement demo scenario."""
    # 1. Setup ports, repositories, gateways
    repo = InMemoryServiceRequestRepository()
    identity_gateway = SimulatedIdentityVerificationGateway()
    payment_gateway = SimulatedPaymentVerificationGateway()
    notification_gateway = SimulatedNotificationGateway()
    
    # 2. Intake: Citizen in Ntinda, Kampala reports lost National ID
    # Citizen: Demo Citizen A, NIN: CF900000000000
    submit_use_case = SubmitLostNationalIDRequest(repo)
    request_id = "req_demo_001"
    reference_no = "NGS-NIRA-2026-0001"
    
    request = submit_use_case.execute(
        request_id=request_id,
        reference_no=reference_no,
        nin_str="CF900000000000",
        citizen_name="Demo Citizen A",
        phone_number="+256780000000",
        location="Ntinda, Kampala",
        description="Lost my National ID on a boda boda in Ntinda.",
        email="demo.citizen.a@example.test",
        created_at=time.time()
    )
    
    # Verify Citizen request record has correct fields and is 'Submitted'
    assert request.request_id == request_id
    assert request.reference_no == reference_no
    assert request.location == "Ntinda, Kampala"
    assert request.status == WorkflowStatus.SUBMITTED
    assert request.identity_status == "Requires Review"
    assert request.payment_status == "Not Required"
    
    # Check that initial audit event is recorded
    assert len(request.events) == 1
    assert request.events[0].__class__.__name__ == "RequestSubmitted"
    
    # 3. Request appears in officer dashboard.
    # Officer desk review starts. Trigger simulated NIRA identity check.
    review_use_case = StartOfficerReview(repo)
    review_use_case.execute(
        request_id=request_id,
        deadline=time.time() + 86400.0, # 24 hours SLA
        actor="officer_demo",
        timestamp=time.time()
    )
    
    # Status changes to Under Review
    assert request.status == WorkflowStatus.UNDER_REVIEW
    
    # Trigger Simulated NIRA Identity Verification
    identity_use_case = RunSimulatedIdentityCheck(repo, identity_gateway)
    identity_result = identity_use_case.execute(
        request_id=request_id,
        actor="officer_demo",
        timestamp=time.time()
    )
    
    assert identity_result == "Matched"
    assert request.identity_status == "Matched"
    assert request.identity_by == "officer_demo"
    
    # 4. Payment status is set to Payment Pending
    request.update_payment_status("Pending", 50000.0, time.time())
    request.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_demo", time.time())
    assert request.payment_status == "Pending"
    assert request.status == WorkflowStatus.PAYMENT_PENDING
    
    # 5. Simulated payment verification is completed
    verify_payment_use_case = VerifyPayment(repo, payment_gateway)
    payment_result = verify_payment_use_case.execute(
        request_id=request_id,
        actor="officer_demo",
        timestamp=time.time()
    )
    
    assert payment_result == "Verified"
    assert request.payment_status == "Verified"
    # Verify payment use case automatically transitions status to PAYMENT_VERIFIED
    assert request.status == WorkflowStatus.PAYMENT_VERIFIED
    
    # 6. Case is approved and Ready for Collection
    close_use_case = CloseCase(repo)
    close_use_case.execute(
        request_id=request_id,
        note="Verified against simulated backup registry. Approved for card reissue.",
        approved=True,
        actor="officer_demo",
        timestamp=time.time()
    )
    
    # Request should move to terminal status Closed
    assert request.status == WorkflowStatus.CLOSED
    assert request.decision == "Approved"
    assert request.closure_notes == "Verified against simulated backup registry. Approved for card reissue."
    
    # 7. Audit trail records all key actions
    # We should have events for: RequestSubmitted, StatusChanged (Under Review, Payment Pending, Payment Verified, Approved, Ready for Collection, Closed), IdentityCheckCompleted, PaymentStatusChanged.
    event_names = [e.__class__.__name__ for e in request.events]
    assert "RequestSubmitted" in event_names
    assert "IdentityCheckCompleted" in event_names
    assert "PaymentStatusChanged" in event_names
    assert "StatusChanged" in event_names
    
    # 8. Dashboard updates service performance metrics
    metrics_use_case = CalculateDashboardMetrics(repo)
    metrics = metrics_use_case.execute([request_id])
    
    assert metrics["total_requests"] == 1
    assert metrics["closed"] == 1
    assert metrics["overdue"] == 0
    assert metrics["submitted"] == 0
    assert metrics["under_review"] == 0
