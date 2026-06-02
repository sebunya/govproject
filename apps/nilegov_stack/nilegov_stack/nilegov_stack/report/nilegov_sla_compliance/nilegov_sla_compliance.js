// NileGov SLA Compliance — Report Client Script
// Prototype simulation only. Not official government statistics.
frappe.query_reports["NileGov SLA Compliance"] = {
    "filters": [
        {
            "fieldname": "status",
            "label": __("SLA Status"),
            "fieldtype": "Select",
            "options": "\nPending\nMet\nBreached\nIn Progress"
        },
        {
            "fieldname": "breach_risk",
            "label": __("Breach Risk"),
            "fieldtype": "Select",
            "options": "\nLow\nMedium\nHigh"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype SLA report — simulated compliance data only. Not official government SLA reporting."),
            indicator: "orange"
        });
    }
};
