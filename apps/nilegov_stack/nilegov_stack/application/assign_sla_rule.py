# Use case: Assign SLA Rule to Service Request
# Prototype simulation only. No live Government registry access.

import time
from typing import Optional
from nilegov_stack.application.ports import ServiceRequestRepository, SLARuleRepository

class AssignSLARule:
    def __init__(self, request_repo: ServiceRequestRepository, rule_repo: SLARuleRepository):
        self.request_repo = request_repo
        self.rule_repo = rule_repo

    def execute(self, request_id: str, rule_id: Optional[str] = None, timestamp: Optional[float] = None) -> None:
        t = timestamp if timestamp is not None else time.time()
        req = self.request_repo.get_by_id(request_id)
        if not req:
            raise ValueError(f"Service Request with ID {request_id} not found.")
        
        if not rule_id:
            rule = self.rule_repo.get_by_service_type(req.service_type)
        else:
            rule = self.rule_repo.get_by_id(rule_id)
            
        if not rule:
            # No SLA rule found, leave as Not Applicable
            return
            
        req.assign_sla_rule(rule, t)
        self.request_repo.save(req)
