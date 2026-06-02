# Unit Test for Frappe Service Request Repository
# Prototype simulation only. No live Government registry access.

import pytest
from unittest.mock import MagicMock, patch
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus
from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository


@patch("frappe.db.exists")
@patch("frappe.new_doc")
@patch("frappe.get_doc")
def test_frappe_repository_save_new(mock_get_doc, mock_new_doc, mock_exists):
    """Verifies repository save maps domain state to new Frappe document correctly."""
    mock_exists.return_value = False
    mock_doc = MagicMock()
    mock_new_doc.return_value = mock_doc
    
    repo = FrappeServiceRequestRepository()
    
    nin = NIN("CF900000000000")
    request = ServiceRequest(
        request_id="req_001",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256780000000",
        location="Ntinda, Kampala",
        description="Lost ID."
    )
    
    repo.save(request)
    
    # Assert exists was called with our service request ID
    exists_calls = [args[0] for args in mock_exists.call_args_list]
    assert ("NileGov Service Request", "req_001") in exists_calls
    
    # Assert new_doc was called for NileGov Service Request and NileGov Audit Event
    new_doc_types = [c[0][0] for c in mock_new_doc.call_args_list]
    assert "NileGov Service Request" in new_doc_types
    assert "NileGov Audit Event" in new_doc_types

    
    assert mock_doc.reference_no == "NGS-NIRA-2026-0001"
    assert mock_doc.citizen_full_name == "Demo Citizen A"
    assert mock_doc.nin == "CF900000000000"
    assert mock_doc.location == "Ntinda, Kampala"
    assert mock_doc.internal_status == WorkflowStatus.SUBMITTED
    mock_doc.save.assert_called_once()



@patch("frappe.db.exists")
@patch("frappe.get_doc")
def test_frappe_repository_get_by_id(mock_get_doc, mock_exists):
    """Verifies repository get maps Frappe document fields to domain aggregate."""
    mock_exists.return_value = True
    
    mock_doc = MagicMock()
    mock_doc.service_request_id = "req_001"
    mock_doc.reference_no = "NGS-NIRA-2026-0001"
    mock_doc.nin = "CF900000000000"
    mock_doc.citizen_full_name = "Demo Citizen A"
    mock_doc.phone = "+256780000000"
    mock_doc.location = "Ntinda, Kampala"
    mock_doc.reason_for_request = "Lost ID."
    mock_doc.internal_status = "Submitted"
    mock_doc.payment_status = "Not Required"
    mock_doc.payment_timestamp = None
    mock_doc.identity_status = "Requires Review"
    mock_doc.identity_timestamp = None
    mock_doc.identity_by = None
    mock_doc.assigned_officer = "officer_demo"
    mock_doc.assigned_supervisor = None
    mock_doc.sla_deadline = None
    
    mock_get_doc.return_value = mock_doc
    
    repo = FrappeServiceRequestRepository()
    request = repo.get_by_id("req_001")
    
    assert request is not None
    assert request.request_id == "req_001"
    assert request.reference_no == "NGS-NIRA-2026-0001"
    assert str(request.citizen_nin) == "CF900000000000"
    assert request.citizen_name == "Demo Citizen A"
    assert request.status == WorkflowStatus.SUBMITTED
