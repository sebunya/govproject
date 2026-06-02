# Controller for NileGov Integration Simulation Log
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovIntegrationSimulationLog(Document):
    def validate(self):
        if not self.integration_name:
            frappe.throw("Integration Name is required.")
        if not self.simulation_type:
            frappe.throw("Simulation Type is required.")
        if not self.status:
            frappe.throw("Status is required.")
        if not self.simulated_at:
            frappe.throw("Simulated At is required.")
        if not self.disclaimer:
            frappe.throw("Disclaimer is required.")
            
        # Ensure simulated disclaimer wording
        required_msg = "Prototype simulation only. No live Government registry access."
        if required_msg not in self.disclaimer:
            frappe.throw(f"Disclaimer field must contain exact text: '{required_msg}'")
            
        # Append-only check: Block modifications
        if not self.is_new():
            frappe.throw("Integration Simulation Logs are append-only. Modification is strictly forbidden.")
