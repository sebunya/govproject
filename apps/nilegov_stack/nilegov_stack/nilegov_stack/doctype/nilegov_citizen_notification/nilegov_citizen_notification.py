# Controller for NileGov Citizen Notification
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovCitizenNotification(Document):
    def validate(self):
        if not self.notification_type:
            frappe.throw("Notification type is required.")
        if not self.channel:
            frappe.throw("Channel is required.")
        if not self.message:
            frappe.throw("Message is required.")
        if not self.delivery_status:
            frappe.throw("Delivery status is required.")
            
        required_disclaimer = "Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."
        if not self.disclaimer or required_disclaimer not in self.disclaimer:
            self.disclaimer = required_disclaimer
