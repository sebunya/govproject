// NileGov Audit & Integrity Report — Report Client Script
// Prototype simulation only. Not official government statistics.

frappe.query_reports["NileGov Audit & Integrity Report"] = {
    "filters": [
        {
            "fieldname": "event_type",
            "label": __("Event Type"),
            "fieldtype": "Data"
        },
        {
            "fieldname": "actor_role",
            "label": __("Actor Role"),
            "fieldtype": "Data"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — simulated audit events only. Not official government statistics."),
            indicator: "orange"
        });
    }
};
