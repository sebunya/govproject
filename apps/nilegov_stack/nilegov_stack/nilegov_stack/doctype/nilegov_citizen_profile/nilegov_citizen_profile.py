# Controller for NileGov Citizen Profile
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovCitizenProfile(Document):
    def validate(self):
        # Basic validation
        if not self.citizen_profile_id:
            frappe.throw("Citizen Profile ID is required.")
        if not self.full_name:
            frappe.throw("Full name is required.")
        if not self.location:
            frappe.throw("Location is required.")
        if not self.phone and not self.email:
            frappe.throw("Either phone or email must be provided.")
            
        # Preferred contact channel validation
        valid_channels = {"Phone", "Email", "Portal", "SMS", "WhatsApp", "Officer Assisted"}
        if self.preferred_contact_channel and self.preferred_contact_channel not in valid_channels:
            frappe.throw(f"Invalid preferred contact channel: {self.preferred_contact_channel}")
            
        # Status validation
        valid_statuses = {"Active", "Inactive", "Archived", "Demo Only"}
        if self.status and self.status not in valid_statuses:
            frappe.throw(f"Invalid status: {self.status}")
