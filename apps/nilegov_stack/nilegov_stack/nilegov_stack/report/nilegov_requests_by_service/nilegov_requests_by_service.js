// NileGov Requests by Service — Report Client Script
// Prototype simulation only. Not official government statistics.
frappe.query_reports["NileGov Requests by Service"] = {
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
            "options": "\nSubmitted\nUnder Review\nApproved\nRejected\nClosed"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — fictional demo data only. Not official government statistics."),
            indicator: "orange"
        });
    }
};
