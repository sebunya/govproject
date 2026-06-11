// NileGov Payment Monitoring Report — Report Client Script
// Prototype simulation only. Not official government statistics.

frappe.query_reports["NileGov Payment Monitoring Report"] = {
    "filters": [
        {
            "fieldname": "payment_status",
            "label": __("Payment Status"),
            "fieldtype": "Select",
            "options": "\nPending\nSubmitted\nVerified\nFailed\nReversed\nCancelled"
        },
        {
            "fieldname": "reconciliation_status",
            "label": __("Reconciliation Status"),
            "fieldtype": "Select",
            "options": "\nPending Reconciliation\nReconciled\nMismatch\nRequires Review"
        }
    ],
    "onload": function(report) {
        frappe.show_alert({
            message: __("Prototype report — simulated payments only. Not official government payment data."),
            indicator: "red"
        });
    }
};
