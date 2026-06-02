"""API envelope helpers for NileGov interoperability readiness."""

from typing import Any, Dict, Optional

from nilegov_stack.domain.interoperability import (
    APIEnvelope,
    APIError,
    generate_correlation_id,
)


def build_success_envelope(
    data: Dict[str, Any],
    correlation_id: Optional[str] = None,
) -> APIEnvelope:
    return APIEnvelope(
        success=True,
        correlation_id=correlation_id or generate_correlation_id(),
        data=data,
        error=None,
    )


def build_error_envelope(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    retryable: bool = False,
    correlation_id: Optional[str] = None,
) -> APIEnvelope:
    corr = correlation_id or generate_correlation_id()
    return APIEnvelope(
        success=False,
        correlation_id=corr,
        data=None,
        error=APIError(
            code=code,
            message=message,
            details=details or {},
            retryable=retryable,
            correlation_id=corr,
        ),
    )
