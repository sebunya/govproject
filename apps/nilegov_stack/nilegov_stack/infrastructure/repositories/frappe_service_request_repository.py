# Frappe-based Service Request Repository
# Prototype simulation only. No live Government registry access.

try:
    import frappe
except ImportError:
    frappe = None

from typing import Optional, List
from nilegov_stack.application.ports import ServiceRequestRepository
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.domain.value_objects import NIN


class FrappeServiceRequestRepository(ServiceRequestRepository):
    """Frappe-based repository for persisting and loading Service Request aggregates."""
    
    def _check_frappe(self):
        if not frappe:
            raise ImportError("Frappe framework is not loaded in this environment.")

    def save(self, service_request: ServiceRequest) -> None:
        self._check_frappe()
        # Load or create frappe document
        if frappe.db.exists("NileGov Service Request", service_request.request_id):
            doc = frappe.get_doc("NileGov Service Request", service_request.request_id)
        else:
            doc = frappe.new_doc("NileGov Service Request")
            doc.service_request_id = service_request.request_id
            
        doc.reference_no = service_request.reference_no
        doc.citizen_profile = service_request.citizen_profile_id
        doc.citizen_full_name = service_request.citizen_name
        doc.nin = str(service_request.citizen_nin)
        doc.phone = service_request.phone_number
        doc.email = service_request.email
        doc.location = service_request.location
        doc.reason_for_request = service_request.description
        doc.internal_status = service_request.status
        doc.citizen_visible_status = service_request.status
        
        doc.payment_status = service_request.payment_status
        doc.payment_amount = service_request.payment_amount
        doc.payment_timestamp = service_request.payment_timestamp
        
        doc.identity_status = service_request.identity_status
        doc.identity_timestamp = service_request.identity_timestamp
        doc.identity_by = service_request.identity_by
        
        doc.assigned_officer = service_request.assigned_officer_id
        doc.assigned_supervisor = service_request.assigned_supervisor_id
        doc.sla_deadline = service_request.sla_deadline
        
        # Assignment Fields Mapping
        doc.assigned_department = service_request.assigned_department
        doc.assigned_team = service_request.assigned_team
        doc.assignment_status = service_request.assignment_status
        doc.queue_name = service_request.queue_name
        doc.supervisor_review_required = 1 if service_request.supervisor_review_required else 0
        doc.reassignment_reason = service_request.reassignment_reason
        
        if service_request.assigned_at:
            doc.assigned_at = frappe.utils.get_datetime(service_request.assigned_at)
        if service_request.reassigned_at:
            doc.reassigned_at = frappe.utils.get_datetime(service_request.reassigned_at)
            
        # SLA & Escalation Fields Mapping
        doc.sla_rule = service_request.sla_rule_id
        doc.sla_state = service_request.sla_state
        doc.escalation_state = service_request.escalation_state
        doc.escalated_to = service_request.escalated_to
        doc.escalation_reason = service_request.escalation_reason
        doc.at_risk_flag = 1 if service_request.at_risk_flag else 0
        doc.overdue_flag = 1 if service_request.overdue_flag else 0
        
        if service_request.response_due_at:
            doc.response_due_at = frappe.utils.get_datetime(service_request.response_due_at)
        if service_request.resolution_due_at:
            doc.resolution_due_at = frappe.utils.get_datetime(service_request.resolution_due_at)
        if service_request.sla_last_checked_at:
            doc.sla_last_checked_at = frappe.utils.get_datetime(service_request.sla_last_checked_at)
        if service_request.escalated_at:
            doc.escalated_at = frappe.utils.get_datetime(service_request.escalated_at)
        
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        # Save audit logs
        # Map domain events to NileGov Audit Event DocType
        for event in service_request.events:
            self._save_event(service_request.request_id, event)
            
        service_request.clear_events()

    def _save_event(self, request_id: str, event) -> None:
        self._check_frappe()
        evt_type = event.__class__.__name__
        audit_doc = frappe.new_doc("NileGov Audit Event")
        audit_doc.service_request = request_id
        audit_doc.event_type = evt_type
        audit_doc.actor = getattr(event, "actor", "System")
        # Ensure standard link target fallback
        if not frappe.db.exists("User", audit_doc.actor):
            audit_doc.actor = "Administrator"
            
        audit_doc.event_time = frappe.utils.get_datetime(event.timestamp)
        
        # Define action summary
        if evt_type == "RequestSubmitted":
            summary = f"Ref: {event.reference_no}, Citizen NIN: {event.citizen_nin}"
        elif evt_type == "IdentityCheckCompleted":
            summary = f"Result: {event.result_status}, Triggered by: {event.actor}"
        elif evt_type == "PaymentStatusChanged":
            summary = f"Status: {event.old_status} -> {event.new_status}, Amount: UGX {event.amount:,.2f}"
        elif evt_type == "StatusChanged":
            summary = f"Workflow: {event.old_status} -> {event.new_status}, Actor: {event.actor}"
            audit_doc.previous_status = event.old_status
            audit_doc.new_status = event.new_status
        elif evt_type == "NoteAdded":
            summary = f"Note by {event.author}: {event.note_content}"
        elif evt_type == "CaseAssigned":
            summary = f"Assigned SDO: {event.officer_id}"
        elif evt_type == "OfficerAssigned":
            summary = f"Officer Assigned: {event.officer_id} at {event.assigned_at}"
        elif evt_type == "OfficerReassigned":
            summary = f"Reassigned: {event.old_officer_id} -> {event.new_officer_id}, Reason: {event.reason}"
        elif evt_type == "DepartmentAssigned":
            summary = f"Department Queue: {event.department}, Team: {event.team}"
        elif evt_type == "SupervisorReviewRequested":
            summary = f"Supervisor Review Requested: {event.supervisor_id}"
        elif evt_type == "CaseReturnedToOfficer":
            summary = f"Returned to SDO: {event.officer_id}"
        elif evt_type == "AssignmentClosed":
            summary = "Assignment Closed and Archived"
        elif evt_type == "SLARuleAssigned":
            summary = f"SLA Rule Assigned: {event.rule_id}"
        elif evt_type == "SLAStateChanged":
            summary = f"SLA State: {event.old_state} -> {event.new_state}"
        elif evt_type == "RequestMarkedAtRisk":
            summary = "SLA Alert: Request is At Risk"
        elif evt_type == "RequestMarkedOverdue":
            summary = "SLA Alert: Request is Overdue"
        elif evt_type == "EscalationRecommended":
            summary = "Escalation Recommended (threshold exceeded)"
        elif evt_type == "RequestEscalated":
            summary = f"Escalated to: {event.supervisor_id}, Reason: {event.reason}"
        elif evt_type == "EscalationResolved":
            summary = "Escalation Resolved"
        else:
            summary = "Action recorded in compliance log."
            
        audit_doc.action_summary = summary
        audit_doc.insert(ignore_permissions=True)
        frappe.db.commit()

    def get_by_id(self, request_id: str) -> Optional[ServiceRequest]:
        self._check_frappe()
        if not frappe.db.exists("NileGov Service Request", request_id):
            return None
        doc = frappe.get_doc("NileGov Service Request", request_id)
        
        # Map doc to domain ServiceRequest
        nin = NIN(doc.nin)
        req = ServiceRequest(
            request_id=doc.service_request_id,
            reference_no=doc.reference_no,
            citizen_nin=nin,
            citizen_name=doc.citizen_full_name,
            phone_number=doc.phone,
            location=doc.location,
            description=doc.reason_for_request,
            email=doc.email,
            created_at=frappe.utils.get_timestamp(doc.creation),
            citizen_profile_id=doc.citizen_profile
        )
        
        req.status = doc.internal_status
        req.payment_status = doc.payment_status
        req.payment_amount = doc.payment_amount
        req.payment_timestamp = frappe.utils.get_timestamp(doc.payment_timestamp) if doc.payment_timestamp else None
        
        req.identity_status = doc.identity_status
        req.identity_timestamp = frappe.utils.get_timestamp(doc.identity_timestamp) if doc.identity_timestamp else None
        req.identity_by = doc.identity_by
        
        req.assigned_officer_id = doc.assigned_officer
        req.assigned_supervisor_id = doc.assigned_supervisor
        req.sla_deadline = frappe.utils.get_timestamp(doc.sla_deadline) if doc.sla_deadline else None
        
        # Assignment Fields Mapping
        req.assigned_department = doc.assigned_department
        req.assigned_team = doc.assigned_team
        req.assignment_status = doc.assignment_status or "Unassigned"
        req.queue_name = doc.queue_name or "National ID Replacement Desk"
        req.supervisor_review_required = True if doc.supervisor_review_required else False
        req.reassignment_reason = doc.reassignment_reason
        req.assigned_at = frappe.utils.get_timestamp(doc.assigned_at) if doc.assigned_at else None
        req.reassigned_at = frappe.utils.get_timestamp(doc.reassigned_at) if doc.reassigned_at else None
        
        # SLA & Escalation Fields Mapping
        req.sla_rule_id = doc.sla_rule
        req.sla_state = doc.sla_state or "Not Applicable"
        req.escalation_state = doc.escalation_state or "Not Escalated"
        req.escalated_to = doc.escalated_to
        req.escalation_reason = doc.escalation_reason
        req.at_risk_flag = True if doc.at_risk_flag else False
        req.overdue_flag = True if doc.overdue_flag else False
        
        req.response_due_at = frappe.utils.get_timestamp(doc.response_due_at) if doc.response_due_at else None
        req.resolution_due_at = frappe.utils.get_timestamp(doc.resolution_due_at) if doc.resolution_due_at else None
        req.sla_last_checked_at = frappe.utils.get_timestamp(doc.sla_last_checked_at) if doc.sla_last_checked_at else None
        req.escalated_at = frappe.utils.get_timestamp(doc.escalated_at) if doc.escalated_at else None
        
        req.clear_events()
        return req

    def get_by_reference(self, reference_no: str) -> Optional[ServiceRequest]:
        self._check_frappe()
        request_id = frappe.db.get_value("NileGov Service Request", {"reference_no": reference_no}, "name")
        if not request_id:
            return None
        return self.get_by_id(request_id)

    def get_by_citizen_profile(self, profile_id: str) -> List[ServiceRequest]:
        self._check_frappe()
        request_ids = frappe.get_all(
            "NileGov Service Request",
            filters={"citizen_profile": profile_id},
            pluck="name"
        )
        results = []
        for rid in request_ids:
            req = self.get_by_id(rid)
            if req:
                results.append(req)
        return results

    def get_all(self) -> List[ServiceRequest]:
        self._check_frappe()
        request_ids = frappe.get_all("NileGov Service Request", pluck="name")
        results = []
        for rid in request_ids:
            req = self.get_by_id(rid)
            if req:
                results.append(req)
        return results
