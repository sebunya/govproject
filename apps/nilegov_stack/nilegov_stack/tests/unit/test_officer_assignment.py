# Unit Tests for NileGov Officer Assignment & Department Queues
# Prototype simulation only. No live Government registry access.

import pytest
import time
from unittest.mock import MagicMock, patch
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.application.assign_officer import AssignOfficer
from nilegov_stack.application.reassign_officer import ReassignOfficer
from nilegov_stack.application.assign_department_team import AssignDepartmentTeam
from nilegov_stack.application.mark_supervisor_review import MarkSupervisorReview
from nilegov_stack.application.return_case_to_officer import ReturnCaseToOfficer
from nilegov_stack.application.list_unassigned_requests import ListUnassignedRequests
from nilegov_stack.application.list_requests_by_officer import ListRequestsByOfficer
from nilegov_stack.application.list_requests_by_department import ListRequestsByDepartment
from nilegov_stack.application.list_supervisor_review_queue import ListSupervisorReviewQueue
from nilegov_stack.application.calculate_workload_metrics import CalculateWorkloadMetrics
from nilegov_stack.infrastructure.repositories.service_request_repository import InMemoryServiceRequestRepository
from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository


def test_service_request_initial_assignment_state():
    """Verifies that a new Service Request is unassigned by default."""
    nin = NIN("CF900000000000")
    req = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID"
    )

    assert req.assigned_officer_id is None
    assert req.assigned_supervisor_id is None
    assert req.assignment_status == "Unassigned"
    assert req.queue_name == "National ID Replacement Desk"
    assert req.assigned_department is None
    assert req.assigned_team is None
    assert req.supervisor_review_required is False


def test_assign_to_officer():
    """Verifies that assigning to an officer updates status and logs event."""
    nin = NIN("CF900000000000")
    req = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID"
    )

    assign_time = 1700000000.0
    req.assign_to_officer("officer_demo", assign_time)

    assert req.assigned_officer_id == "officer_demo"
    assert req.assignment_status == "Assigned"
    assert req.assigned_at == assign_time
    assert req.queue_name == "National ID Replacement Desk"
    
    # Event verification
    events = [e for e in req.events if e.__class__.__name__ == "OfficerAssigned"]
    assert len(events) == 1
    assert events[0].officer_id == "officer_demo"
    assert events[0].assigned_at == assign_time


def test_reassign_officer():
    """Verifies reassignment updates officer, reason, and status."""
    nin = NIN("CF900000000000")
    req = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID"
    )

    req.assign_to_officer("officer_demo", 1700000000.0)
    reassign_time = 1700000100.0
    req.reassign_to_officer("officer_review", "Workload split", reassign_time)

    assert req.assigned_officer_id == "officer_review"
    assert req.assignment_status == "Reassigned"
    assert req.reassigned_at == reassign_time
    assert req.reassignment_reason == "Workload split"

    events = [e for e in req.events if e.__class__.__name__ == "OfficerReassigned"]
    assert len(events) == 1
    assert events[0].old_officer_id == "officer_demo"
    assert events[0].new_officer_id == "officer_review"
    assert events[0].reason == "Workload split"


def test_assign_to_department():
    """Verifies that routing to department changes department and queue fields."""
    nin = NIN("CF900000000000")
    req = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID"
    )

    req.assign_to_department("Verification Desk", "Team Alpha", 1700000000.0)
    assert req.assigned_department == "Verification Desk"
    assert req.assigned_team == "Team Alpha"
    assert req.queue_name == "Verification Desk"

    events = [e for e in req.events if e.__class__.__name__ == "DepartmentAssigned"]
    assert len(events) == 1
    assert events[0].department == "Verification Desk"
    assert events[0].team == "Team Alpha"


def test_mark_supervisor_review_and_return():
    """Verifies supervisor escalation and return workflow."""
    nin = NIN("CF900000000000")
    req = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID"
    )

    req.assign_to_officer("officer_demo", 1700000000.0)
    req.mark_supervisor_review("supervisor_demo", 1700000100.0)

    assert req.assigned_supervisor_id == "supervisor_demo"
    assert req.supervisor_review_required is True
    assert req.assignment_status == "Supervisor Review"
    assert req.queue_name == "Supervisor Review Queue"

    # Return to officer
    req.return_to_officer(1700000200.0)
    assert req.supervisor_review_required is False
    assert req.assignment_status == "Returned to Officer"
    assert req.queue_name == "National ID Replacement Desk"

    # Return without officer raises value error
    req.assigned_officer_id = None
    with pytest.raises(ValueError, match="No assigned officer"):
        req.return_to_officer(1700000300.0)


