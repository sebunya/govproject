# NileGov Stack Permissions & Access Control Logic
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.
#
# Pass 11B-2: Aligned to canonical NileGov-prefixed role names.
# All role checks reference the eight canonical roles defined in:
#   - application/permission_policy.py (NILEGOV_ROLES)
#   - patches/seed_roles.py (NILEGOV_ROLES)
#   - hooks.py fixtures

import frappe

# ─────────────────────────────────────────────────────────────────────────────
# Canonical role constants
# ─────────────────────────────────────────────────────────────────────────────
ROLE_CITIZEN_OFFICER = "NileGov Citizen Officer"
ROLE_RECORDS_OFFICER = "NileGov Records Officer"
ROLE_PAYMENTS_OFFICER = "NileGov Payments Officer"
ROLE_SLA_SUPERVISOR = "NileGov SLA Supervisor"
ROLE_ME_VIEWER = "NileGov M&E Viewer"
ROLE_MDA_ADMIN = "NileGov MDA Admin"
ROLE_SYSTEM_AUDITOR = "NileGov System Auditor"
ROLE_SYSTEM_MANAGER = "NileGov System Manager"

# Frappe built-in admin roles — always granted bypass
FRAPPE_ADMIN_ROLES = {"System Manager", "Administrator"}

# Roles granted full bypass (Frappe built-ins + NileGov system-level)
BYPASS_ROLES = FRAPPE_ADMIN_ROLES | {ROLE_MDA_ADMIN, ROLE_SYSTEM_MANAGER}

# DocTypes that must not be modified by ordinary operational roles
PROTECTED_DOCTYPES = {
    "NileGov Audit Event",
    "NileGov Integration Simulation Log",
}

# Write/create/delete operations — blocked on protected DocTypes for ordinary roles
PROTECTED_WRITE_PTYPES = {"write", "create", "delete", "save"}


def get_permission_query_conditions(user=None):
    """
    Enforces query-level row restrictions for NileGov DocTypes based on user roles.

    Called by Frappe for list views to filter visible records.
    Returns a SQL WHERE fragment that limits which rows the user may see.
    """
    if not user:
        user = frappe.session.user

    roles = set(frappe.get_roles(user))

    # Admin / manager bypass — no row filtering
    if roles & BYPASS_ROLES:
        return ""

    # System Auditor — read-all (no row restriction for audit access)
    if ROLE_SYSTEM_AUDITOR in roles:
        return ""

    # M&E Viewer — read-all for reporting/summary purposes
    if ROLE_ME_VIEWER in roles:
        return ""

    # SLA Supervisor — can see escalated cases and cases assigned to them
    if ROLE_SLA_SUPERVISOR in roles:
        return (
            f"`tabNileGov Service Request`.`escalation_state` = 'Escalated' "
            f"or `tabNileGov Service Request`.`assigned_supervisor` = {frappe.db.escape(user)}"
        )

    # Citizen Officer — can only see records assigned to them
    if ROLE_CITIZEN_OFFICER in roles:
        return f"`tabNileGov Service Request`.`assigned_officer` = {frappe.db.escape(user)}"

    # Records Officer — can see service requests awaiting document review
    if ROLE_RECORDS_OFFICER in roles:
        return f"`tabNileGov Service Request`.`internal_status` in ('Under Review', 'Information Required')"

    # Payments Officer — can see service requests in payment states
    if ROLE_PAYMENTS_OFFICER in roles:
        return f"`tabNileGov Service Request`.`internal_status` in ('Payment Pending', 'Payment Verified')"

    # Default: deny all
    return "0=1"


def has_permission(doc, ptype="read", user=None):
    """
    Evaluates document-level permissions for a specific record.

    Called by Frappe before opening, saving, or deleting a document.
    Returns True if the user is permitted; False otherwise.
    """
    if not user:
        user = frappe.session.user

    roles = set(frappe.get_roles(user))

    # Frappe built-in admin bypass
    if roles & FRAPPE_ADMIN_ROLES:
        return True

    # NileGov System Manager — full access
    if ROLE_SYSTEM_MANAGER in roles:
        return True

    # MDA Admin — full operational access (no individual row restriction)
    if ROLE_MDA_ADMIN in roles:
        return True

    # ── Protected log guard ──────────────────────────────────────────────────
    # No ordinary role may write/create/delete audit or simulation logs.
    if doc.doctype in PROTECTED_DOCTYPES:
        if ptype in PROTECTED_WRITE_PTYPES:
            return False

    # ── System Auditor ───────────────────────────────────────────────────────
    # Read-only access to protected logs and all operational records.
    if ROLE_SYSTEM_AUDITOR in roles:
        if ptype in PROTECTED_WRITE_PTYPES:
            return False
        return True

    # ── M&E Viewer ──────────────────────────────────────────────────────────
    # Read-only across reporting and summary DocTypes; no operational writes.
    if ROLE_ME_VIEWER in roles:
        if ptype in PROTECTED_WRITE_PTYPES:
            return False
        return True

    # ── SLA Supervisor ───────────────────────────────────────────────────────
    if ROLE_SLA_SUPERVISOR in roles:
        # Cannot write audit or integration logs (already guarded above)
        if doc.doctype in PROTECTED_DOCTYPES and ptype in PROTECTED_WRITE_PTYPES:
            return False
        return True

    # ── Citizen Officer ──────────────────────────────────────────────────────
    if ROLE_CITIZEN_OFFICER in roles:
        # Can only access records assigned to them
        if hasattr(doc, "assigned_officer") and doc.assigned_officer != user:
            return False
        # Cannot write to restricted DocTypes
        if doc.doctype in PROTECTED_DOCTYPES and ptype in PROTECTED_WRITE_PTYPES:
            return False
        # Cannot write to closed requests
        if doc.doctype == "NileGov Service Request" and ptype in ("write", "save"):
            if getattr(doc, "internal_status", None) not in (
                "Submitted", "Under Review", "Information Required"
            ):
                return False
        return True

    # ── Records Officer ──────────────────────────────────────────────────────
    if ROLE_RECORDS_OFFICER in roles:
        # Cannot access payment records
        if doc.doctype == "NileGov Payment Record" and ptype in PROTECTED_WRITE_PTYPES:
            return False
        if doc.doctype in PROTECTED_DOCTYPES and ptype in PROTECTED_WRITE_PTYPES:
            return False
        return True

    # ── Payments Officer ─────────────────────────────────────────────────────
    if ROLE_PAYMENTS_OFFICER in roles:
        # Cannot modify evidence decisions
        if doc.doctype == "NileGov Evidence Document" and ptype in PROTECTED_WRITE_PTYPES:
            return False
        if doc.doctype in PROTECTED_DOCTYPES and ptype in PROTECTED_WRITE_PTYPES:
            return False
        return True

    # Default: deny
    return False
