# Controller for NileGov Simulated Identity Verification
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovSimulatedIdentityVerification(Document):
    def validate(self):
        if not self.service_request:
            frappe.throw("Service Request link is required.")
        if not self.simulation_status:
            frappe.throw("Simulation status is required.")
        if not self.verification_source:
            frappe.throw("Verification source is required.")
        if not self.response_message:
            frappe.throw("Response message is required.")
        if not self.simulated_at:
            frappe.throw("Simulated at timestamp is required.")
            
        # Ensure simulated wording in source
        if "simulat" not in self.verification_source.lower() and "mock" not in self.verification_source.lower():
            frappe.throw("Verification source must specify that it is simulated or mock.")
            
        # Ensure correct disclaimer message is present
        required_msg = "Prototype simulation only. No live Government registry access."
        if required_msg not in self.response_message:
            frappe.throw(f"Response message must contain disclaimer: '{required_msg}'")
