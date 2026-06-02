# Controller for NileGov Audit Event
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovAuditEvent(Document):
    def validate(self):
        if not self.event_type:
            frappe.throw("Event type is required.")
        if not self.actor:
            frappe.throw("Actor link is required.")
        if not self.event_time:
            frappe.throw("Event time is required.")
        if not self.action_summary:
            frappe.throw("Action summary is required.")
            
        # Append-only check: Block modifications to existing records
        if not self.is_new():
            frappe.throw("Audit Events are append-only. Modification is strictly forbidden.")
