from datetime import datetime, timezone

import pytest

from nilegov_stack.application.build_api_envelope import build_error_envelope, build_success_envelope
from nilegov_stack.application.build_interoperability_payloads import (
    assert_payload_excludes_sensitive_values,
    build_identity_verification_payload,
    build_notification_event_payload,
    build_payment_verification_payload,
    build_reporting_snapshot_payload,
    build_service_request_payload,
)
from nilegov_stack.application.create_integration_request import CreateIntegrationRequest
from nilegov_stack.application.generate_integration_keys import GenerateIntegrationKeys
from nilegov_stack.application.list_integration_requests import ListIntegrationRequests
from nilegov_stack.application.record_integration_result import (
    RecordIntegrationFailure,
    RecordIntegrationSuccess,
)
from nilegov_stack.domain.interoperability import (
    INTEROPERABILITY_DISCLAIMER,
    APIEnvelope,
    APIError,
    IntegrationRequest,
    IntegrationResponse,
    generate_correlation_id,
    generate_idempotency_key,
)
from nilegov_stack.infrastructure.repositories.integration_request_repository import (
    InMemoryIntegrationRequestRepository,
)


class DummyServiceRequest:
    reference_number = "NGS-NIRA-2026-0001"
    service_type = "SVC-LOST-NID"
    citizen_profile_id = "CP-001"
    location = "Ntinda, Kampala"
    status = "Submitted"
    assigned_department = "National ID Replacement Desk"
    sla_state = "Within SLA"
    payment_status = "Pending"
    created_at = datetime(2026, 6, 1, tzinfo=timezone.utc)


class DummyPaymentRecord:
    payment_record_id = "PAY-001"
    service_request_id = "NGS-NIRA-2026-0001"
    amount = 50000
    currency = "UGX"
    payment_purpose = "National ID Replacement Fee"
    provider = "Pesapal Sandbox"
    provider_mode = "sandbox"
    simulated_transaction_reference = "SIM-TXN-001"
    provider_merchant_reference = "MERCH-001"


class DummyNotificationEvent:
    notification_event_id = "NOTIF-001"
    service_request_id = "NGS-NIRA-2026-0001"
    channel = "SMS"
    message_type = "Status Update"
    delivery_status = "Simulated Sent"
    recipient = "+256700000000"


class DummyReportingSnapshot:
    reporting_snapshot_id = "RPT-001"
    reporting_period_start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    reporting_period_end = datetime(2026, 6, 2, tzinfo=timezone.utc)
    total_requests = 3
    requests_by_status = {"Submitted": 2, "Closed": 1}
    requests_by_service = {"SVC-LOST-NID": 3}
    within_sla_count = 2
    at_risk_count = 1
    overdue_count = 0
    escalated_count = 0
    payment_pending_count = 1
    payment_verified_count = 2
    payment_failed_count = 0
    notification_queued_count = 1
    notification_simulated_sent_count = 2
    notification_failed_count = 0
    officer_workload_summary = {"Officer A": 2, "Officer B": 1}


def test_correlation_and_idempotency_keys_are_generated():
    assert generate_correlation_id().startswith("corr-")
    assert generate_idempotency_key().startswith("idem-")

    keys = GenerateIntegrationKeys().execute()
    assert keys["correlation_id"].startswith("corr-")
    assert keys["idempotency_key"].startswith("idem-")


def test_api_success_envelope():
    envelope = build_success_envelope({"ok": True}, correlation_id="corr-test")
    data = envelope.to_dict()

    assert data["success"] is True
    assert data["correlation_id"] == "corr-test"
    assert data["data"] == {"ok": True}
    assert data["error"] is None
    assert data["disclaimer"] == INTEROPERABILITY_DISCLAIMER


def test_api_error_envelope():
    envelope = build_error_envelope(
        code="VALIDATION_ERROR",
        message="Invalid payload",
        details={"field": "service_code"},
        retryable=False,
        correlation_id="corr-error",
    )
    data = envelope.to_dict()

    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["retryable"] is False
    assert data["error"]["correlation_id"] == "corr-error"


def test_integration_request_and_response_can_be_created():
    request = IntegrationRequest(
        integration_request_id="INT-001",
        correlation_id="corr-001",
        idempotency_key="idem-001",
        source_system="Internal NileGov",
        target_system="Simulated UGHub",
        operation="Submit Service Request",
        payload={"reference_number": "NGS-NIRA-2026-0001"},
        status="Simulated Pending",
        service_request_reference="NGS-NIRA-2026-0001",
    )

    assert request.disclaimer == INTEROPERABILITY_DISCLAIMER

    response = IntegrationResponse(
        correlation_id="corr-001",
        operation="Submit Service Request",
        status="Simulated Completed",
        response_payload={"accepted": True},
    )

    assert response.to_dict()["response_payload"] == {"accepted": True}


