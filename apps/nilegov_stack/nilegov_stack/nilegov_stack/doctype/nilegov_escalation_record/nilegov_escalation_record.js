// Client script for NileGov Escalation Record form view
// Digi-Verse Uganda Limited
// Prototype simulation only. Escalation records reflect simulated workflow only.
// Pass 11B-4B: Read-only UI helpers for escalation review.

frappe.ui.form.on('NileGov Escalation Record', {

    onload: function(frm) {
        if (!frm.is_new()) {
            frm.set_intro(
                __('⚠ Prototype escalation record. This reflects simulated supervisor workflow ' +
                   'in the NileGov prototype. No live Ministry of Internal Affairs or ' +
                   'government MDA escalation system is contacted.'),
                'orange'
            );
        }
    },

    refresh: function(frm) {
        if (frm.is_new()) return;

        var doc = frm.doc;

        // ── Status indicator ──────────────────────────────────────────────────
        var status    = doc.status || 'Open';
        var decision  = doc.supervisor_decision || '';

        var colour = 'orange';
        if (status === 'Resolved')           { colour = 'green'; }
        else if (status === 'Escalated')     { colour = 'red'; }
        else if (status === 'Open')          { colour = 'orange'; }

        var parts = ['<b>Escalation Status:</b> ' + status];
        if (decision && decision !== 'None') {
            parts.push('<b>Supervisor Decision:</b> ' + decision);
        }
        if (doc.escalated_to) {
            parts.push('<b>Assigned To:</b> ' + doc.escalated_to);
        }

        frm.dashboard.set_headline_alert(
            '<span style="color:' + colour + ';">' + parts.join(' &nbsp;|&nbsp; ') + '</span>'
        );

        // ── Context summary message ───────────────────────────────────────────
        var msgParts = [];
        if (doc.escalation_reason) {
            msgParts.push('Reason: <b>' + doc.escalation_reason + '</b>');
        }
        if (doc.escalated_by) {
            msgParts.push('Raised by: <b>' + doc.escalated_by + '</b>');
        }
        if (doc.escalated_to) {
            msgParts.push('Assigned to: <b>' + doc.escalated_to + '</b>');
        }
        if (doc.escalated_at) {
            msgParts.push('Escalated at: <b>' + doc.escalated_at + '</b>');
        }
        if (doc.resolved_at) {
            msgParts.push('Resolved at: <b>' + doc.resolved_at + '</b>');
        }

        if (msgParts.length > 0) {
            frm.set_df_property('supervisor_decision', 'description',
                msgParts.join(' &nbsp;·&nbsp; ')
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

        // ── Informational note for supervisors ────────────────────────────────
        if (status === 'Escalated') {
            frappe.show_alert({
                message: __('This case is currently escalated. Use the Service Request form ' +
                            'to escalate, return or resolve it via the Supervisor Actions group.'),
                indicator: 'orange'
            });
        }
    }
});
