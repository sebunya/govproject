# Controller for NileGov SLA Event
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovSLAEvent(Document):
    def validate(self):
        if not self.service_request:
            frappe.throw("Service Request is required.")
        if not self.event_type:
            frappe.throw("Event Type is required.")
        if not self.due_at:
            frappe.throw("Due At timestamp is required.")
        if not self.status:
            frappe.throw("Status is required.")
