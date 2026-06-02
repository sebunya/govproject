# NileGov Stack App Hooks Configuration
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

app_name = "nilegov_stack"
app_title = "NileGov Stack"
app_publisher = "Digi-Verse Uganda Limited"
app_description = "Uganda service delivery and case-management accountability platform"
app_email = "info@digiverse.co.ug"
app_license = "mit"

# ─────────────────────────────────────────────────────────────────────────────
# Role Fixtures (Pass 11B-2 aligned)
#
# Canonical NileGov roles — used across permission_policy.py, seed_roles.py,
# DocType JSON permission rows, and interfaces/permissions.py.
#
# Legacy names (Citizen, Service Desk Officer, Supervisor, etc.) are NOT used
# as the primary model. They may be seeded as backward-compatible aliases only.
# ─────────────────────────────────────────────────────────────────────────────
fixtures = [
    {"dt": "Role", "filters": [[
        "name", "in", [
            "NileGov Citizen Officer",
            "NileGov Records Officer",
            "NileGov Payments Officer",
            "NileGov SLA Supervisor",
            "NileGov M&E Viewer",
            "NileGov MDA Admin",
            "NileGov System Auditor",
            "NileGov System Manager",
        ]
    ]]}
]

# ─────────────────────────────────────────────────────────────────────────────
# Installation hook — runs after bench install to seed demo data
# ─────────────────────────────────────────────────────────────────────────────
# after_install = "nilegov_stack.install.after_install"  # Pass 11B-8

# ─────────────────────────────────────────────────────────────────────────────
# Row-Level Permission Conditions (query-level isolation by role)
# ─────────────────────────────────────────────────────────────────────────────
permission_query_conditions = {
    "NileGov Service Request": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Citizen Profile": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Consent Record": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Evidence Document": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Case Note": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Citizen Notification": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
}

# ─────────────────────────────────────────────────────────────────────────────
# Document-Level Permission Guards (per-record access evaluation)
# ─────────────────────────────────────────────────────────────────────────────
has_permission = {
    "NileGov Service Request": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov Citizen Profile": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov Consent Record": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov Evidence Document": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov Simulated Identity Verification": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov Case Note": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov SLA Rule": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov SLA Event": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov Escalation Record": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov Citizen Notification": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov Audit Event": "nilegov_stack.interfaces.permissions.has_permission",
    "NileGov Integration Simulation Log": "nilegov_stack.interfaces.permissions.has_permission",
}
