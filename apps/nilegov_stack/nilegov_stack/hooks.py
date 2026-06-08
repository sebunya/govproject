# NileGov Stack App Hooks Configuration
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

app_name = "nilegov_stack"
app_title = "NileGov Stack"
app_publisher = "Digi-Verse Uganda Limited"
app_description = "Uganda service delivery and case-management accountability platform"
app_email = "info@digiverse.co.ug"
app_license = "mit"

# Assets Inclusion
app_logo_url = "/assets/nilegov_stack/branding/nilegov-symbol.svg"

app_include_css = [
    "/assets/nilegov_stack/branding/css/nilegov_brand_final.css"
]

web_include_css = [
    "/assets/nilegov_stack/branding/css/nilegov_brand_final.css"
]

app_include_js = [
    "/assets/nilegov_stack/branding/js/nilegov_brand_final.js"
]

web_include_js = [
    "/assets/nilegov_stack/branding/js/nilegov_brand_final.js"
]



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
    # ── Roles ─────────────────────────────────────────────────────────────────
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
    ]]},
    # ── Workspace ─────────────────────────────────────────────────────────────
    {"dt": "Workspace", "filters": [[
        "name", "in", [
            "nilegov_case_operations",
            "nilegov_insights_reporting",
        ]
    ]]},
    # ── Reports (Pass 11B-5A) ─────────────────────────────────────────────────
    {"dt": "Report", "filters": [[
        "name", "in", [
            "NileGov Requests by Status",
            "NileGov Requests by Service",
            "NileGov SLA Compliance",
            "NileGov Officer Workload",
            "NileGov Evidence Completeness",
            "NileGov Payment Reconciliation",
            "NileGov Notification Delivery",
            "NileGov Integration Simulation Report",
            "NileGov Reporting Snapshot Summary",
            "NileGov Service Delivery Executive Summary",
            "NileGov Backlog Ageing Report",
            "NileGov Payment Monitoring Report",
            "NileGov Escalation Risk Report",
            "NileGov Audit & Integrity Report",
            "NileGov Service Catalogue Performance Report",
            "NileGov Data Quality & Exceptions Report",
            "NileGov Equity & Access Report",
            "NileGov Weekly Management Review Report",
        ]
    ]]},
    # ── Number Cards (Pass 11B-5A) ────────────────────────────────────────────
    {"dt": "Number Card", "filters": [[
        "name", "in", [
            "NileGov Total Requests",
            "NileGov Open Requests",
            "NileGov Overdue SLA Cases",
            "NileGov Escalated Cases",
            "NileGov Pending Payments",
            "NileGov Verified Payments",
            "NileGov Evidence Incomplete",
            "NileGov Simulated Notifications Sent",
            "NileGov Reporting Snapshots",
            "NileGov Closed Requests",
            "NileGov Submitted Requests",
            "NileGov Under Review Requests",
            "NileGov Approved Requests",
            "NileGov Cases Due Today",
            "NileGov Unresolved Escalations",
            "NileGov Pending Reconciliation",
            "NileGov Failed Payments",
            "NileGov Evidence Pending Verification",
            "NileGov Failed Identity Verifications",
            "NileGov Failed Notifications",
            "NileGov Integration Errors",
            "NileGov Successful Integrations",
            "NileGov Active Citizen Profiles",
            "NileGov Data Quality Exceptions",
        ]
    ]]},
    # ── Dashboard Charts (Pass 11B-5A) ────────────────────────────────────────
    {"dt": "Dashboard Chart", "filters": [[
        "name", "in", [
            "NileGov Requests by Status Chart",
            "NileGov Requests by Service Chart",
            "NileGov SLA Compliance Chart",
            "NileGov Payment Status Chart",
            "NileGov Evidence Verification Chart",
            "NileGov Notification Delivery Chart",
            "NileGov Officer Workload Chart",
            "NileGov Integration Simulation Chart",
            "NileGov Reconciliation Status Chart",
            "NileGov Escalations by Status Chart",
            "NileGov Identity Verification Status Chart",
            "NileGov Notifications by Channel Chart",
            "NileGov Audit Events by Action Chart",
            "NileGov Services by Category Chart",
            "NileGov Active Citizens by Location Chart",
            "NileGov Data Quality Exceptions Chart",
        ]
    ]]},
    # ── Dashboards (Pass 11B-5A) ──────────────────────────────────────────────
    {"dt": "Dashboard", "filters": [[
        "name", "in", [
            "NileGov Case Operations Dashboard",
            "NileGov Insights Dashboard",
        ]
    ]]},
    # ── Print Formats (Pass 11B-6B) ───────────────────────────────────────────
    {"dt": "Print Format", "filters": [[
        "name", "in", [
            "NileGov Service Request Acknowledgement Slip",
            "NileGov Lost National ID Replacement Case Summary",
            "NileGov Simulated Payment Receipt",
            "NileGov Evidence Review Sheet",
            "NileGov SLA Escalation Memo",
            "NileGov Case Closure Certificate",
            "NileGov M&E Summary Brief",
        ]
    ]]},
    # ── Notifications (Pass 11B-6C) ───────────────────────────────────────────
    {"dt": "Notification", "filters": [[
        "name", "in", [
            "NileGov Officer Assigned Alert",
            "NileGov Evidence Incomplete Alert",
            "NileGov Payment Pending Review Alert",
            "NileGov SLA At Risk Alert",
            "NileGov SLA Overdue Alert",
            "NileGov Escalation Assigned Alert",
            "NileGov Case Closed Alert",
            "NileGov Simulated Citizen Status Update",
        ]
    ]]},
    # ── Assignment Rules (Pass 11B-6D) ────────────────────────────────────────
    {"dt": "Assignment Rule", "filters": [[
        "name", "in", [
            "NileGov Submitted Request Queue Assignment",
            "NileGov Evidence Review Assignment",
            "NileGov Payment Review Assignment",
            "NileGov SLA At Risk Supervisor Assignment",
            "NileGov SLA Overdue Supervisor Assignment",
            "NileGov Escalation Review Assignment",
            "NileGov Closure Review Assignment",
        ]
    ]]},
    # ── Web Forms (Pass 11B-7B) ───────────────────────────────────────────────
    {"dt": "Web Form", "filters": [[
        "name", "in", [
            "NileGov Lost National ID Replacement Intake",
            "NileGov Evidence Supplement Metadata",
            "NileGov Citizen Consent Capture",
        ]
    ]]},
]


# ─────────────────────────────────────────────────────────────────────────────
# Installation hook — runs after bench install to seed demo data
# ─────────────────────────────────────────────────────────────────────────────
after_install = "nilegov_stack.install.after_install"

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
