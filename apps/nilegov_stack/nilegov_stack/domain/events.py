# Domain Events for NileGov Stack
# Digi-Verse Uganda Limited

import time
from typing import Dict, Any


class DomainEvent:
    """Base class for all domain events."""
    def __init__(self):
        self.timestamp = time.time()


class RequestSubmitted(DomainEvent):
    """Fired when a citizen submits a new Service Request."""
    def __init__(self, request_id: str, reference_no: str, citizen_nin: str):
        super().__init__()
        self.request_id = request_id
        self.reference_no = reference_no
        self.citizen_nin = citizen_nin


class ConsentCaptured(DomainEvent):
    """Fired when legal consent is verified for a Service Request."""
    def __init__(self, request_id: str, verified_at: float):
        super().__init__()
        self.request_id = request_id
        self.verified_at = verified_at


class IdentityCheckCompleted(DomainEvent):
    """Fired when the simulated NIRA identity check is logged."""
    def __init__(self, request_id: str, verified: bool, result_status: str, actor: str = "System"):
        super().__init__()
        self.request_id = request_id
        self.verified = verified
        self.result_status = result_status
        self.actor = actor


class CaseAssigned(DomainEvent):
    """Fired when a request is assigned to an officer."""
    def __init__(self, request_id: str, officer_id: str):
        super().__init__()
        self.request_id = request_id
        self.officer_id = officer_id


class SLABreached(DomainEvent):
    """Fired when an active workflow step SLA breaches."""
    def __init__(self, request_id: str, step: str, deadline: float):
        super().__init__()
        self.request_id = request_id
        self.step = step
        self.deadline = deadline


class CaseEscalated(DomainEvent):
    """Fired when a case is escalated to supervisor review."""
    def __init__(self, request_id: str, reason: str):
        super().__init__()
        self.request_id = request_id
        self.reason = reason


class CaseResolved(DomainEvent):
    """Fired when a case is completed and resolved."""
    def __init__(self, request_id: str, decision: str, notes: str):
        super().__init__()
        self.request_id = request_id
        self.decision = decision
        self.notes = notes


class NoteAdded(DomainEvent):
    """Fired when an internal note is added to a case."""
    def __init__(self, request_id: str, author: str, note_content: str):
        super().__init__()
        self.request_id = request_id
        self.author = author
        self.note_content = note_content


class PaymentStatusChanged(DomainEvent):
    """Fired when payment status changes."""
    def __init__(self, request_id: str, old_status: str, new_status: str, amount: float):
        super().__init__()
        self.request_id = request_id
        self.old_status = old_status
        self.new_status = new_status
        self.amount = amount


class StatusChanged(DomainEvent):
    """Fired when request workflow status changes."""
    def __init__(self, request_id: str, old_status: str, new_status: str, actor: str):
        super().__init__()
        self.request_id = request_id
        self.old_status = old_status
        self.new_status = new_status
        self.actor = actor


class OfficerAssigned(DomainEvent):
    """Fired when a request is assigned to an officer."""
    def __init__(self, request_id: str, officer_id: str, assigned_at: float):
        super().__init__()
        self.request_id = request_id
        self.officer_id = officer_id
        self.assigned_at = assigned_at
        self.actor = "System"


class OfficerReassigned(DomainEvent):
    """Fired when a request is reassigned from one officer to another."""
    def __init__(self, request_id: str, old_officer_id: str, new_officer_id: str, reason: str, reassigned_at: float):
        super().__init__()
        self.request_id = request_id
        self.old_officer_id = old_officer_id
        self.new_officer_id = new_officer_id
        self.reason = reason
        self.reassigned_at = reassigned_at
        self.actor = "System"


class DepartmentAssigned(DomainEvent):
    """Fired when a request is assigned to a department."""
    def __init__(self, request_id: str, department: str, team: str, assigned_at: float):
        super().__init__()
        self.request_id = request_id
        self.department = department
        self.team = team
        self.assigned_at = assigned_at
        self.actor = "System"


class SupervisorReviewRequested(DomainEvent):
    """Fired when a case is marked for supervisor review."""
    def __init__(self, request_id: str, supervisor_id: str, requested_at: float):
        super().__init__()
        self.request_id = request_id
        self.supervisor_id = supervisor_id
        self.requested_at = requested_at
        self.actor = "System"


class CaseReturnedToOfficer(DomainEvent):
    """Fired when a case is returned from supervisor review to the officer."""
    def __init__(self, request_id: str, officer_id: str, returned_at: float):
        super().__init__()
        self.request_id = request_id
        self.officer_id = officer_id
        self.returned_at = returned_at
        self.actor = "System"


class AssignmentClosed(DomainEvent):
    """Fired when assignment workflow is closed."""
    def __init__(self, request_id: str, closed_at: float):
        super().__init__()
        self.request_id = request_id
        self.closed_at = closed_at
        self.actor = "System"


class SLARuleAssigned(DomainEvent):
    """Fired when an SLA Rule is assigned to a Service Request."""
    def __init__(self, request_id: str, rule_id: str, timestamp: float):
        super().__init__()
        self.request_id = request_id
        self.rule_id = rule_id
        self.timestamp = timestamp


class SLAStateChanged(DomainEvent):
    """Fired when the SLA State of a Service Request changes."""
    def __init__(self, request_id: str, old_state: str, new_state: str, timestamp: float):
        super().__init__()
        self.request_id = request_id
        self.old_state = old_state
        self.new_state = new_state
        self.timestamp = timestamp


class RequestMarkedAtRisk(DomainEvent):
    """Fired when a request is flagged as At Risk."""
    def __init__(self, request_id: str, timestamp: float):
        super().__init__()
        self.request_id = request_id
        self.timestamp = timestamp


class RequestMarkedOverdue(DomainEvent):
    """Fired when a request is flagged as Overdue."""
    def __init__(self, request_id: str, timestamp: float):
        super().__init__()
        self.request_id = request_id
        self.timestamp = timestamp


class EscalationRecommended(DomainEvent):
    """Fired when escalation threshold has been exceeded and escalation is recommended."""
    def __init__(self, request_id: str, timestamp: float):
        super().__init__()
        self.request_id = request_id
        self.timestamp = timestamp


class RequestEscalated(DomainEvent):
    """Fired when a request is officially escalated to a supervisor."""
    def __init__(self, request_id: str, supervisor_id: str, reason: str, timestamp: float):
        super().__init__()
        self.request_id = request_id
        self.supervisor_id = supervisor_id
        self.reason = reason
        self.timestamp = timestamp


class EscalationResolved(DomainEvent):
    """Fired when a request's escalation status is resolved."""
    def __init__(self, request_id: str, timestamp: float):
        super().__init__()
        self.request_id = request_id
        self.timestamp = timestamp


