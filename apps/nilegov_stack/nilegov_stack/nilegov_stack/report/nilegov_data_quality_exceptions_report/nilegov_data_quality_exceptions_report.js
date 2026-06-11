// NileGov Data Quality & Exceptions Report — Report Client Script
// Prototype simulation only. Not official government statistics.

frappe.query_reports["NileGov Data Quality & Exceptions Report"] = {
    "filters": [
        {
            "fieldname": "service_type",
            "label": __("Service Type"),
            "fieldtype": "Link",
            "options": "NileGov Service Type"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — simulated data quality exceptions data only. Not official government statistics."),
            indicator: "orange"
        });
    }
};
