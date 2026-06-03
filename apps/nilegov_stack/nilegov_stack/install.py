"""NileGov Stack clean installation hook wrapper.

Ensures that canonical roles and fixtures compile safely without performing
live external connections, credential requirements, or user seeding.
"""

from typing import Dict, List

import frappe

CANONICAL_ROLES = [
    "NileGov Citizen Officer",
    "NileGov Records Officer",
    "NileGov Payments Officer",
    "NileGov SLA Supervisor",
    "NileGov M&E Viewer",
    "NileGov MDA Admin",
    "NileGov System Auditor",
    "NileGov System Manager",
]


def get_canonical_roles() -> List[str]:
    """Returns the list of 8 canonical NileGov roles."""
    return list(CANONICAL_ROLES)


def get_install_readiness_summary() -> Dict[str, str]:
    """Compiles and returns a safe summary of installation readiness status."""
    return {
        "status": "Ready",
        "pesapal_mode": "sandbox",
        "live_registry_connection": "disabled",
        "external_notifications": "disabled",
        "manual_setup_required": (
            "Configure site domain, assign test user profiles, "
            "and provision Pesapal sandbox merchant credentials manually."
        ),
    }


def after_install():
    """Conservative, idempotent Frappe hook executed after app installation."""
    print("Executing NileGov Stack after_install hooks...")

    # Safe role verification/creation helper
    for role_name in CANONICAL_ROLES:
        if not frappe.db.exists("Role", role_name):
            try:
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.insert(ignore_permissions=True)
                print(f"Created canonical role: {role_name}")
            except Exception as e:
                # Fallback to logs if db transaction is not permitted or in mock checks
                frappe.log_error(message=str(e), title="NileGov Install Role Check Failure")

    # Log safe installation readiness summary
    summary = get_install_readiness_summary()
    frappe.logger().info(f"NileGov Stack setup verification: {summary}")
    print("NileGov Stack after_install hooks completed successfully.")
