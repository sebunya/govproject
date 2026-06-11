// NileGov Backlog Ageing Report — Report Client Script
// Prototype simulation only. Not official government statistics.

frappe.query_reports["NileGov Backlog Ageing Report"] = {
    "filters": [
        {
            "fieldname": "service_type",
            "label": __("Service Type"),
            "fieldtype": "Link",
            "options": "NileGov Service Type"
        },
        {
            "fieldname": "sla_state",
            "label": __("SLA State"),
            "fieldtype": "Select",
            "options": "\nWithin SLA\nAt Risk\nOverdue\nPaused\nMet"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — simulated backlog ageing data only. Not official government statistics."),
            indicator: "orange"
        });
    }
};
