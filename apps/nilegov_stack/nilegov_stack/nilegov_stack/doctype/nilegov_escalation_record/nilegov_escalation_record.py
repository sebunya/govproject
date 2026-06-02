# Controller for NileGov Escalation Record
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovEscalationRecord(Document):
    def validate(self):
        if not self.escalation_reason:
            frappe.throw("Escalation reason is required.")
        if not self.escalated_to:
            frappe.throw("Escalated to user is required.")
        if not self.status:
            frappe.throw("Status is required.")
