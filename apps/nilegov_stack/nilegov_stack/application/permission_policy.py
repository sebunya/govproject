"""NileGov role and permission policy helpers.

This module documents and tests permission assumptions before full Frappe runtime validation.
"""

PROTECTED_DOCTYPES = {
    "NileGov Audit Event",
    "NileGov Integration Simulation Log",
}

SENSITIVE_DOCTYPES = {
    "NileGov Citizen Profile",
    "NileGov Consent Record",
    "NileGov Evidence Document",
    "NileGov Payment Record",
    "NileGov Service Request",
    "NileGov SLA Event",
    "NileGov Escalation Record",
    "NileGov Audit Event",
    "NileGov Integration Simulation Log",
    "NileGov Reporting Snapshot",
    "NileGov Service Catalogue",
}

NILEGOV_ROLES = {
    "NileGov Citizen Officer",
    "NileGov Records Officer",
    "NileGov Payments Officer",
    "NileGov SLA Supervisor",
    "NileGov M&E Viewer",
    "NileGov MDA Admin",
    "NileGov System Auditor",
    "NileGov System Manager",
}

READ_ONLY_LOG_ROLES = {
    "NileGov System Auditor",
    "NileGov M&E Viewer",
    "NileGov SLA Supervisor",
    "NileGov MDA Admin",
    "NileGov System Manager",
}

PAYMENT_REVIEW_ROLES = {
    "NileGov Payments Officer",
    "NileGov System Manager",
}

EVIDENCE_REVIEW_ROLES = {
    "NileGov Records Officer",
    "NileGov System Manager",
}


def is_nilegov_role(role: str) -> bool:
    return role in NILEGOV_ROLES


def is_sensitive_doctype(doctype: str) -> bool:
    return doctype in SENSITIVE_DOCTYPES


def is_protected_doctype(doctype: str) -> bool:
    return doctype in PROTECTED_DOCTYPES


def can_modify_protected_log(role: str, doctype: str) -> bool:
    """Protected logs should not be modified through ordinary operational roles."""
    if doctype not in PROTECTED_DOCTYPES:
        return True
    return False


def can_read_protected_log(role: str, doctype: str) -> bool:
    if doctype not in PROTECTED_DOCTYPES:
        return True
    return role in READ_ONLY_LOG_ROLES


def can_review_payment(role: str) -> bool:
    return role in PAYMENT_REVIEW_ROLES


def can_review_evidence(role: str) -> bool:
    return role in EVIDENCE_REVIEW_ROLES


def role_implies_live_government_access(role: str) -> bool:
    """No prototype role should imply live registry or MDA access."""
    return False
