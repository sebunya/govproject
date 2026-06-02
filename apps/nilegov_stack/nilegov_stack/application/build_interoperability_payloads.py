"""Safe payload builders for API / interoperability readiness.

These builders intentionally minimise sensitive data and avoid live registry claims.
"""

from typing import Any, Dict, Iterable, Optional

from nilegov_stack.domain.interoperability import INTEROPERABILITY_DISCLAIMER


def _safe_value(value: Any, fallback: Any = None) -> Any:
    return fallback if value is None else value


def build_service_request_payload(
    service_request,
    service_name: Optional[str] = None,
    evidence_status_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "reference_number": service_request.reference_number,
        "service_code": _safe_value(getattr(service_request, "service_type", None), "UNKNOWN_SERVICE"),
        "service_name": service_name or "Prototype Government Service",
        "citizen_profile_id": _safe_value(getattr(service_request, "citizen_profile_id", None), "REDACTED"),
        "location": _safe_value(getattr(service_request, "location", None), "Not specified"),
        "status": service_request.status,
        "assigned_queue": _safe_value(getattr(service_request, "assigned_department", None), "Unassigned"),
        "sla_state": _safe_value(getattr(service_request, "sla_state", None), "Not Evaluated"),
        "payment_status": _safe_value(getattr(service_request, "payment_status", None), "Not Required"),
        "evidence_status_summary": evidence_status_summary or {},
        "created_at": service_request.created_at.isoformat() if getattr(service_request, "created_at", None) else None,
        "disclaimer": INTEROPERABILITY_DISCLAIMER,
    }


def build_identity_verification_payload(
    service_request_reference: str,
    citizen_profile_id: str,
    consent_reference: str,
    verification_purpose: str,
) -> Dict[str, Any]:
    return {
        "service_request_reference": service_request_reference,
        "citizen_profile_id": citizen_profile_id,
        "consent_reference": consent_reference,
        "verification_purpose": verification_purpose,
        "simulated_identifier_reference": "SIMULATED_IDENTIFIER_REDACTED",
        "disclaimer": INTEROPERABILITY_DISCLAIMER,
    }


def build_payment_verification_payload(payment_record) -> Dict[str, Any]:
    return {
        "payment_record_id": payment_record.payment_record_id,
        "service_request_reference": payment_record.service_request_id,
        "amount": payment_record.amount,
        "currency": payment_record.currency,
        "payment_purpose": payment_record.payment_purpose,
        "provider": _safe_value(getattr(payment_record, "provider", None), "Simulated"),
        "provider_mode": _safe_value(getattr(payment_record, "provider_mode", None), "sandbox"),
        "simulated_transaction_reference": _safe_value(
            getattr(payment_record, "simulated_transaction_reference", None),
            getattr(payment_record, "provider_merchant_reference", None),
        ),
        "disclaimer": INTEROPERABILITY_DISCLAIMER,
    }


def build_notification_event_payload(notification_event) -> Dict[str, Any]:
    return {
        "notification_event_id": notification_event.notification_event_id,
        "service_request_reference": notification_event.service_request_id,
        "recipient_type": "Citizen",
        "channel": notification_event.channel,
        "message_type": notification_event.message_type,
        "delivery_status": notification_event.delivery_status,
        "disclaimer": INTEROPERABILITY_DISCLAIMER,
    }


def build_reporting_snapshot_payload(reporting_snapshot) -> Dict[str, Any]:
    return {
        "reporting_snapshot_id": reporting_snapshot.reporting_snapshot_id,
        "reporting_period": {
            "start": reporting_snapshot.reporting_period_start.isoformat()
            if reporting_snapshot.reporting_period_start
            else None,
            "end": reporting_snapshot.reporting_period_end.isoformat()
            if reporting_snapshot.reporting_period_end
            else None,
        },
        "total_requests": reporting_snapshot.total_requests,
        "requests_by_status": reporting_snapshot.requests_by_status,
        "requests_by_service": reporting_snapshot.requests_by_service,
        "sla_summary": {
            "within_sla": reporting_snapshot.within_sla_count,
            "at_risk": reporting_snapshot.at_risk_count,
            "overdue": reporting_snapshot.overdue_count,
            "escalated": reporting_snapshot.escalated_count,
        },
        "payment_summary": {
            "pending": reporting_snapshot.payment_pending_count,
            "verified": reporting_snapshot.payment_verified_count,
            "failed": reporting_snapshot.payment_failed_count,
        },
        "notification_summary": {
            "queued": reporting_snapshot.notification_queued_count,
            "simulated_sent": reporting_snapshot.notification_simulated_sent_count,
            "failed": reporting_snapshot.notification_failed_count,
        },
        "workload_summary": reporting_snapshot.officer_workload_summary,
        "disclaimer": INTEROPERABILITY_DISCLAIMER,
    }


def assert_payload_excludes_sensitive_values(payload: Dict[str, Any], forbidden_values: Iterable[str]) -> None:
    serialized = str(payload)
    for value in forbidden_values:
        if value and value in serialized:
            raise ValueError("Payload contains sensitive value that must not be exposed")
