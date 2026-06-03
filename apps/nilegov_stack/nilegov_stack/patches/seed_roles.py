# Idempotent Role Seeding Patch
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

import frappe

# ─────────────────────────────────────────────────────────────────────────────
# Canonical NileGov Roles (Pass 11B-2 aligned)
# These are the primary role names used across:
#   - hooks.py fixtures
#   - interfaces/permissions.py
#   - DocType JSON permission rows
#   - application/permission_policy.py
# ─────────────────────────────────────────────────────────────────────────────
NILEGOV_ROLES = [
    "NileGov Citizen Officer",
    "NileGov Records Officer",
    "NileGov Payments Officer",
    "NileGov SLA Supervisor",
    "NileGov M&E Viewer",
    "NileGov MDA Admin",
    "NileGov System Auditor",
    "NileGov System Manager",
]

# ─────────────────────────────────────────────────────────────────────────────
# Legacy alias roles — seeded for backward compatibility with any existing
# demo users created before Pass 11B-2. Not used as the primary model.
# ─────────────────────────────────────────────────────────────────────────────
LEGACY_ALIAS_ROLES = [
    "Citizen",
    "Service Desk Officer",
    "Supervisor",
    "Registry Liaison Officer",
    "MDA Leadership",
    "MDA Administrator",
    "System Administrator",
]


def execute():
    """Idempotently inserts canonical NileGov roles and legacy alias roles."""
    all_roles = NILEGOV_ROLES + LEGACY_ALIAS_ROLES
    for role_name in all_roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.insert(ignore_permissions=True)
            frappe.db.commit()
