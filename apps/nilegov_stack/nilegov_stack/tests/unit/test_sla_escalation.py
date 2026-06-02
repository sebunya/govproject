# Unit Tests for NileGov SLA Rules & Escalation Foundation
# Prototype simulation only. No live Government registry access.

import pytest
import time
from unittest.mock import MagicMock, patch
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus
from nilegov_stack.domain.sla import SLARule, SLAState, EscalationState
from nilegov_stack.application.create_sla_rule import CreateSLARule
from nilegov_stack.application.assign_sla_rule import AssignSLARule
from nilegov_stack.application.evaluate_sla_state import EvaluateSLAState
from nilegov_stack.application.escalate_case import EscalateCase
from nilegov_stack.application.resolve_escalation import ResolveEscalation
from nilegov_stack.application.list_at_risk_requests import ListAtRiskRequests
from nilegov_stack.application.list_overdue_requests import ListOverdueRequests
from nilegov_stack.application.list_escalated_requests import ListEscalatedRequests
from nilegov_stack.infrastructure.repositories.service_request_repository import InMemoryServiceRequestRepository
from nilegov_stack.infrastructure.repositories.sla_rule_repository import InMemorySLARuleRepository
from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository


def test_sla_rule_creation_validation():
    """Verifies that SLA Rules are validated correctly upon creation."""
    repo = InMemorySLARuleRepository()
    creator = CreateSLARule(repo)

    # Valid creation
    rule = creator.execute(
        rule_id="SLA-1",
        service_type="LOST_NATIONAL_ID",
        response_hours=4,
        resolution_hours=48,
        at_risk_threshold_percent=80,
        escalation_threshold_hours=2
    )
    assert rule.rule_id == "SLA-1"
    assert rule.response_hours == 4
    assert rule.resolution_hours == 48

    # Invalid hours
    with pytest.raises(ValueError, match="SLA hours must be positive"):
        creator.execute("SLA-2", "LOST_NATIONAL_ID", response_hours=0, resolution_hours=48)
    with pytest.raises(ValueError, match="SLA hours must be positive"):
        creator.execute("SLA-3", "LOST_NATIONAL_ID", response_hours=4, resolution_hours=-5)

    # Invalid threshold percent
    with pytest.raises(ValueError, match="At Risk Threshold Percent must be between 1 and 100"):
        creator.execute("SLA-4", "LOST_NATIONAL_ID", 4, 48, at_risk_threshold_percent=120)
    with pytest.raises(ValueError, match="At Risk Threshold Percent must be between 1 and 100"):
        creator.execute("SLA-5", "LOST_NATIONAL_ID", 4, 48, at_risk_threshold_percent=0)


def test_sla_rule_assignment():
    """Verifies that assigning a rule correctly computes response and resolution deadlines."""
    nin = NIN("CF900000000000")
    req = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID",
        created_at=100000.0
    )
    rule = SLARule(
        rule_id="SLA-1",
        service_type="LOST_NATIONAL_ID",
        response_hours=4,
        resolution_hours=48
    )

    t = 100000.0
    req.assign_sla_rule(rule, t)

    assert req.sla_rule_id == "SLA-1"
    assert req.response_due_at == t + (4 * 3600)
    assert req.resolution_due_at == t + (48 * 3600)
    assert req.sla_deadline == req.resolution_due_at
    assert req.sla_state == SLAState.WITHIN_SLA

    events = [e for e in req.events if e.__class__.__name__ == "SLARuleAssigned"]
    assert len(events) == 1
    assert events[0].rule_id == "SLA-1"


