"""PII and Service Request status redaction helpers for public REST API readiness.

Ensures that no raw NIN, phone numbers, email addresses, or internal office notes are leaked.
"""

import re
from typing import Any, Dict, Optional

from nilegov_stack.domain.interoperability import INTEROPERABILITY_DISCLAIMER

# A list of internal workflow/security fields that must NEVER leak to the public payload.
FORBIDDEN_FIELDS = [
    "assigned_officer",
    "assigned_supervisor",
    "assigned_department",
    "assigned_team",
    "queue_name",
    "internal_status",
    "decision",
    "closure_notes",
    "sla_deadline",
    "response_due_at",
    "resolution_due_at",
    "sla_last_checked_at",
    "reassignment_reason",
    "escalation_reason",
    "escalated_to",
    "escalated_at",
    "at_risk_flag",
    "overdue_flag",
    "identity_by",
    "identity_timestamp",
    "payment_timestamp",
]


def mask_nin(value: Optional[str]) -> str:
    """Masks all but the last 4 characters of a National ID Number (NIN).

    If missing or too short, returns 'REDACTED'.
    """
    if not value or not isinstance(value, str):
        return "REDACTED"
    val = value.strip()
    if len(val) < 8:
        return "REDACTED"
    return "*" * (len(val) - 4) + val[-4:]


def mask_phone(value: Optional[str]) -> str:
    """Masks a phone number. Keeps country code prefix and last 3 digits where safe.

    Example: +256700123001 becomes +25670****001.
    If missing or too short (e.g. less than 7 chars), returns 'REDACTED'.
    """
    if not value or not isinstance(value, str):
        return "REDACTED"
    val = value.strip()
    if len(val) < 7:
        return "REDACTED"
    # Find prefix (e.g., '+25670' or '070')
    if val.startswith("+"):
        prefix_len = 6  # Keep '+' and 5 digits e.g. +25670
    elif val.startswith("0"):
        prefix_len = 3  # Keep e.g. 070
    else:
        prefix_len = 3

    if len(val) <= prefix_len + 3:
        return "REDACTED"

    prefix = val[:prefix_len]
    suffix = val[-3:]
    stars = "*" * (len(val) - prefix_len - 3)
    return f"{prefix}{stars}{suffix}"


def mask_email(value: Optional[str]) -> str:
    """Masks email address, keeping first character and domain.

    Example: robert@example.com becomes r*****@example.com.
    If invalid or missing, returns 'REDACTED'.
    """
    if not value or not isinstance(value, str):
        return "REDACTED"
    val = value.strip()
    # Simple regex validation
    if "@" not in val or not re.match(r"^[^@]+@[^@]+\.[^@]+$", val):
        return "REDACTED"
    parts = val.split("@")
    local = parts[0]
    domain = parts[1]
    if not local:
        return "REDACTED"
    return f"{local[0]}{'*' * (len(local) - 1)}@{domain}"


def redact_service_request_status(data: Dict[str, Any]) -> Dict[str, Any]:
    """Builds a public-safe status response from Service Request record data.

    Strictly removes all forbidden fields and sanitizes PII fields.
    """
    # Enforce absence of raw PII
    masked_nin_val = mask_nin(data.get("nin"))
    masked_phone_val = mask_phone(data.get("phone"))
    masked_email_val = mask_email(data.get("email"))

    # Map internal status to public-safe wording if internal status is present
    internal_stat = data.get("internal_status", "Pending")
    public_status = data.get("citizen_visible_status")
    if not public_status:
        if internal_stat in ("Approved", "Ready for Collection"):
            public_status = "Approved & Ready for Collection"
        elif internal_stat == "Closed":
            public_status = "Completed"
        else:
            public_status = "In Progress"

    # Simplify SLA state
    sla_state_val = data.get("sla_state")
    if not sla_state_val or sla_state_val not in ("Within SLA", "At Risk", "Overdue", "Met"):
        sla_state_val = "Processing"
    elif sla_state_val == "Met":
        sla_state_val = "Completed"

    # Payment status mapping
    pay_status = data.get("payment_status")
    if not pay_status or pay_status not in ("Paid", "Pending", "Not Required", "Failed"):
        pay_status = "Pending"

    # Evidence status mapping
    evi_status = data.get("evidence_status")
    if not evi_status:
        evi_status = "Pending Review"

    # Next step wording
    next_step = "Your service request is being reviewed by the processing unit."
    if pay_status == "Pending":
        next_step = "Processing fee payment is required to proceed."
    elif public_status == "Approved & Ready for Collection":
        next_step = "Please collect your document from the designated service center."
    elif public_status == "Completed":
        next_step = "This request has been successfully closed."

    redacted = {
        "service_request_reference": data.get("service_request_id") or data.get("name") or "UNKNOWN",
        "service_type": data.get("service_type") or "UNKNOWN",
        "citizen_visible_status": public_status,
        "submitted_at": data.get("submitted_at"),
        "location": data.get("location") or "Not specified",
        "payment_status": pay_status,
        "evidence_status": evi_status,
        "sla_state": sla_state_val,
        "next_step_message": next_step,
        "masked_nin": masked_nin_val,
        "masked_phone": masked_phone_val,
        "masked_email": masked_email_val,
        "disclaimer": INTEROPERABILITY_DISCLAIMER,
    }

    return redacted
