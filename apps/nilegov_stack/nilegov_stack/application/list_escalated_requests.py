# Use case: List Escalated Requests
# Prototype simulation only. No live Government registry access.

from typing import List
from nilegov_stack.application.ports import ServiceRequestRepository
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.domain.sla import EscalationState

class ListEscalatedRequests:
    def __init__(self, request_repo: ServiceRequestRepository):
        self.request_repo = request_repo

    def execute(self) -> List[ServiceRequest]:
        all_reqs = self.request_repo.get_all()
        return [
            req for req in all_reqs
            if req.escalation_state == EscalationState.ESCALATED
        ]
