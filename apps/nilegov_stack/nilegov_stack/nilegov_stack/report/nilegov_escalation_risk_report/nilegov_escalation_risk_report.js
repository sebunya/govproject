// NileGov Escalation Risk Report — Report Client Script
// Prototype simulation only. Not official government statistics.

frappe.query_reports["NileGov Escalation Risk Report"] = {
    "filters": [
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nPending\nResolved"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — simulated escalations data only. Not official government statistics."),
            indicator: "orange"
        });
    }
};