def test_close_assignment():
    """Verifies that closing assignment archives it in the Completed queue."""
    nin = NIN("CF900000000000")
    req = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256700000001",
        location="Ntinda, Kampala",
        description="Lost ID"
    )

    req.close_assignment(1700000000.0)
    assert req.assignment_status == "Closed"
    assert req.queue_name == "Completed Cases Queue"


def test_use_cases_and_workload_metrics():
    """Verifies assignment use cases and workload counter metrics."""
    repo = InMemoryServiceRequestRepository()

    # Seed requests
    nin = NIN("CF900000000000")
    req1 = ServiceRequest("req-1", "NGS-NIRA-2026-0001", nin, "Demo Citizen A", "+256700000001", "Ntinda", "Lost ID")
    req2 = ServiceRequest("req-2", "NGS-NIRA-2026-0002", nin, "Demo Citizen B", "+256700000002", "Ntinda", "Lost ID")
    
    repo.save(req1)
    repo.save(req2)

    # Use Case: Assign Officer
    assign_uc = AssignOfficer(repo)
    assign_uc.execute("req-1", "officer_demo", 1700000000.0)
    assert repo.get_by_id("req-1").assigned_officer_id == "officer_demo"

    # Use Case: Reassign Officer
    reassign_uc = ReassignOfficer(repo)
    reassign_uc.execute("req-1", "officer_review", "Work overload", 1700000100.0)
    assert repo.get_by_id("req-1").assigned_officer_id == "officer_review"

    # Use Case: Assign Dept
    dept_uc = AssignDepartmentTeam(repo)
    dept_uc.execute("req-2", "Verification Desk", "Team Alpha", 1700000000.0)
    assert repo.get_by_id("req-2").assigned_department == "Verification Desk"

    # Use Case: List Unassigned
    list_unassigned = ListUnassignedRequests(repo)
    unassigned = list_unassigned.execute()
    # req-2 has department assigned, but no officer, so it's unassigned
    assert len(unassigned) == 1
    assert unassigned[0].request_id == "req-2"

    # Use Case: List by Officer
    list_officer = ListRequestsByOfficer(repo)
    assert len(list_officer.execute("officer_review")) == 1
    assert len(list_officer.execute("officer_demo")) == 0

    # Use Case: List by Department
    list_dept = ListRequestsByDepartment(repo)
    assert len(list_dept.execute("Verification Desk")) == 1

    # Use Case: Supervisor escalation
    sup_uc = MarkSupervisorReview(repo)
    sup_uc.execute("req-1", "supervisor_demo", 1700000200.0)
    
    list_sup = ListSupervisorReviewQueue(repo)
    assert len(list_sup.execute()) == 1

    return_uc = ReturnCaseToOfficer(repo)
    return_uc.execute("req-1", 1700000300.0)
    assert len(list_sup.execute()) == 0

    # Workload Metrics Use Case
    metrics_uc = CalculateWorkloadMetrics(repo)
    metrics = metrics_uc.execute()

    assert metrics["total_cases"] == 2
    assert metrics["unassigned_cases"] == 1 # req-2 is unassigned (no officer)
    assert metrics["assigned_cases"] == 1 # req-1 is assigned (officer_review)
    assert metrics["officer_workloads"]["officer_review"] == 1
    assert metrics["department_queues"]["Verification Desk"] == 1


@patch("frappe.db.exists")
@patch("frappe.new_doc")
@patch("frappe.get_doc")
def test_frappe_service_request_repository_save_assignment(mock_get_doc, mock_new_doc, mock_exists):
    """Verifies FrappeServiceRequestRepository maps assignment domain fields to Frappe document."""
    mock_exists.return_value = False
    mock_doc = MagicMock()
    mock_new_doc.return_value = mock_doc

    repo = FrappeServiceRequestRepository()
    nin = NIN("CF900000000000")
    req = ServiceRequest("req-1", "NGS-NIRA-2026-0001", nin, "Demo Citizen A", "+256700000001", "Ntinda", "Lost ID")
    
    req.assign_to_officer("officer_demo", 1700000000.0)
    req.assign_to_department("Verification Desk", "Team Alpha", 1700000000.0)
    req.mark_supervisor_review("supervisor_demo", 1700000100.0)

    repo.save(req)

    mock_exists.assert_any_call("NileGov Service Request", "req-1")
    assert mock_doc.assigned_officer == "officer_demo"
    assert mock_doc.assigned_supervisor == "supervisor_demo"
    assert mock_doc.assigned_department == "Verification Desk"
    assert mock_doc.assigned_team == "Team Alpha"
    assert mock_doc.assignment_status == "Supervisor Review"
    assert mock_doc.queue_name == "Supervisor Review Queue"
    assert mock_doc.supervisor_review_required == 1
    
    mock_doc.save.assert_called_once()
