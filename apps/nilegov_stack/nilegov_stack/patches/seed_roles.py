# Idempotent Role Seeding Patch
# Prototype simulation only. No live Government registry access.

import frappe

def execute():
    """Idempotently inserts required custom roles into the database."""
    roles = [
        "Citizen", "Service Desk Officer", "Supervisor", "Registry Liaison Officer",
        "MDA Leadership", "MDA Administrator", "System Administrator"
    ]
    for role_name in roles:
        # Check if role exists to avoid duplicates
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.insert(ignore_permissions=True)
            frappe.db.commit()
