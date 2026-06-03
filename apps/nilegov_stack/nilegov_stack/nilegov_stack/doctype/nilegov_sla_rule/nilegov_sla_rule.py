# Controller for NileGov SLA Rule
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovSLARule(Document):
    def validate(self):
        if not self.service_type:
            frappe.throw("Service Type link is required.")
        if self.response_hours is None or self.response_hours <= 0:
            frappe.throw("Response hours must be greater than zero.")
        if self.resolution_hours is None or self.resolution_hours <= 0:
            frappe.throw("Resolution hours must be greater than zero.")
        if self.escalation_threshold_hours is None or self.escalation_threshold_hours < 0:
            frappe.throw("Escalation threshold hours cannot be negative.")
