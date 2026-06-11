// NileGov Service Delivery Executive Summary — Report Client Script
// Prototype simulation only. Not official government statistics.

frappe.query_reports["NileGov Service Delivery Executive Summary"] = {
    "filters": [
        {
            "fieldname": "service_type",
            "label": __("Service Type"),
            "fieldtype": "Link",
            "options": "NileGov Service Type"
        },
        {
            "fieldname": "internal_status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nSubmitted\nUnder Review\nInformation Required\nPayment Pending\nPayment Verified\nApproved\nReady for Collection\nRejected\nClosed"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — simulated executive summary data only. Not official government statistics."),
            indicator: "orange"
        });
    }
};