def test_sla_state_transitions():
    """Verifies the SLA state transitions based on elapsed time percentage."""
    nin = NIN("CF900000000000")
    req = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID",
        created_at=100000.0
    )
    rule = SLARule(
        rule_id="SLA-1",
        service_type="LOST_NATIONAL_ID",
        response_hours=4,
        resolution_hours=48,
        at_risk_threshold_percent=80
    )

    req.assign_sla_rule(rule, 100000.0)
    req.assign_to_officer("officer_demo", 100000.0)

    # 1. 50% elapsed: Within SLA
    # Total resolution duration is 48 hours = 172800 seconds.
    # 50% is 24 hours = 86400 seconds.
    req.evaluate_sla_state(100000.0 + 86400.0, rule)
    assert req.sla_state == SLAState.WITHIN_SLA
    assert req.at_risk_flag is False
    assert req.overdue_flag is False

    # 2. 85% elapsed: At Risk
    # 85% is 40.8 hours = 146880 seconds.
    req.evaluate_sla_state(100000.0 + 146880.0, rule)
    assert req.sla_state == SLAState.AT_RISK
    assert req.at_risk_flag is True
    assert req.overdue_flag is False

    events = [e for e in req.events if e.__class__.__name__ == "RequestMarkedAtRisk"]
    assert len(events) == 1

    # 3. 110% elapsed: Overdue
    # 110% is 52.8 hours = 190080 seconds.
    req.evaluate_sla_state(100000.0 + 190080.0, rule)
    assert req.sla_state == SLAState.OVERDUE
    assert req.at_risk_flag is False
    assert req.overdue_flag is True

    events = [e for e in req.events if e.__class__.__name__ == "RequestMarkedOverdue"]
    assert len(events) == 1

    # 4. Request closed: Met
    req.update_status(WorkflowStatus.UNDER_REVIEW, "officer_demo", 100000.0)
    req.update_status(WorkflowStatus.APPROVED, "officer_demo", 100000.0)
    req.update_status(WorkflowStatus.READY_FOR_COLLECTION, "officer_demo", 100000.0)
    req.update_status(WorkflowStatus.CLOSED, "officer_demo", 100000.0)
    req.evaluate_sla_state(100000.0 + 190080.0, rule)
    assert req.sla_state == SLAState.MET
    assert req.at_risk_flag is False
    assert req.overdue_flag is False


def test_escalation_routing():
    """Verifies that escalation calculations recommend and trigger escalation correctly."""
    nin = NIN("CF900000000000")
    req = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID",
        created_at=100000.0
    )
    rule = SLARule(
        rule_id="SLA-1",
        service_type="LOST_NATIONAL_ID",
        response_hours=4,
        resolution_hours=48,
        escalation_threshold_hours=2
    )

    req.assign_sla_rule(rule, 100000.0)
    req.assign_to_officer("officer_demo", 100000.0)

    # Overdue by 1 hour (less than 2 hour threshold) -> Overdue but not recommended yet
    req.evaluate_sla_state(100000.0 + (49 * 3600), rule)
    assert req.sla_state == SLAState.OVERDUE
    assert req.escalation_state == EscalationState.NOT_ESCALATED

    # Overdue by 3 hours (greater than 2 hour threshold) -> Escalation Recommended
    req.evaluate_sla_state(100000.0 + (51 * 3600), rule)
    assert req.sla_state == SLAState.OVERDUE
    assert req.escalation_state == EscalationState.RECOMMENDED

    events = [e for e in req.events if e.__class__.__name__ == "EscalationRecommended"]
    assert len(events) == 1

    # Official Escalation triggered
    req.escalate_case("supervisor_demo", "SLA resolution breach", 100000.0 + (51 * 3600))
    assert req.escalation_state == EscalationState.ESCALATED
    assert req.escalated_to == "supervisor_demo"
    assert req.escalation_reason == "SLA resolution breach"
    assert req.assignment_status == "Supervisor Review"
    assert req.queue_name == "Supervisor Review Queue"
    assert req.assigned_officer_id == "officer_demo"  # Assigned officer remains intact

    events = [e for e in req.events if e.__class__.__name__ == "RequestEscalated"]
    assert len(events) == 1

    # Resolve escalation
    req.resolve_escalation(100000.0 + (52 * 3600))
    assert req.escalation_state == EscalationState.RESOLVED
    assert req.assignment_status == "Returned to Officer"
    assert req.queue_name == "National ID Replacement Desk"

    events = [e for e in req.events if e.__class__.__name__ == "EscalationResolved"]
    assert len(events) == 1


