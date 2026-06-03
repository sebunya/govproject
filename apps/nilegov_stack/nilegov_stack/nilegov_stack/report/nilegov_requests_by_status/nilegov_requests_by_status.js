// NileGov Requests by Status — Report Client Script
// Prototype simulation only. Not official government statistics.
frappe.query_reports["NileGov Requests by Status"] = {
    "filters": [
        {
            "fieldname": "internal_status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nSubmitted\nUnder Review\nInformation Required\nPayment Pending\nPayment Verified\nApproved\nReady for Collection\nRejected\nClosed"
        },
        {
            "fieldname": "sla_state",
            "label": __("SLA State"),
            "fieldtype": "Select",
            "options": "\nWithin SLA\nAt Risk\nOverdue\nPaused\nMet\nNot Applicable"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — fictional demo data only. Not official government statistics."),
            indicator: "orange"
        });
    }
};
