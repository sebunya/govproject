# Use case: Create SLA Rule
# Prototype simulation only. No live Government registry access.

from nilegov_stack.application.ports import SLARuleRepository
from nilegov_stack.domain.sla import SLARule

class CreateSLARule:
    def __init__(self, rule_repo: SLARuleRepository):
        self.rule_repo = rule_repo

    def execute(
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
    ) -> SLARule:
        if response_hours <= 0 or resolution_hours <= 0:
            raise ValueError("SLA hours must be positive integers.")
        if at_risk_threshold_percent <= 0 or at_risk_threshold_percent > 100:
            raise ValueError("At Risk Threshold Percent must be between 1 and 100.")
            
        rule = SLARule(
            rule_id=rule_id,
            service_type=service_type,
            response_hours=response_hours,
            resolution_hours=resolution_hours,
            at_risk_threshold_percent=at_risk_threshold_percent,
            escalation_threshold_hours=escalation_threshold_hours,
            escalation_queue=escalation_queue,
            escalation_role=escalation_role,
            notes=notes,
            disclaimer=disclaimer,
            active=active
        )
        self.rule_repo.save(rule)
        return rule
