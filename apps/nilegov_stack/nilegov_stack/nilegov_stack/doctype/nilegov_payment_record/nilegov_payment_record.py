# Controller for NileGov Payment Record
# Prototype simulation only. No live payment processed.

import frappe
from frappe.model.document import Document


class NileGovPaymentRecord(Document):
    def validate(self):
        if not self.amount or float(self.amount) < 0.0:
            frappe.throw("Payment amount must be a positive number.")
        if not self.payment_purpose:
            frappe.throw("Payment purpose is required.")
        if not self.payment_channel:
            frappe.throw("Payment channel is required.")
        if not self.payment_status:
            frappe.throw("Payment status is required.")
        if not self.verification_status:
            frappe.throw("Verification status is required.")

        required_disclaimer = "Prototype simulation only. No live payment was processed."
        if not self.disclaimer or required_disclaimer not in self.disclaimer:
            self.disclaimer = required_disclaimer
        
        # Enforce valid purposes, channels, and statuses
        valid_purposes = (
            "National ID Replacement Fee",
            "Service Processing Fee",
            "Document Replacement Fee",
            "Other Government Service Fee",
            "Not Applicable"
        )
        if self.payment_purpose not in valid_purposes:
            frappe.throw(f"Invalid payment purpose: {self.payment_purpose}")

        valid_channels = (
            "Simulated Mobile Money",
            "Simulated Card",
            "Simulated Bank",
            "Simulated Cash Office",
            "Not Applicable"
        )
        if self.payment_channel not in valid_channels:
            frappe.throw(f"Invalid payment channel: {self.payment_channel}")

        valid_statuses = (
            "Not Required",
            "Pending",
            "Submitted",
            "Verified",
            "Failed",
            "Reversed",
            "Cancelled"
        )
        if self.payment_status not in valid_statuses:
            frappe.throw(f"Invalid payment status: {self.payment_status}")

        valid_providers = (
            "Simulated",
            "Pesapal Sandbox",
            "Pesapal Live"
        )
        if self.provider and self.provider not in valid_providers:
            frappe.throw(f"Invalid provider: {self.provider}")

