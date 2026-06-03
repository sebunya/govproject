# Service Request Aggregate Root
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

from typing import List, Optional, Dict, Any
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.exceptions import WorkflowTransitionException
from nilegov_stack.domain.sla import SLAState, EscalationState, SLARule
from nilegov_stack.domain.events import (
    DomainEvent, RequestSubmitted, IdentityCheckCompleted,
    CaseAssigned, NoteAdded, PaymentStatusChanged, StatusChanged,
    OfficerAssigned, OfficerReassigned, DepartmentAssigned,
    SupervisorReviewRequested, CaseReturnedToOfficer, AssignmentClosed,
    SLARuleAssigned, SLAStateChanged, RequestMarkedAtRisk, RequestMarkedOverdue,
    EscalationRecommended, RequestEscalated, EscalationResolved
)


class WorkflowStatus:
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    INFORMATION_REQUIRED = "Information Required"
    PAYMENT_PENDING = "Payment Pending"
    PAYMENT_VERIFIED = "Payment Verified"
    APPROVED = "Approved"
    READY_FOR_COLLECTION = "Ready for Collection"
    REJECTED = "Rejected"
    CLOSED = "Closed"


class ServiceRequest:
    """The main Aggregate Root coordinating service delivery workflows."""
    
    def __init__(
        self,
        request_id: str,
        reference_no: str,
        citizen_nin: NIN,
        citizen_name: str,
        phone_number: str,
        location: str,
        description: str,
        email: Optional[str] = None,
        created_at: Optional[float] = None,
        citizen_profile_id: Optional[str] = None
    ):
        self.request_id = request_id
        self.reference_no = reference_no
        self.citizen_nin = citizen_nin
        self.citizen_name = citizen_name
        self.phone_number = phone_number
        self.location = location
        self.description = description
        self.email = email
        self.created_at = created_at or 0.0
        self.updated_at = self.created_at
        self.citizen_profile_id = citizen_profile_id
        self.service_type: Optional[str] = None
        self.service_catalogue_item_id: Optional[str] = None
        
        self.status = WorkflowStatus.SUBMITTED
        self.assigned_officer_id: Optional[str] = None
        self.assigned_supervisor_id: Optional[str] = None
        self.sla_deadline: Optional[float] = None
        self.sla_status = "Within SLA"
        
        # Assignment and Queue Attributes
        self.assigned_department: Optional[str] = None
        self.assigned_team: Optional[str] = None
        self.assignment_status: str = "Unassigned"
        self.assigned_at: Optional[float] = None
        self.reassigned_at: Optional[float] = None
        self.reassignment_reason: Optional[str] = None
        self.supervisor_review_required: bool = False
        self.queue_name: str = "National ID Replacement Desk"
        
        # Simulated Identity Verification Attributes
        self.identity_status = "Requires Review"
        self.identity_timestamp: Optional[float] = None
        self.identity_by: Optional[str] = None
        
        # Simulated Payment Verification Attributes
        self.payment_status = "Not Required"
        self.payment_amount = 0.0
        self.payment_timestamp: Optional[float] = None
        
        # SLA & Escalation Attributes
        self.sla_rule_id: Optional[str] = None
        self.response_due_at: Optional[float] = None
        self.resolution_due_at: Optional[float] = None
        self.sla_state: str = SLAState.NOT_APPLICABLE
        self.sla_last_checked_at: Optional[float] = None
        self.escalation_state: str = EscalationState.NOT_ESCALATED
        self.escalated_at: Optional[float] = None
        self.escalated_to: Optional[str] = None
        self.escalation_reason: Optional[str] = None
        self.at_risk_flag: bool = False
        self.overdue_flag: bool = False
        
        self.closure_notes: Optional[str] = None
        self.decision: Optional[str] = None
        self.notes: List[Dict[str, Any]] = []
        self.events: List[DomainEvent] = []
        
        # Record initial event
        self.record_event(RequestSubmitted(self.request_id, self.reference_no, str(self.citizen_nin)))

    def clear_events(self):
        self.events.clear()

    def record_event(self, event: DomainEvent):
        self.events.append(event)

    def add_note(self, note: str, author: str, timestamp: float):
        """Adds an internal note to the case notes repository."""
        if not note:
            raise ValueError("Note content cannot be empty.")
        self.notes.append({
            "note": note,
            "author": author,
            "timestamp": timestamp
        })
        self.updated_at = timestamp
        self.record_event(NoteAdded(self.request_id, author, note))

    def trigger_identity_verification(self, result: str, actor: str, timestamp: float):
        """Processes simulated NIRA registry checks."""
        if result not in ("Matched", "Not Matched", "Requires Review"):
            raise ValueError(f"Invalid simulated identity verification result: {result}")
        
        self.identity_status = result
        self.identity_timestamp = timestamp
        self.identity_by = actor
        self.updated_at = timestamp
        
        success = (result == "Matched")
        self.record_event(IdentityCheckCompleted(self.request_id, success, f"Simulated NIRA Verification: {result}", actor))

    def update_payment_status(self, status: str, amount: float, timestamp: float):
        """Updates simulated payment verification status."""
        if status not in ("Not Required", "Pending", "Verified", "Failed"):
            raise ValueError(f"Invalid payment status: {status}")
            
        old_status = self.payment_status
        self.payment_status = status
        self.payment_amount = amount
        self.payment_timestamp = timestamp
        self.updated_at = timestamp
        
        self.record_event(PaymentStatusChanged(self.request_id, old_status, status, amount))

    def update_status(self, new_status: str, actor: str, timestamp: float):
        """Transitions request status, checking workflow rules."""
        if new_status not in (
            WorkflowStatus.SUBMITTED,
            WorkflowStatus.UNDER_REVIEW,
            WorkflowStatus.INFORMATION_REQUIRED,
            WorkflowStatus.PAYMENT_PENDING,
            WorkflowStatus.PAYMENT_VERIFIED,
            WorkflowStatus.APPROVED,
            WorkflowStatus.READY_FOR_COLLECTION,
            WorkflowStatus.REJECTED,
            WorkflowStatus.CLOSED
        ):
            raise WorkflowTransitionException(f"Unknown status: {new_status}")
            
        # Terminal state checks
        if self.status in (WorkflowStatus.CLOSED, WorkflowStatus.REJECTED):
            raise WorkflowTransitionException(f"Cannot transition from terminal state: {self.status}")
            
        # Specific transition rule constraints
        if new_status == WorkflowStatus.UNDER_REVIEW:
            if self.status not in (WorkflowStatus.SUBMITTED, WorkflowStatus.INFORMATION_REQUIRED, WorkflowStatus.UNDER_REVIEW):
                raise WorkflowTransitionException(f"Cannot transition to Under Review from {self.status}")
        elif new_status == WorkflowStatus.INFORMATION_REQUIRED:
            if self.status != WorkflowStatus.UNDER_REVIEW:
                raise WorkflowTransitionException("Can only request more information while Under Review.")
        elif new_status == WorkflowStatus.PAYMENT_PENDING:
            if self.status != WorkflowStatus.UNDER_REVIEW:
                raise WorkflowTransitionException("Can only request payment while Under Review.")
        elif new_status == WorkflowStatus.PAYMENT_VERIFIED:
            if self.status != WorkflowStatus.PAYMENT_PENDING:
                raise WorkflowTransitionException("Payment must be pending before verified.")
        elif new_status == WorkflowStatus.APPROVED:
            if self.status not in (WorkflowStatus.UNDER_REVIEW, WorkflowStatus.PAYMENT_VERIFIED):
                raise WorkflowTransitionException("Case must be Under Review or Payment Verified to be Approved.")
        elif new_status == WorkflowStatus.READY_FOR_COLLECTION:
            if self.status not in (WorkflowStatus.APPROVED, WorkflowStatus.PAYMENT_VERIFIED, WorkflowStatus.UNDER_REVIEW):
                raise WorkflowTransitionException("Case must be approved or payment verified to be Ready for Collection.")
        elif new_status == WorkflowStatus.CLOSED:
            if self.status != WorkflowStatus.READY_FOR_COLLECTION:
                raise WorkflowTransitionException("Case must be Ready for Collection to be closed.")
                
        old_status = self.status
        self.status = new_status
        self.updated_at = timestamp
        
        self.record_event(StatusChanged(self.request_id, old_status, new_status, actor))

        # Check if closed
        if new_status in (WorkflowStatus.CLOSED, WorkflowStatus.REJECTED):
            self.sla_state = SLAState.MET
            self.at_risk_flag = False
            self.overdue_flag = False

    def assign_sla_rule(self, rule: SLARule, timestamp: float):
        """Assigns an SLA Rule and calculates response and resolution deadlines."""
        self.sla_rule_id = rule.rule_id
        self.response_due_at = timestamp + (rule.response_hours * 3600)
        self.resolution_due_at = timestamp + (rule.resolution_hours * 3600)
        self.sla_deadline = self.resolution_due_at
        self.sla_state = SLAState.WITHIN_SLA
        self.sla_last_checked_at = timestamp
        self.updated_at = timestamp
        self.record_event(SLARuleAssigned(self.request_id, rule.rule_id, timestamp))

    def evaluate_sla_state(self, current_time: float, rule: Optional[SLARule] = None):
        """Calculates SLA states based on elapsed time relative to deadlines."""
        self.sla_last_checked_at = current_time
        
        # If terminal, it is Met
        if self.status in (WorkflowStatus.CLOSED, WorkflowStatus.REJECTED):
            if self.sla_state != SLAState.MET:
                old_state = self.sla_state
                self.sla_state = SLAState.MET
                self.at_risk_flag = False
                self.overdue_flag = False
                self.record_event(SLAStateChanged(self.request_id, old_state, SLAState.MET, current_time))
            return

        if not self.sla_rule_id:
            self.sla_state = SLAState.NOT_APPLICABLE
            return

        # Check breach
        is_response_breached = (not self.assigned_officer_id) and self.response_due_at and (current_time > self.response_due_at)
        is_resolution_breached = self.resolution_due_at and (current_time > self.resolution_due_at)

        old_state = self.sla_state

        if is_response_breached or is_resolution_breached:
            self.sla_state = SLAState.OVERDUE
            self.overdue_flag = True
            self.at_risk_flag = False
            self.sla_status = "Overdue"
            
            if old_state != SLAState.OVERDUE:
                self.record_event(SLAStateChanged(self.request_id, old_state, SLAState.OVERDUE, current_time))
                self.record_event(RequestMarkedOverdue(self.request_id, current_time))
            
            # Check escalation threshold
            if rule and self.escalation_state == EscalationState.NOT_ESCALATED:
                due_time = self.resolution_due_at or self.response_due_at or 0.0
                if current_time > due_time + (rule.escalation_threshold_hours * 3600):
                    self.escalation_state = EscalationState.RECOMMENDED
                    self.record_event(EscalationRecommended(self.request_id, current_time))
        else:
            # Check At Risk threshold
            if rule and self.resolution_due_at and self.created_at:
                total_allowed = self.resolution_due_at - self.created_at
                elapsed = current_time - self.created_at
                if total_allowed > 0:
                    pct = (elapsed / total_allowed) * 100
                    if pct >= rule.at_risk_threshold_percent:
                        self.sla_state = SLAState.AT_RISK
                        self.at_risk_flag = True
                        self.overdue_flag = False
                        self.sla_status = "Within SLA"
                        if old_state != SLAState.AT_RISK:
                            self.record_event(SLAStateChanged(self.request_id, old_state, SLAState.AT_RISK, current_time))
                            self.record_event(RequestMarkedAtRisk(self.request_id, current_time))
                        return

            self.sla_state = SLAState.WITHIN_SLA
            self.at_risk_flag = False
            self.overdue_flag = False
            self.sla_status = "Within SLA"
            if old_state != SLAState.WITHIN_SLA and old_state != SLAState.NOT_APPLICABLE:
                self.record_event(SLAStateChanged(self.request_id, old_state, SLAState.WITHIN_SLA, current_time))

    def escalate_case(self, supervisor_id: str, reason: str, timestamp: float):
        """Escalates the case to supervisor review."""
        self.escalation_state = EscalationState.ESCALATED
        self.escalated_at = timestamp
        self.escalated_to = supervisor_id
        self.escalation_reason = reason
        self.assignment_status = "Supervisor Review"
        self.queue_name = "Supervisor Review Queue"
        self.supervisor_review_required = True
        self.updated_at = timestamp
        self.record_event(RequestEscalated(self.request_id, supervisor_id, reason, timestamp))

    def resolve_escalation(self, timestamp: float):
        """Resolves the active escalation and returns it to officer queue."""
        self.escalation_state = EscalationState.RESOLVED
        self.supervisor_review_required = False
        self.assignment_status = "Returned to Officer"
        self.queue_name = "National ID Replacement Desk"
        self.updated_at = timestamp
        self.record_event(EscalationResolved(self.request_id, timestamp))

    def update_sla_state(self, current_time: float):
        """Deprecated legacy compatibility method, falls back to evaluate_sla_state."""
        self.evaluate_sla_state(current_time)

    def assign_officer(self, officer_id: str):
        """Deprecated simple assignment method; calls assign_to_officer with current time."""
        import time
        self.assign_to_officer(officer_id, time.time())

    def assign_to_officer(self, officer_id: str, timestamp: float):
        """Assigns the request to a specific officer and updates assignment status."""
        self.assigned_officer_id = officer_id
        self.assignment_status = "Assigned"
        self.assigned_at = timestamp
        self.queue_name = "National ID Replacement Desk"
        self.record_event(OfficerAssigned(self.request_id, officer_id, timestamp))

    def reassign_to_officer(self, new_officer_id: str, reason: str, timestamp: float):
        """Reassigns the request to a different officer, documenting the reason."""
        old_officer = self.assigned_officer_id or ""
        self.assigned_officer_id = new_officer_id
        self.assignment_status = "Reassigned"
        self.reassigned_at = timestamp
        self.reassignment_reason = reason
        self.record_event(OfficerReassigned(self.request_id, old_officer, new_officer_id, reason, timestamp))

    def assign_to_department(self, department: str, team: Optional[str], timestamp: float):
        """Assigns the request to a department/team queue."""
        self.assigned_department = department
        self.assigned_team = team
        self.queue_name = department
        self.record_event(DepartmentAssigned(self.request_id, department, team or "", timestamp))

    def mark_supervisor_review(self, supervisor_id: str, timestamp: float):
        """Routes the request for supervisor review."""
        self.assigned_supervisor_id = supervisor_id
        self.supervisor_review_required = True
        self.assignment_status = "Supervisor Review"
        self.queue_name = "Supervisor Review Queue"
        self.record_event(SupervisorReviewRequested(self.request_id, supervisor_id, timestamp))

    def return_to_officer(self, timestamp: float):
        """Returns the case from supervisor review to the assigned officer."""
        if not self.assigned_officer_id:
            raise ValueError("No assigned officer to return the case to.")
        self.supervisor_review_required = False
        self.assignment_status = "Returned to Officer"
        self.queue_name = "National ID Replacement Desk"
        self.record_event(CaseReturnedToOfficer(self.request_id, self.assigned_officer_id, timestamp))

    def close_assignment(self, timestamp: float):
        """Closes assignment routing for the request."""
        self.assignment_status = "Closed"
        self.queue_name = "Completed Cases Queue"
        self.record_event(AssignmentClosed(self.request_id, timestamp))
