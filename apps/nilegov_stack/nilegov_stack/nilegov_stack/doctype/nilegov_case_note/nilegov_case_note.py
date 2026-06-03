# Controller for NileGov Case Note
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovCaseNote(Document):
    def validate(self):
        if not self.note:
            frappe.throw("Note content is required.")
        if not self.created_by_user:
            frappe.throw("Created by user is required.")
