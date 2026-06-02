# Use case: Evaluate SLA State
# Prototype simulation only. No live Government registry access.

import time
from typing import Optional
from nilegov_stack.application.ports import ServiceRequestRepository, SLARuleRepository

class EvaluateSLAState:
    def __init__(self, request_repo: ServiceRequestRepository, rule_repo: SLARuleRepository):
        self.request_repo = request_repo
        self.rule_repo = rule_repo

    def execute(self, request_id: str, current_time: Optional[float] = None) -> None:
        t = current_time if current_time is not None else time.time()
        req = self.request_repo.get_by_id(request_id)
        if not req:
            raise ValueError(f"Service Request with ID {request_id} not found.")
            
        rule = None
        if req.sla_rule_id:
            rule = self.rule_repo.get_by_id(req.sla_rule_id)
            
        req.evaluate_sla_state(t, rule)
        self.request_repo.save(req)
