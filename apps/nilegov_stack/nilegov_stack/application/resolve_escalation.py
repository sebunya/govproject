# Use case: Resolve Case Escalation
# Prototype simulation only. No live Government registry access.

import time
from typing import Optional
from nilegov_stack.application.ports import ServiceRequestRepository

class ResolveEscalation:
    def __init__(self, request_repo: ServiceRequestRepository):
        self.request_repo = request_repo

    def execute(self, request_id: str, timestamp: Optional[float] = None) -> None:
        t = timestamp if timestamp is not None else time.time()
        req = self.request_repo.get_by_id(request_id)
        if not req:
            raise ValueError(f"Service Request with ID {request_id} not found.")
            
        req.resolve_escalation(t)
        self.request_repo.save(req)
