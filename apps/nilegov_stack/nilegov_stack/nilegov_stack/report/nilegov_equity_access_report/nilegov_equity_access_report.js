// NileGov Equity & Access Report — Report Client Script
// Prototype simulation only. Not official government statistics.

frappe.query_reports["NileGov Equity & Access Report"] = {
    "filters": [
        {
            "fieldname": "location",
            "label": __("Location"),
            "fieldtype": "Data"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — simulated equity and access data only. Not official government statistics."),
            indicator: "orange"
        });
    }
};
