// NileGov Integration Simulation Report — Report Client Script
// Prototype simulation only. No live government registry contacted.
frappe.query_reports["NileGov Integration Simulation Report"] = {
    "filters": [
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nSuccess\nFailure"
        },
        {
            "fieldname": "integration_name",
            "label": __("Integration Name"),
            "fieldtype": "Data"
        },
        {
            "fieldname": "simulation_type",
            "label": __("Simulation Type"),
            "fieldtype": "Data"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype integration log — simulated calls only. No live NIRA, UGHub, URA or government registry contacted."),
            indicator: "orange"
        });
    }
};
