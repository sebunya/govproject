# Controller for NileGov Service Type
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovServiceType(Document):
    def validate(self):
        if not self.service_name:
            frappe.throw("Service Name is required.")
        if not self.service_code:
            frappe.throw("Service Code is required.")
        if self.default_sla_hours is None or self.default_sla_hours <= 0:
            frappe.throw("Default SLA Hours must be greater than zero.")
