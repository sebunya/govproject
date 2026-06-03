# Controller for NileGov Consent Record
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovConsentRecord(Document):
    def validate(self):
        if not self.consent_record_id:
            frappe.throw("Consent Record ID is required.")
        if not self.citizen_profile:
            frappe.throw("Citizen Profile link is required.")
        if not self.consent_purpose:
            frappe.throw("Consent purpose is required.")
        if not self.consent_channel:
            frappe.throw("Consent channel is required.")
        if not self.consent_status:
            frappe.throw("Consent status is required.")
            
        # Validate purpose options
        valid_purposes = {
            "Service Request Processing",
            "Simulated Identity Verification",
            "Simulated Payment Verification",
            "Status Notifications",
            "Future MDA Integration Readiness"
        }
        if self.consent_purpose not in valid_purposes:
            frappe.throw(f"Invalid consent purpose: {self.consent_purpose}")
            
        # Validate status options
        valid_statuses = {"Granted", "Withdrawn", "Expired", "Not Required", "Pending"}
        if self.consent_status not in valid_statuses:
            frappe.throw(f"Invalid consent status: {self.consent_status}")
            
        # Validate channel options
        valid_channels = {"Web Form", "Officer Assisted", "Portal", "Email", "Phone", "WhatsApp", "Other"}
        if self.consent_channel not in valid_channels:
            frappe.throw(f"Invalid consent channel: {self.consent_channel}")
