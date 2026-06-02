"""Unit tests for public redaction and masking helpers."""

import pytest
from nilegov_stack.application.redaction import (
    FORBIDDEN_FIELDS,
    mask_email,
    mask_nin,
    mask_phone,
    redact_service_request_status,
)


def test_mask_nin():
    assert mask_nin("CM1234567890001") == "***********0001"
    assert mask_nin("CF1234567") == "*****4567"
    assert mask_nin("") == "REDACTED"
    assert mask_nin(None) == "REDACTED"
    assert mask_nin("123") == "REDACTED"


def test_mask_phone():
    assert mask_phone("+256700123001") == "+25670****001"
    assert mask_phone("0700123001") == "070****001"
    assert mask_phone("12345") == "REDACTED"
    assert mask_phone(None) == "REDACTED"


def test_mask_email():
    assert mask_email("robert@example.com") == "r*****@example.com"
    assert mask_email("a@b.com") == "a@b.com"
    assert mask_email("invalid-email") == "REDACTED"
    assert mask_email(None) == "REDACTED"


def test_redact_service_request_status():
    raw_data = {
        "service_request_id": "REQ-2026-0001",
        "service_type": "LOST_NATIONAL_ID",
        "nin": "CM1234567890001",
        "phone": "+256700123001",
        "email": "robert@example.com",
        "location": "Kampala",
        "internal_status": "Approved",
        "assigned_officer": "officer_demo",
        "assigned_supervisor": "supervisor_demo",
        "assigned_department": "Verification Desk",
        "closure_notes": "Internal closing notes",
        "submitted_at": "2026-06-02T12:00:00",
        "sla_state": "Within SLA",
        "payment_status": "Paid",
        "evidence_status": "Accepted",
    }

    redacted = redact_service_request_status(raw_data)

    # Public safe fields check
    assert redacted["service_request_reference"] == "REQ-2026-0001"
    assert redacted["service_type"] == "LOST_NATIONAL_ID"
    assert redacted["citizen_visible_status"] == "Approved & Ready for Collection"
    assert redacted["masked_nin"] == "***********0001"
    assert redacted["masked_phone"] == "+25670****001"
    assert redacted["masked_email"] == "r*****@example.com"
    assert redacted["location"] == "Kampala"
    assert redacted["payment_status"] == "Paid"
    assert redacted["evidence_status"] == "Accepted"
    assert redacted["sla_state"] == "Within SLA"

    # Make sure forbidden fields are completely absent
    for field in FORBIDDEN_FIELDS:
        assert field not in redacted
