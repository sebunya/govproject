# NileGov Stack Permissions & Access Control Logic
# Prototype simulation only. No live Government registry access.

import frappe

def get_permission_query_conditions(user=None):
    """Enforces query-level row restrictions for NileGov DocTypes based on user roles."""
    if not user:
        user = frappe.session.user

    # If system manager or administrator, no restrictive query filters
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "Administrator" in roles or "MDA Administrator" in roles:
        return ""

    conditions = []
    
    # Citizen query isolation: can only query their own requests/notifications
    if "Citizen" in roles:
        conditions.append(f"`owner` = {frappe.db.escape(user)}")
        return " or ".join(conditions)

    # Service Desk Officer query isolation: can only query assigned requests
    if "Service Desk Officer" in roles:
        conditions.append(f"`assigned_officer` = {frappe.db.escape(user)}")
        return " or ".join(conditions)

    # Supervisor query isolation: can query escalated requests or team workloads
    if "Supervisor" in roles:
        conditions.append(f"`internal_status` = 'Escalated' or `assigned_supervisor` = {frappe.db.escape(user)}")
        return " or ".join(conditions)

    # MDA Leadership query isolation: read-only access (no specific row filters, managed by DocPerms)
    if "MDA Leadership" in roles:
        return ""

    # Default fallback: block everything
    return "0=1"


def has_permission(doc, ptype="read", user=None):
    """Evaluates document-level permissions (e.g. during saves, reads or updates)."""
    if not user:
        user = frappe.session.user

    # Administrators and MDA Admins bypass row-level checks
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "Administrator" in roles or "MDA Administrator" in roles:
        return True

    # Block write access to audit log and integration simulation logs for ordinary users
    if doc.doctype in ("NileGov Audit Event", "NileGov Integration Simulation Log"):
        if ptype in ("write", "create", "delete"):
            return False

    # Citizen document access rules
    if "Citizen" in roles:
        # Citizens can only access their own documents
        if doc.owner != user:
            return False
        # Citizens cannot access internal DocTypes (e.g. Escalation, SLA Events, Audit logs)
        if doc.doctype in (
            "NileGov SLA Rule", "NileGov SLA Event", "NileGov Escalation Record",
            "NileGov Audit Event", "NileGov Integration Simulation Log"
        ):
            return False
        # Citizens can write to their requests only in Draft or More Information Required status
        if doc.doctype == "NileGov Service Request" and ptype in ("write", "save"):
            if doc.internal_status not in ("Draft", "More Information Required"):
                return False
        return True

    # Service Desk Officer document access rules
    if "Service Desk Officer" in roles:
        # Desk Officers cannot access internal configuration rules or logs
        if doc.doctype in ("NileGov SLA Rule", "NileGov Audit Event", "NileGov Integration Simulation Log"):
            return False
        # Desk Officers can only view/edit cases assigned to them
        if hasattr(doc, "assigned_officer") and doc.assigned_officer != user:
            return False
        return True

    # Supervisor document access rules
    if "Supervisor" in roles:
        # Supervisors cannot access system audit events directly unless authorized
        if doc.doctype == "NileGov Audit Event" and ptype in ("write", "delete"):
            return False
        return True

    # MDA Leadership document access rules
    if "MDA Leadership" in roles:
        # Leadership is strictly read-only for reporting
        if ptype in ("write", "create", "delete", "save"):
            return False
        return True

    return False
