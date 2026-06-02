# Controller for NileGov Service Catalogue DocType
# Prototype service catalogue only. Not connected to a live government service registry.

import frappe
from frappe.model.document import Document


class NileGovServiceCatalogue(Document):
    def validate(self):
        if not self.service_name:
            frappe.throw("Service name is required.")
        if not self.service_code:
            frappe.throw("Service code is required.")
        if self.default_fee_amount and float(self.default_fee_amount) < 0.0:
            frappe.throw("Default fee amount cannot be negative.")

        required_disclaimer = "Prototype service catalogue only. Not connected to a live government service registry."
        if not self.disclaimer or required_disclaimer not in self.disclaimer:
            self.disclaimer = required_disclaimer

        valid_categories = (
            "Identity Services",
            "Citizen Complaints",
            "Permit Applications",
            "Inspection Services",
            "Information Requests",
            "Other Government Services"
        )
        if self.service_category not in valid_categories:
            frappe.throw(f"Invalid service category: {self.service_category}")

        valid_statuses = (
            "Active",
            "Inactive",
            "Demo Only",
            "Retired"
        )
        if self.active_status not in valid_statuses:
            frappe.throw(f"Invalid active status: {self.active_status}")

        valid_templates = (
            "Standard Application Workflow",
            "Replacement Request Workflow",
            "Complaint Resolution Workflow",
            "Inspection Workflow",
            "Information Request Workflow"
        )
        if self.workflow_template not in valid_templates:
            frappe.throw(f"Invalid workflow template: {self.workflow_template}")

        valid_providers = (
            "Simulated",
            "Pesapal Sandbox Ready",
            "Not Applicable"
        )
        if self.default_payment_provider not in valid_providers:
            frappe.throw(f"Invalid default payment provider: {self.default_payment_provider}")
