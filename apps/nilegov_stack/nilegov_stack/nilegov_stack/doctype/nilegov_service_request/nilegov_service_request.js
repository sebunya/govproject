// Client script for NileGov Service Request form view
// Prototype simulation only. No live Government registry access.

frappe.ui.form.on('NileGov Service Request', {
    refresh: function(frm) {
        // Add simulated identity check action
        if (frm.doc.identity_status === 'Requires Review' && !frm.is_new()) {
            frm.add_custom_button(__('Trigger Simulated NIRA Verification'), function() {
                frappe.call({
                    method: 'nilegov_stack.nilegov_stack.doctype.nilegov_service_request.nilegov_service_request.run_simulated_identity_check',
                    args: {
                        request_id: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.show_alert({
                                message: __('Simulated NIRA Verification result: ' + r.message),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        }
                    }
                });
            }, __('Simulated Actions'));
        }

        // Add simulated payment check action
        if (frm.doc.payment_status === 'Pending' && !frm.is_new()) {
            frm.add_custom_button(__('Trigger Simulated Payment Verification'), function() {
                frappe.call({
                    method: 'nilegov_stack.nilegov_stack.doctype.nilegov_service_request.nilegov_service_request.verify_payment',
                    args: {
                        request_id: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.show_alert({
                                message: __('Simulated Payment Verification status: ' + r.message),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        }
                    }
                });
            }, __('Simulated Actions'));
        }
    }
});
