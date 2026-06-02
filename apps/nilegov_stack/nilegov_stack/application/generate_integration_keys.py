"""Correlation and idempotency key helpers."""

from nilegov_stack.domain.interoperability import (
    generate_correlation_id,
    generate_idempotency_key,
)


class GenerateIntegrationKeys:
    def execute(self) -> dict:
        return {
            "correlation_id": generate_correlation_id(),
            "idempotency_key": generate_idempotency_key(),
        }
