// Client script for NileGov Payment Record form view
// Digi-Verse Uganda Limited
// Prototype simulation only. This is NOT live payment processing.
// No real money is moved. No Pesapal live keys are used.
// Pass 11B-4B: Read-only UI helpers for payment review.

frappe.ui.form.on('NileGov Payment Record', {

    onload: function(frm) {
        if (!frm.is_new()) {
            frm.set_intro(
                __('⚠ Simulated payment record. This prototype does not process real payments. ' +
                   'No live Pesapal, mobile money or card gateway is contacted. ' +
                   'All payment status values are sandbox-only and not live payment clearances.'),
                'orange'
            );
        }
    },

    refresh: function(frm) {
        if (frm.is_new()) return;

        var doc = frm.doc;

        // ── Status indicator ──────────────────────────────────────────────────
        var payStatus    = doc.payment_status || 'Pending';
        var verifyStatus = doc.verification_status || '';
        var receiptStatus= doc.receipt_status || '';

        var colour = 'blue';
        if (payStatus === 'Verified' || verifyStatus === 'Verified') { colour = 'green'; }
        else if (payStatus === 'Failed')                             { colour = 'red'; }
        else if (payStatus === 'Pending' || payStatus === 'Initiated') { colour = 'orange'; }

        var parts = ['<b>Payment:</b> ' + payStatus];
        if (verifyStatus) { parts.push('<b>Verification:</b> ' + verifyStatus); }
        if (receiptStatus){ parts.push('<b>Receipt:</b> ' + receiptStatus); }

        frm.dashboard.set_headline_alert(
            '<span style="color:' + colour + ';">' + parts.join(' &nbsp;|&nbsp; ') + '</span>'
        );

        // ── Context summary message ───────────────────────────────────────────
        var summaryParts = [];
        if (doc.payment_purpose) {
            summaryParts.push('Purpose: <b>' + doc.payment_purpose + '</b>');
        }
        if (doc.amount && doc.currency) {
            summaryParts.push('Amount: <b>' + doc.currency + ' ' + doc.amount + '</b> (simulated)');
        }
        if (doc.provider) {
            summaryParts.push('Provider: <b>' + doc.provider + '</b>');
        }
        if (doc.provider_mode) {
            summaryParts.push('Mode: <b>' + doc.provider_mode + '</b>');
        }
        if (doc.payment_channel) {
            summaryParts.push('Channel: <b>' + doc.payment_channel + '</b>');
        }
        if (doc.simulated_transaction_reference) {
            summaryParts.push('Ref: <b>' + doc.simulated_transaction_reference + '</b>');
        }

        if (summaryParts.length > 0) {
            frm.set_df_property('failure_reason', 'description',
                summaryParts.join(' &nbsp;·&nbsp; ')
            );
        }

        // ── Navigation: jump to linked Service Request ────────────────────────
        if (doc.service_request) {
            frm.add_custom_button(
                __('View Linked Service Request'),
                function() {
                    frappe.set_route('Form', 'NileGov Service Request', doc.service_request);
                },
                __('Navigate')
            );
        }

        // ── Navigation: jump to linked Citizen Profile ────────────────────────
        if (doc.citizen_profile) {
            frm.add_custom_button(
                __('View Citizen Profile'),
                function() {
                    frappe.set_route('Form', 'NileGov Citizen Profile', doc.citizen_profile);
                },
                __('Navigate')
            );
        }
    }
});
