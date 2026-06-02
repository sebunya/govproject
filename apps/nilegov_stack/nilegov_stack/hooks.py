# NileGov Stack App Hooks Configuration
# Digi-Verse Uganda Limited

app_name = "nilegov_stack"
app_title = "NileGov Stack"
app_publisher = "Digi-Verse Uganda Limited"
app_description = "Uganda service delivery and case-management accountability platform"
app_email = "info@digiverse.co.ug"
app_license = "mit"

# Document classes mapping (Pass 2 setup)
# DocTypes will be mapped here as active controller overrides if necessary

# Fixtures registration
# Role and custom permissions fixtures will be loaded in Pass 2
fixtures = [
    {"dt": "Role", "filters": [["name", "in", [
        "Citizen", "Service Desk Officer", "Supervisor", "Registry Liaison Officer",
        "MDA Leadership", "MDA Administrator", "System Administrator"
    ]]]}
]

# Row-Level Permissions Scaffolding (Pass 2)
permission_query_conditions = {
    "NileGov Service Request": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Citizen Profile": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Consent Record": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Evidence Document": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Case Note": "nilegov_stack.interfaces.permissions.get_permission_query_conditions",
    "NileGov Citizen Notification": "nilegov_stack.interfaces.permissions.get_permission_query_conditions"
}

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
    "NileGov Integration Simulation Log": "nilegov_stack.interfaces.permissions.has_permission"
}
