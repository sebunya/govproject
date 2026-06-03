// Client script for NileGov Reporting Snapshot form view
// Digi-Verse Uganda Limited
// Prototype simulation only. Metrics are calculated from fictional demo data.
// These are NOT official government statistics.
// Pass 11B-4B: Read-only UI helpers for M&E snapshot review.

frappe.ui.form.on('NileGov Reporting Snapshot', {

    onload: function(frm) {
        if (!frm.is_new()) {
            frm.set_intro(
                __('⚠ Prototype M&E reporting snapshot. All metrics shown are calculated ' +
                   'from fictional seed data and are not official government statistics. ' +
                   'This snapshot does not represent live NileGov, NIRA, URA or any ' +
                   'Ministry performance data.'),
                'orange'
            );
        }
    },

    refresh: function(frm) {
        if (frm.is_new()) return;

        var doc = frm.doc;

        // ── Executive metric summary banner ───────────────────────────────────
        var parts = [];
        if (doc.snapshot_name)  { parts.push('<b>' + doc.snapshot_name + '</b>'); }
        if (doc.total_requests !== undefined && doc.total_requests !== null) {
            parts.push('Requests: <b>' + doc.total_requests + '</b>');
        }
        if (doc.within_sla_count !== undefined && doc.within_sla_count !== null) {
            parts.push('Within SLA: <b>' + doc.within_sla_count + '</b>');
        }
        if (doc.at_risk_count !== undefined && doc.at_risk_count !== null) {
            parts.push('At Risk: <b>' + doc.at_risk_count + '</b>');
        }
        if (doc.overdue_count !== undefined && doc.overdue_count !== null) {
            parts.push('Overdue: <b>' + doc.overdue_count + '</b>');
        }
        if (doc.escalated_count !== undefined && doc.escalated_count !== null) {
            parts.push('Escalated: <b>' + doc.escalated_count + '</b>');
        }

        var colour = 'blue';
        if (doc.overdue_count > 0 || doc.escalated_count > 0) {
            colour = 'orange';
        }

        if (parts.length > 0) {
            frm.dashboard.set_headline_alert(
                '<span style="color:' + colour + ';">' + parts.join(' &nbsp;|&nbsp; ') + '</span>'
            );
        }

        // ── Prototype disclaimer reminder ─────────────────────────────────────
        // Always reinforce the prototype context in the disclaimer field description
        frm.set_df_property('disclaimer', 'description',
            '<span style="color:red;font-weight:bold;">' +
            'These are prototype metrics only. Not official government statistics.' +
            '</span>'
        );

        // ── Payment summary helper ────────────────────────────────────────────
        var payParts = [];
        if (doc.payment_pending_count !== undefined) {
            payParts.push('Pending: <b>' + doc.payment_pending_count + '</b>');
        }
        if (doc.payment_verified_count !== undefined) {
            payParts.push('Verified: <b>' + doc.payment_verified_count + '</b>');
        }
        if (doc.payment_failed_count !== undefined) {
            payParts.push('Failed: <b>' + doc.payment_failed_count + '</b>');
        }
        if (payParts.length > 0) {
            frm.set_df_property('payment_value_summary', 'description',
                'Simulated payment metrics: ' + payParts.join(' &nbsp;·&nbsp; ')
            );
        }

        // ── Evidence summary helper ───────────────────────────────────────────
        var evParts = [];
        if (doc.evidence_complete_count !== undefined) {
            evParts.push('Complete: <b>' + doc.evidence_complete_count + '</b>');
        }
        if (doc.evidence_incomplete_count !== undefined) {
            evParts.push('Incomplete: <b>' + doc.evidence_incomplete_count + '</b>');
        }
        if (evParts.length > 0) {
            frm.set_df_property('officer_workload_summary', 'description',
                'Evidence status: ' + evParts.join(' &nbsp;·&nbsp; ')
            );
        }

        // ── Navigate to all snapshots ─────────────────────────────────────────
        frm.add_custom_button(
            __('View All Snapshots'),
            function() {
                frappe.set_route('List', 'NileGov Reporting Snapshot');
            },
            __('Navigate')
        );
    }
});
