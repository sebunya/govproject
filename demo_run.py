#!/usr/bin/env python3
# NileGov Stack lost National ID Replacement Service Walkthrough Demo
# Digi-Verse Uganda Limited

import time
import sys
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
    CloseCase,
    CalculateDashboardMetrics,
    VerifyPayment
)


def log_section(title):
    print("\n" + "=" * 80)
    print(f" {title.upper()} ")
    print("=" * 80)


def log_step(step_no, description):
    print(f"\n[Step {step_no}] {description}")
    print("-" * 50)


def run_demo():
    # Setup environments
    repo = InMemoryServiceRequestRepository()
    identity_gateway = SimulatedIdentityVerificationGateway()
    payment_gateway = SimulatedPaymentVerificationGateway()
    notification_gateway = SimulatedNotificationGateway()
    
    log_section("NileGov Stack - Prototype Demo Walkthrough")
    print("Demo Service : Lost National ID Replacement")
    print("Branding     : NileGov Service Experience & Case Operations")
    print("Location     : Ntinda, Kampala")
    print(f"Disclaimer   : {SimulatedIdentityVerificationGateway.DISCLAIMER}")
    
    # ----------------------------------------------------
    log_step(1, "Citizen Reports Lost ID & Submits Replacement Request")
    submit_use_case = SubmitLostNationalIDRequest(repo)
    request_id = "req_nilegov_001"
    reference_no = "NGS-NIRA-2026-0001"
    
    request = submit_use_case.execute(
        request_id=request_id,
        reference_no=reference_no,
        nin_str="CF900000000000",
        citizen_name="Robert Sebunya",
        phone_number="+256780000000",
        location="Ntinda, Kampala",
        description="Lost my wallet containing my national ID near Ntinda market.",
        email="robert.sebunya@example.ug",
        created_at=time.time()
    )
    
    print(f"Request ID       : {request.request_id}")
    print(f"Reference No     : {request.reference_no}")
    print(f"Citizen Name     : {request.citizen_name}")
    print(f"Citizen Location : {request.location}")
    print(f"Service Type     : Lost National ID Replacement")
    print(f"Initial Status   : {request.status}")
    print(f"Payment Status   : {request.payment_status}")
    
    # ----------------------------------------------------
    log_step(2, "Request Appears in Officer Dashboard & Review Initiated")
    review_use_case = StartOfficerReview(repo)
    sla_hours = 24.0
    sla_seconds = sla_hours * 3600.0
    deadline = time.time() + sla_seconds
    
    review_use_case.execute(
        request_id=request_id,
        deadline=deadline,
        actor="officer_sebunya",
        timestamp=time.time()
    )
    request.update_sla_state(time.time())
    
    print(f"Workflow Status  : {request.status}")
    print(f"Assigned Officer : officer_sebunya")
    print(f"SLA Target       : {sla_hours} Hours")
    print(f"SLA Compliance   : {request.sla_status}")
    
    # ----------------------------------------------------
    log_step(3, "Trigger Simulated NIRA Identity Verification")
    print(f"Gateway Label    : Simulated NIRA Identity Verification")
    print(f"Disclaimer Note  : {SimulatedIdentityVerificationGateway.DISCLAIMER}")
    
    identity_use_case = RunSimulatedIdentityCheck(repo, identity_gateway)
    identity_result = identity_use_case.execute(
        request_id=request_id,
        actor="officer_sebunya",
        timestamp=time.time()
    )
    
    print(f"Verification Result    : {request.identity_status}")
    print(f"Verified By            : {request.identity_by}")
    print(f"Verification Timestamp : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.identity_timestamp))}")
    
    # ----------------------------------------------------
    log_step(4, "Officer Requests Payment (Status set to Payment Pending)")
    request.update_payment_status("Pending", 50000.0, time.time())
    request.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_sebunya", time.time())
    
    print(f"Workflow Status  : {request.status}")
    print(f"Payment Status   : {request.payment_status}")
    print(f"Payment Amount   : UGX {request.payment_amount:,.2f}")
    
    # ----------------------------------------------------
    log_step(5, "Simulated Payment Verification Completed")
    print(f"Gateway Label    : Simulated Payment Verification")
    print(f"Disclaimer Note  : {SimulatedPaymentVerificationGateway.DISCLAIMER}")
    
    verify_payment_use_case = VerifyPayment(repo, payment_gateway)
    payment_result = verify_payment_use_case.execute(
        request_id=request_id,
        actor="officer_sebunya",
        timestamp=time.time()
    )
    
    print(f"Verification Result    : {request.payment_status}")
    print(f"Verification Timestamp : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.payment_timestamp))}")
    print(f"Workflow Status        : {request.status}")
    
    # ----------------------------------------------------
    log_step(6, "Case Approved and Ready for Collection")
    close_use_case = CloseCase(repo)
    close_use_case.execute(
        request_id=request_id,
        note="Verified against simulated backup registry. Approved for card reissue.",
        approved=True,
        actor="officer_sebunya",
        timestamp=time.time()
    )
    
    print(f"Workflow Status  : {request.status}")
    print(f"Decision         : {request.decision}")
    print(f"Closure Notes    : {request.closure_notes}")
    
    # ----------------------------------------------------
    log_step(7, "Compliance Audit Trail Record")
    print(f"Audit log status: Immutable simulation records")
    print(f"{'TIMESTAMP':<20} | {'ACTION / EVENT TYPE':<25} | {'SUMMARY / METADATA'}")
    print("-" * 80)
    for event in request.events:
        evt_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.timestamp))
        evt_type = event.__class__.__name__
        
        # Display specific summaries based on event types
        if evt_type == "RequestSubmitted":
            summary = f"Ref: {event.reference_no}, Citizen NIN: {event.citizen_nin}"
        elif evt_type == "IdentityCheckCompleted":
            summary = f"Result: {event.result_status}, Triggered by: {event.actor}"
        elif evt_type == "PaymentStatusChanged":
            summary = f"Status: {event.old_status} -> {event.new_status}, Amount: UGX {event.amount:,.2f}"
        elif evt_type == "StatusChanged":
            summary = f"Workflow: {event.old_status} -> {event.new_status}, Actor: {event.actor}"
        elif evt_type == "NoteAdded":
            summary = f"Note by {event.author}: {event.note_content}"
        elif evt_type == "CaseAssigned":
            summary = f"Assigned SDO: {event.officer_id}"
        else:
            summary = "Audit record commited."
            
        print(f"{evt_time:<20} | {evt_type:<25} | {summary}")
        
    # ----------------------------------------------------
    log_step(8, "Aggregated Leadership Dashboard Metrics Update")
    metrics_use_case = CalculateDashboardMetrics(repo)
    metrics = metrics_use_case.execute([request_id])
    
    for metric_name, val in metrics.items():
        print(f"{metric_name.replace('_', ' ').title():<25} : {val}")
        
    log_section("Demo Completed Successfully")


if __name__ == "__main__":
    run_demo()
