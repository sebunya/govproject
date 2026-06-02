// NileGov Officer Workload — Report Client Script
// Prototype simulation only. Not official MDA staffing or performance data.
frappe.query_reports["NileGov Officer Workload"] = {
    "filters": [
        {
            "fieldname": "assigned_officer",
            "label": __("Officer"),
            "fieldtype": "Link",
            "options": "User"
        },
        {
            "fieldname": "internal_status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nSubmitted\nUnder Review\nApproved\nRejected\nClosed"
        },
        {
            "fieldname": "sla_state",
            "label": __("SLA State"),
            "fieldtype": "Select",
            "options": "\nWithin SLA\nAt Risk\nOverdue"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype workload report — fictional demo data. Not official MDA staffing data."),
            indicator: "orange"
        });
    }
};
