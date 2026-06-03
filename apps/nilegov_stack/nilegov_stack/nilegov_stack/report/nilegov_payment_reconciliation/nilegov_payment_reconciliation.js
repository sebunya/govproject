// NileGov Payment Reconciliation — Report Client Script
// Prototype simulation only. Not live payment clearance. No real money moved.
frappe.query_reports["NileGov Payment Reconciliation"] = {
    "filters": [
        {
            "fieldname": "payment_status",
            "label": __("Payment Status"),
            "fieldtype": "Select",
            "options": "\nNot Required\nPending\nVerified\nFailed"
        },
        {
            "fieldname": "verification_status",
            "label": __("Verification Status"),
            "fieldtype": "Select",
            "options": "\nPending\nVerified\nFailed"
        },
        {
            "fieldname": "payment_channel",
            "label": __("Payment Channel"),
            "fieldtype": "Select",
            "options": "\nMobile Money\nBank Transfer\nCard\nCash"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype payment report — simulated sandbox transactions only. Not live payment clearance. No real money moved."),
            indicator: "red"
        });
    }
};
