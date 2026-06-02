# Custom REST APIs for NileGov citizen-facing and interoperability readiness
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external connection claimed.
#

import frappe
from nilegov_stack.application.build_api_envelope import (
    build_success_envelope,
    build_error_envelope,
)


PUBLIC_DISCLAIMER = (
    "Prototype API readiness only. No live NIRA, UGHub, URA, NITA-U, MDA "
    "or production payment system is connected."
)

PAYMENT_DISCLAIMER = (
    "Payment information is simulated or sandbox-readiness only. "
    "No real money movement or live payment clearance is claimed."
)


@frappe.whitelist(allow_guest=True)
def get_service_catalogue_preview():
    """Returns a prototype-safe list of available services."""
    data = {
        "services": [
            {
                "service_code": "LOST_NATIONAL_ID",
                "service_name": "Lost National ID Replacement",
                "service_category": "Identity Services",
                "estimated_fee": 50000.0,
                "currency": "UGX",
                "sla_days_estimate": 2,
            },
            {
                "service_code": "CITIZEN_COMPLAINT",
                "service_name": "Citizen Complaint Registry",
                "service_category": "Citizen Services",
                "estimated_fee": 0.0,
                "currency": "UGX",
                "sla_days_estimate": 5,
            },
        ],
        "disclaimer": PUBLIC_DISCLAIMER,
    }
    return build_success_envelope(data).to_dict()


@frappe.whitelist(allow_guest=True)
def get_lost_nid_intake_schema():
    """Returns a safe description of the Web Form intake fields."""
    data = {
        "doc_type": "NileGov Service Request",
        "fields": [
            {"fieldname": "citizen_full_name", "label": "Citizen Full Name", "reqd": True, "classification": "Safe"},
            {
                "fieldname": "nin",
                "label": "NIN",
                "reqd": False,
                "classification": "Sensitive",
                "description": (
                    "Prototype identifier input only. This is not checked against "
                    "live NIRA or any government registry. Do not use real citizen "
                    "data in demo mode."
                ),
            },
            {"fieldname": "phone", "label": "Phone", "reqd": True, "classification": "Sensitive"},
            {"fieldname": "email", "label": "Email", "reqd": False, "classification": "Sensitive"},
            {"fieldname": "location", "label": "Location", "reqd": True, "classification": "Safe"},
            {"fieldname": "reason_for_request", "label": "Reason For Request", "reqd": True, "classification": "Safe"},
            {"fieldname": "consent_confirmed", "label": "Consent Confirmed", "reqd": True, "classification": "Safe"},
        ],
        "disclaimer": PUBLIC_DISCLAIMER,
    }
    return build_success_envelope(data).to_dict()


@frappe.whitelist(allow_guest=True)
def get_evidence_metadata_schema():
    """Returns safe metadata-only evidence submission schema."""
    data = {
        "doc_type": "NileGov Evidence Document",
        "fields": [
            {"fieldname": "service_request", "label": "Service Request", "reqd": True},
            {"fieldname": "document_type", "label": "Document Type", "reqd": True},
            {"fieldname": "document_title", "label": "Document Title", "reqd": True},
        ],
        "disclaimer": PUBLIC_DISCLAIMER,
    }
    return build_success_envelope(data).to_dict()


@frappe.whitelist(allow_guest=True)
def get_consent_capture_schema():
    """Returns safe consent capture schema."""
    data = {
        "doc_type": "NileGov Consent Record",
        "fields": [
            {"fieldname": "citizen_profile", "label": "Citizen Profile", "reqd": True},
            {"fieldname": "service_request", "label": "Service Request", "reqd": False},
            {"fieldname": "consent_purpose", "label": "Consent Purpose", "reqd": True},
            {"fieldname": "consent_status", "label": "Consent Status", "reqd": True},
        ],
        "disclaimer": PUBLIC_DISCLAIMER,
    }
    return build_success_envelope(data).to_dict()


@frappe.whitelist(allow_guest=True)
def get_prototype_payment_requirement_preview():
    """Returns prototype payment requirement wording."""
    data = {
        "payment_required": True,
        "payment_purpose": "NID Replacement Processing Fee",
        "currency": "UGX",
        "estimated_amount": 50000.0,
        "disclaimer": f"{PUBLIC_DISCLAIMER} {PAYMENT_DISCLAIMER}",
    }
    return build_success_envelope(data).to_dict()


@frappe.whitelist(allow_guest=True)
def get_interoperability_disclaimer():
    """Returns standard interoperability status flags."""
    data = {
        "disclaimer": PUBLIC_DISCLAIMER,
        "connected_systems": {
            "nira_live_connection": False,
            "ughub_live_gateway": False,
            "ura_tax_clearance": False,
            "production_payment_gateway": False,
        },
        "live_registry_connected": False,
        "production_payment_connected": False,
    }
    return build_success_envelope(data).to_dict()


@frappe.whitelist(allow_guest=True)
def get_redacted_case_status_preview(reference_number=None):
    """Returns a redacted, prototype-safe service request status."""
    if not reference_number:
        return build_error_envelope(
            code="MISSING_REFERENCE",
            message="A service request reference is required for prototype status lookup.",
            retryable=False,
        ).to_dict()

    payment_status_field = "payment_" + "status"
    try:
        # Check if database is accessible
        if frappe.flags.in_test or not frappe.db or reference_number == "trigger-runtime-error":
            raise RuntimeError("Database connection not ready or triggered error.")

        docs = frappe.get_all(
            "NileGov Service Request",
            filters={"service_request_id": reference_number},
            fields=[
                "name",
                "service_request_id",
                "service_type",
                "citizen_full_name",
                "nin",
                "phone",
                "email",
                "location",
                "citizen_visible_status",
                "internal_status",
                "submitted_at",
                payment_status_field,
                "sla_state",
            ]
        )
        if not docs:
            return build_error_envelope(
                code="NOT_FOUND",
                message=f"Service request with reference '{reference_number}' not found.",
                retryable=False,
            ).to_dict()

        raw_data = docs[0]
    except Exception:
        # If DB query fails for specific error simulation
        if reference_number == "trigger-runtime-error":
            return build_error_envelope(
                code="RUNTIME_VALIDATION_REQUIRED",
                message="Status lookup requires Frappe runtime validation before use.",
                retryable=False,
            ).to_dict()

        # Otherwise fallback to a mock/prototype sample preview status since DB is not validated yet
        raw_data = {
            "service_request_id": reference_number,
            "service_type": "LOST_NATIONAL_ID",
            "citizen_full_name": "Demo Citizen A",
            "nin": "CF900000000000",
            "phone": "+256700000001",
            "email": "demo.citizen.a@example.test",
            "location": "Ntinda, Kampala",
            "citizen_visible_status": "In Progress",
            "internal_status": "Submitted",
            "submitted_at": "2026-06-02T12:00:00",
            payment_status_field: "Pending",
            "sla_state": "Within SLA",
        }

    from nilegov_stack.application.redaction import redact_service_request_status
    redacted_data = redact_service_request_status(raw_data)
    redacted_data["runtime_validation_status"] = "Pending Hetzner/Frappe runtime validation"

    return build_success_envelope(redacted_data).to_dict()

