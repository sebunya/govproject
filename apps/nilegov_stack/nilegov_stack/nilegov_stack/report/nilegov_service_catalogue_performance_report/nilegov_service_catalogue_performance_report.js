// NileGov Service Catalogue Performance Report — Report Client Script
// Prototype simulation only. Not official government statistics.

frappe.query_reports["NileGov Service Catalogue Performance Report"] = {
    "filters": [
        {
            "fieldname": "service_category",
            "label": __("Service Category"),
            "fieldtype": "Select",
            "options": "\nIdentity Documents\nBusiness Licensing\nTravel & Permits\nOther"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — simulated service catalogue data only. Not official government statistics."),
            indicator: "orange"
        });
    }
};
