// NileGov Notification Delivery — Report Client Script
// Prototype simulation only. No actual notifications sent.
frappe.query_reports["NileGov Notification Delivery"] = {
    "filters": [
        {
            "fieldname": "delivery_status",
            "label": __("Delivery Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nQueued\nSimulated Sent\nSimulated Failed\nCancelled\nNot Required"
        },
        {
            "fieldname": "channel",
            "label": __("Channel"),
            "fieldtype": "Select",
            "options": "\nSMS\nEmail\nIn-App"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype notification report — simulated delivery only. No real SMS/email sent."),
            indicator: "orange"
        });
    }
};
