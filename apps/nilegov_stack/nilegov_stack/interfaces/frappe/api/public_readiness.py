# Custom REST APIs for NileGov citizen-facing and interoperability readiness
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external connection claimed.
#

import frappe
from nilegov_stack.application.build_api_envelope import build_success_envelope

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