def test_invalid_target_system_is_rejected():
    with pytest.raises(ValueError):
        IntegrationRequest(
            integration_request_id="INT-002",
            correlation_id="corr-002",
            idempotency_key="idem-002",
            source_system="Internal NileGov",
            target_system="Live NIRA",
            operation="Verify Identity",
            payload={},
        )


def test_invalid_status_is_rejected():
    with pytest.raises(ValueError):
        IntegrationRequest(
            integration_request_id="INT-003",
            correlation_id="corr-003",
            idempotency_key="idem-003",
            source_system="Internal NileGov",
            target_system="Simulated NIRA",
            operation="Verify Identity",
            payload={},
            status="Live Verified",
        )


def test_create_and_list_integration_requests():
    repo = InMemoryIntegrationRequestRepository()
    use_case = CreateIntegrationRequest(repo)

    request = use_case.execute(
        source_system="Internal NileGov",
        target_system="Simulated UGHub",
        operation="Submit Service Request",
        payload={"reference_number": "NGS-NIRA-2026-0001"},
        service_request_reference="NGS-NIRA-2026-0001",
        status="Simulated Pending",
    )

    lister = ListIntegrationRequests(repo)

    assert request.integration_request_id.startswith("INT-")
    assert len(lister.by_target_system("Simulated UGHub")) == 1
    assert len(lister.by_status("Simulated Pending")) == 1
    assert len(lister.by_service_request("NGS-NIRA-2026-0001")) == 1


def test_record_simulated_success_and_failure():
    repo = InMemoryIntegrationRequestRepository()
    request = CreateIntegrationRequest(repo).execute(
        source_system="Internal NileGov",
        target_system="Simulated MDA System",
        operation="Send Case Update",
        payload={"case": "NGS-NIRA-2026-0001"},
        status="Simulated Pending",
    )

    success = RecordIntegrationSuccess(repo).execute(
        request.integration_request_id,
        {"accepted": True},
    )

    assert success.status == "Simulated Completed"
    assert repo.get(request.integration_request_id).status == "Simulated Completed"

    failed_request = CreateIntegrationRequest(repo).execute(
        source_system="Internal NileGov",
        target_system="Simulated Notification Gateway",
        operation="Notify Citizen",
        payload={"notification": "NOTIF-001"},
        status="Simulated Pending",
    )

    failure = RecordIntegrationFailure(repo).execute(
        failed_request.integration_request_id,
        "SIMULATED_FAILURE",
        "The simulated gateway returned a failure.",
    )

    assert failure.status == "Simulated Failed"
    assert repo.get(failed_request.integration_request_id).error_code == "SIMULATED_FAILURE"


def test_service_request_payload_is_safe():
    payload = build_service_request_payload(
        DummyServiceRequest(),
        service_name="Lost National ID Replacement",
        evidence_status_summary={"complete": 2, "missing": 1},
    )

    assert payload["reference_number"] == "NGS-NIRA-2026-0001"
    assert payload["service_code"] == "SVC-LOST-NID"
    assert payload["disclaimer"] == INTEROPERABILITY_DISCLAIMER


def test_identity_payload_excludes_real_nin():
    payload = build_identity_verification_payload(
        service_request_reference="NGS-NIRA-2026-0001",
        citizen_profile_id="CP-001",
        consent_reference="CONSENT-001",
        verification_purpose="Lost National ID Replacement",
    )

    assert "nin" not in str(payload).lower()
    assert "SIMULATED_IDENTIFIER_REDACTED" in str(payload)
    assert_payload_excludes_sensitive_values(payload, ["CM123456789ABCDE"])


def test_payment_payload_excludes_raw_payment_details():
    payload = build_payment_verification_payload(DummyPaymentRecord())

    assert payload["provider_mode"] == "sandbox"
    assert "card" not in str(payload).lower()
    assert "pin" not in str(payload).lower()
    assert_payload_excludes_sensitive_values(payload, ["4111111111111111", "1234"])


def test_notification_payload_excludes_contact_secret():
    payload = build_notification_event_payload(DummyNotificationEvent())

    assert payload["notification_event_id"] == "NOTIF-001"
    assert "0700000000" not in str(payload)
    assert "+256700000000" not in str(payload)


def test_reporting_snapshot_payload_contains_metric_groups():
    payload = build_reporting_snapshot_payload(DummyReportingSnapshot())

    assert payload["total_requests"] == 3
    assert "sla_summary" in payload
    assert "payment_summary" in payload
    assert "notification_summary" in payload
    assert "workload_summary" in payload
    assert payload["disclaimer"] == INTEROPERABILITY_DISCLAIMER


def test_sensitive_value_guard_raises():
    with pytest.raises(ValueError):
        assert_payload_excludes_sensitive_values(
            {"identifier": "CM123456789ABCDE"},
            ["CM123456789ABCDE"],
        )
