# Escalation Entity for NileGov Stack
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

class EscalationRecord:
    """Represents a case escalation due to SLA breach or supervisor routing."""
    def __init__(
        self,
        escalation_id: str,
        service_request: str,
        escalation_reason: str,
        escalated_by: str,
        escalated_to: str,
        escalated_at: float,
        status: str = "Pending"
    ):
        self.escalation_id = escalation_id
        self.service_request = service_request
        self.escalation_reason = escalation_reason
        self.escalated_by = escalated_by
        self.escalated_to = escalated_to
        self.escalated_at = escalated_at
        self.status = status

    def resolve(self):
        self.status = "Resolved"
