"""Interoperability domain models for NileGov Stack.

These models represent simulated API/interoperability readiness only.
No live government system is contacted from this layer.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


INTEROPERABILITY_DISCLAIMER = (
    "Prototype interoperability simulation only. No live government system was contacted."
)

ALLOWED_INTEGRATION_STATUSES = {
    "Draft",
    "Simulated Pending",
    "Simulated Completed",
    "Simulated Failed",
    "Requires Review",
    "Not Sent",
}

ALLOWED_TARGET_SYSTEMS = {
    "Simulated NIRA",
    "Simulated UGHub",
    "Simulated Payment Provider",
    "Simulated Notification Gateway",
    "Simulated MDA System",
    "Internal NileGov",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_correlation_id() -> str:
    return f"corr-{uuid4().hex}"


def generate_idempotency_key() -> str:
    return f"idem-{uuid4().hex}"


@dataclass
class APIError:
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    retryable: bool = False
    correlation_id: str = field(default_factory=generate_correlation_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "retryable": self.retryable,
            "correlation_id": self.correlation_id,
        }


@dataclass
class APIEnvelope:
    success: bool
    correlation_id: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[APIError] = None
    timestamp: datetime = field(default_factory=utc_now)
    disclaimer: str = INTEROPERABILITY_DISCLAIMER

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "correlation_id": self.correlation_id,
            "data": self.data,
            "error": self.error.to_dict() if self.error else None,
            "timestamp": self.timestamp.isoformat(),
            "disclaimer": self.disclaimer,
        }


@dataclass
class IntegrationRequest:
    integration_request_id: str
    correlation_id: str
    idempotency_key: str
    source_system: str
    target_system: str
    operation: str
    payload: Dict[str, Any]
    status: str = "Draft"
    service_request_reference: Optional[str] = None
    requested_at: datetime = field(default_factory=utc_now)
    completed_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    disclaimer: str = INTEROPERABILITY_DISCLAIMER

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_INTEGRATION_STATUSES:
            raise ValueError(f"Invalid integration status: {self.status}")
        if self.target_system not in ALLOWED_TARGET_SYSTEMS:
            raise ValueError(f"Invalid target system: {self.target_system}")
        if not self.integration_request_id:
            raise ValueError("integration_request_id is required")
        if not self.correlation_id:
            raise ValueError("correlation_id is required")
        if not self.idempotency_key:
            raise ValueError("idempotency_key is required")
        if not self.source_system:
            raise ValueError("source_system is required")
        if not self.operation:
            raise ValueError("operation is required")

    def mark_success(self, response_payload: Optional[Dict[str, Any]] = None) -> "IntegrationResponse":
        self.status = "Simulated Completed"
        self.completed_at = utc_now()
        return IntegrationResponse(
            correlation_id=self.correlation_id,
            operation=self.operation,
            status=self.status,
            response_payload=response_payload or {},
            completed_at=self.completed_at,
        )

    def mark_failure(self, error_code: str, error_message: str) -> "IntegrationResponse":
        self.status = "Simulated Failed"
        self.completed_at = utc_now()
        self.error_code = error_code
        self.error_message = error_message
        return IntegrationResponse(
            correlation_id=self.correlation_id,
            operation=self.operation,
            status=self.status,
            response_payload={},
            error_code=error_code,
            error_message=error_message,
            completed_at=self.completed_at,
        )


@dataclass
class IntegrationResponse:
    correlation_id: str
    operation: str
    status: str
    response_payload: Dict[str, Any]
    completed_at: datetime = field(default_factory=utc_now)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    disclaimer: str = INTEROPERABILITY_DISCLAIMER

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_INTEGRATION_STATUSES:
            raise ValueError(f"Invalid integration response status: {self.status}")
        if not self.correlation_id:
            raise ValueError("correlation_id is required")
        if not self.operation:
            raise ValueError("operation is required")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "operation": self.operation,
            "status": self.status,
            "response_payload": self.response_payload,
            "completed_at": self.completed_at.isoformat(),
            "error_code": self.error_code,
            "error_message": self.error_message,
            "disclaimer": self.disclaimer,
        }