def test_sla_queries():
    """Verifies queries to list requests matching SLA states and escalations."""
    req_repo = InMemoryServiceRequestRepository()
    rule_repo = InMemorySLARuleRepository()

    nin = NIN("CF900000000000")
    
    # 1. Within SLA Case
    req1 = ServiceRequest("req-1", "REF-001", nin, "A", "1", "Ntinda", "Lost ID", created_at=100.0)
    # 2. At Risk Case
    req2 = ServiceRequest("req-2", "REF-002", nin, "B", "2", "Ntinda", "Lost ID", created_at=100.0)
    # 3. Overdue Case
    req3 = ServiceRequest("req-3", "REF-003", nin, "C", "3", "Ntinda", "Lost ID", created_at=100.0)

    # Assign officer to all to prevent response-time SLA breaches
    req1.assign_to_officer("officer_demo", 100.0)
    req2.assign_to_officer("officer_demo", 100.0)
    req3.assign_to_officer("officer_demo", 100.0)

    req_repo.save(req1)
    req_repo.save(req2)
    req_repo.save(req3)

    rule = SLARule("SLA-1", "LOST_NATIONAL_ID", 4, 48, 80, 2)
    rule_repo.save(rule)

    # Assign SLA to all
    assign_uc = AssignSLARule(req_repo, rule_repo)
    assign_uc.execute("req-1", "SLA-1", 100.0)
    assign_uc.execute("req-2", "SLA-1", 100.0)
    assign_uc.execute("req-3", "SLA-1", 100.0)

    # Evaluate states at different time progressions
    eval_uc = EvaluateSLAState(req_repo, rule_repo)
    
    # req-1 checked at t=101.0 (elapsed < 1 hour)
    eval_uc.execute("req-1", 100.0 + 3600.0)
    
    # req-2 checked at t=42 hours (elapsed 87.5% > 80%)
    eval_uc.execute("req-2", 100.0 + (42 * 3600.0))
    
    # req-3 checked at t=50 hours (elapsed > 48 hours)
    eval_uc.execute("req-3", 100.0 + (50 * 3600.0))

    # Query listings
    list_at_risk = ListAtRiskRequests(req_repo)
    list_overdue = ListOverdueRequests(req_repo)

    assert len(list_at_risk.execute()) == 1
    assert list_at_risk.execute()[0].request_id == "req-2"

    assert len(list_overdue.execute()) == 1
    assert list_overdue.execute()[0].request_id == "req-3"

    # Escalate overdue case
    escalate_uc = EscalateCase(req_repo)
    escalate_uc.execute("req-3", "supervisor_demo", "Workload delay", 100.0 + (51 * 3600.0))

    list_escalated = ListEscalatedRequests(req_repo)
    assert len(list_escalated.execute()) == 1
    assert list_escalated.execute()[0].request_id == "req-3"

    # Resolve escalation
    resolve_uc = ResolveEscalation(req_repo)
    resolve_uc.execute("req-3", 100.0 + (52 * 3600.0))
    assert len(list_escalated.execute()) == 0


@patch("frappe.db.exists")
@patch("frappe.new_doc")
@patch("frappe.get_doc")
def test_frappe_service_request_repository_save_sla_fields(mock_get_doc, mock_new_doc, mock_exists):
    """Verifies that FrappeServiceRequestRepository maps SLA rules and escalation fields correctly on save."""
    mock_exists.return_value = False
    mock_doc = MagicMock()
    mock_new_doc.return_value = mock_doc

    repo = FrappeServiceRequestRepository()
    nin = NIN("CF900000000000")
    req = ServiceRequest("req-1", "NGS-NIRA-2026-0001", nin, "Demo Citizen A", "+256700000001", "Ntinda", "Lost ID", created_at=100.0)

    rule = SLARule("SLA-1", "LOST_NATIONAL_ID", 4, 48, 80, 2)
    req.assign_sla_rule(rule, 100.0)
    req.assign_to_officer("officer_demo", 100.0)
    req.evaluate_sla_state(100.0 + (42 * 3600.0), rule)  # At risk
    req.escalate_case("supervisor_demo", "Workload split", 100.0 + (42 * 3600.0))

    repo.save(req)

    mock_exists.assert_any_call("NileGov Service Request", "req-1")
    assert mock_doc.sla_rule == "SLA-1"
    assert mock_doc.sla_state == SLAState.AT_RISK  # since it was evaluated as At Risk (at 42 hours)
    assert mock_doc.escalation_state == EscalationState.ESCALATED
    assert mock_doc.escalated_to == "supervisor_demo"
    assert mock_doc.escalation_reason == "Workload split"
    assert mock_doc.at_risk_flag == 1  # evaluated as At Risk
    
    mock_doc.save.assert_called_once()
