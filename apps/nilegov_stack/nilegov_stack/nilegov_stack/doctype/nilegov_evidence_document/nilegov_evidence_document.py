# Controller for NileGov Evidence Document
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovEvidenceDocument(Document):
    def validate(self):
        if not self.evidence_document_id:
            frappe.throw("Evidence Document ID is required.")
        if not self.citizen_profile:
            frappe.throw("Citizen Profile is required.")
        if not self.service_request:
            frappe.throw("Service Request is required.")
        if not self.document_type:
            frappe.throw("Document Type is required.")
        if not self.document_title:
            frappe.throw("Document Title is required.")
        if not self.file:
            frappe.throw("File attachment reference is required.")
        if not self.upload_channel:
            frappe.throw("Upload Channel is required.")
        if not self.uploaded_by:
            frappe.throw("Uploaded By is required.")
        if not self.uploaded_at:
            frappe.throw("Uploaded At is required.")
        if not self.verification_status:
            frappe.throw("Verification Status is required.")
        if not self.visibility:
            frappe.throw("Visibility is required.")

        # Validate option constraints
        valid_document_types = {
            "Police Letter Placeholder",
            "Affidavit Placeholder",
            "Supporting ID Placeholder",
            "Payment Receipt Placeholder",
            "Application Form Placeholder",
            "Other Supporting Document"
        }
        if self.document_type not in valid_document_types:
            frappe.throw(f"Invalid Document Type: {self.document_type}")

        valid_upload_channels = {
            "Web Form",
            "Officer Assisted",
            "Portal",
            "Email",
            "WhatsApp",
            "Other"
        }
        if self.upload_channel not in valid_upload_channels:
            frappe.throw(f"Invalid Upload Channel: {self.upload_channel}")

        valid_verification_statuses = {
            "Submitted",
            "Under Review",
            "Accepted",
            "Rejected",
            "Requires Replacement",
            "Not Required",
            "Demo Placeholder"
        }
        if self.verification_status not in valid_verification_statuses:
            frappe.throw(f"Invalid Verification Status: {self.verification_status}")
