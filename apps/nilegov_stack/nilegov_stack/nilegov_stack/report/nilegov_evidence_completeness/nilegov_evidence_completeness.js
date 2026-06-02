// NileGov Evidence Completeness — Report Client Script
// Prototype simulation only. No official verification performed.
frappe.query_reports["NileGov Evidence Completeness"] = {
    "filters": [
        {
            "fieldname": "verification_status",
            "label": __("Verification Status"),
            "fieldtype": "Select",
            "options": "\nPending\nVerified\nRejected\nRequires Review"
        },
        {
            "fieldname": "document_type",
            "label": __("Document Type"),
            "fieldtype": "Select",
            "options": "\nNational ID\nPassport\nBirth Certificate\nProof of Residence\nPolice Report\nOther"
        },
        {
            "fieldname": "visibility",
            "label": __("Visibility"),
            "fieldtype": "Select",
            "options": "\nInternal\nCitizen-Visible"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype evidence report — simulated verification only. No official NIRA or court verification."),
            indicator: "orange"
        });
    }
};
