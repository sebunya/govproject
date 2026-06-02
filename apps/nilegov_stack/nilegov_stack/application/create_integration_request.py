"""Use case for creating simulated interoperability requests."""

from typing import Any, Dict, Optional
from uuid import uuid4

from nilegov_stack.domain.interoperability import (
    IntegrationRequest,
    generate_correlation_id,
    generate_idempotency_key,
)


class CreateIntegrationRequest:
    def __init__(self, repository):
        self.repository = repository

    def execute(
        self,
        source_system: str,
        target_system: str,
        operation: str,
        payload: Dict[str, Any],
        service_request_reference: Optional[str] = None,
        status: str = "Draft",
    ) -> IntegrationRequest:
        request = IntegrationRequest(
            integration_request_id=f"INT-{uuid4().hex[:12].upper()}",
            correlation_id=generate_correlation_id(),
            idempotency_key=generate_idempotency_key(),
            source_system=source_system,
            target_system=target_system,
            operation=operation,
            payload=payload,
            service_request_reference=service_request_reference,
            status=status,
        )
        return self.repository.save(request)
