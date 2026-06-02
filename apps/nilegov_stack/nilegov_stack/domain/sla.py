# SLA Entity and State Constants for NileGov Stack
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

class SLAState:
    WITHIN_SLA = "Within SLA"
    AT_RISK = "At Risk"
    OVERDUE = "Overdue"
    PAUSED = "Paused"
    MET = "Met"
    NOT_APPLICABLE = "Not Applicable"


class EscalationState:
    NOT_ESCALATED = "Not Escalated"
    RECOMMENDED = "Escalation Recommended"
    ESCALATED = "Escalated"
    SUPERVISOR_REVIEWING = "Supervisor Reviewing"
    RESOLVED = "Resolved"


class SLARule:
    """Defines processing limits (SLA) for a specific Service Type."""
    def __init__(
        self,
        rule_id: str,
        service_type: str,
        response_hours: int,
        resolution_hours: int,
        at_risk_threshold_percent: int = 80,
        escalation_threshold_hours: int = 2,
        escalation_queue: str = "Supervisor Review Queue",
        escalation_role: str = "supervisor_demo",
        notes: str = None,
        disclaimer: str = "Prototype simulation only. No live Government registry access.",
        active: bool = True
    ):
        self.rule_id = rule_id
        self.service_type = service_type
        self.response_hours = response_hours
        self.resolution_hours = resolution_hours
        self.at_risk_threshold_percent = at_risk_threshold_percent
        self.escalation_threshold_hours = escalation_threshold_hours
        self.escalation_queue = escalation_queue
        self.escalation_role = escalation_role
        self.notes = notes
        self.disclaimer = disclaimer
        self.active = active


class SLAEvent:
    """Logs the progression of a Service Request relative to SLA deadlines."""
    def __init__(self, event_id: str, request_id: str, start_time: float, deadline: float):
        self.event_id = event_id
        self.request_id = request_id
        self.start_time = start_time
        self.deadline = deadline
        self.breached = False

    def check_breach(self, current_time: float) -> bool:
        if current_time > self.deadline:
            self.breached = True
        return self.breached
