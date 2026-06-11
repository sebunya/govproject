// NileGov Weekly Management Review Report — Report Client Script
// Prototype simulation only. All actions and decisions are based on simulated data.

frappe.query_reports["NileGov Weekly Management Review Report"] = {
    "filters": [
        {
            "fieldname": "review_period",
            "label": __("Review Period"),
            "fieldtype": "Select",
            "options": "\nWeekly\nMonthly\nQuarterly\nAnnual"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — simulated management review data only. Observations and actions are based on simulated data."),
            indicator: "orange"
        });
    }
};
