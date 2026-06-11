// Client script for NileGov Management Review Note form view
// Digi-Verse Uganda Limited
// Prototype simulation only. All actions and decisions are based on simulated data.

frappe.ui.form.on('NileGov Management Review Note', {
    onload: function(frm) {
        frm.set_intro(
            __('⚠ Prototype Management Review Note. All observations, actions, and decisions are ' +
               'based on simulated prototype data. This form does not connect to live government ' +
               'ministry systems or official compliance channels.'),
            'orange'
        );
    },

    refresh: function(frm) {
        if (frm.is_new()) return;

        // Display summary alert on dashboard
        var doc = frm.doc;
        var parts = [];
        if (doc.review_period) { parts.push('Period: <b>' + doc.review_period + '</b>'); }
        if (doc.review_date) { parts.push('Date: <b>' + doc.review_date + '</b>'); }
        if (doc.follow_up_status) { parts.push('Follow-up Status: <b>' + doc.follow_up_status + '</b>'); }

        if (parts.length > 0) {
            frm.dashboard.set_headline_alert(
                '<span style="color:blue;">' + parts.join(' &nbsp;|&nbsp; ') + '</span>'
            );
        }
    }
});
