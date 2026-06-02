// Client script for NileGov Evidence Document form view
// Digi-Verse Uganda Limited
// Prototype simulation only. No live Government registry access.
// No official NIRA, police or court verification is performed.
// Pass 11B-4B: Read-only UI helpers for evidence review.

frappe.ui.form.on('NileGov Evidence Document', {

    onload: function(frm) {
        if (!frm.is_new()) {
            frm.set_intro(
                __('⚠ Prototype document record. Verification status reflects simulated ' +
                   'officer review only. No live NIRA, police, court or official registry ' +
                   'verification is performed in this prototype environment.'),
                'orange'
            );
        }
    },

    refresh: function(frm) {
        if (frm.is_new()) return;

        var doc = frm.doc;

        // ── Status indicator ──────────────────────────────────────────────────
        var status = doc.verification_status || 'Pending';
        var vis    = doc.visibility || '';

        var colour = 'blue';
        if (status === 'Verified')                { colour = 'green'; }
        else if (status === 'Rejected')           { colour = 'red'; }
        else if (status === 'Requires Review')    { colour = 'orange'; }

        var parts = ['<b>Verification:</b> ' + status];
        if (doc.document_type) { parts.push('<b>Type:</b> ' + doc.document_type); }
        if (vis)               { parts.push('<b>Visibility:</b> ' + vis); }

        frm.dashboard.set_headline_alert(
            '<span style="color:' + colour + ';">' + parts.join(' &nbsp;|&nbsp; ') + '</span>'
        );

        // ── Context summary message ───────────────────────────────────────────
        var msgParts = [];
        if (doc.document_type)  { msgParts.push('Type: <b>' + doc.document_type + '</b>'); }
        if (doc.document_title) { msgParts.push('Title: <b>' + doc.document_title + '</b>'); }
        if (doc.upload_channel) { msgParts.push('Upload channel: <b>' + doc.upload_channel + '</b>'); }
        if (doc.uploaded_by)    { msgParts.push('Uploaded by: <b>' + doc.uploaded_by + '</b>'); }
        if (doc.visibility)     { msgParts.push('Visibility: <b>' + doc.visibility + '</b>'); }

        if (msgParts.length > 0) {
            frm.set_df_property('officer_notes', 'description',
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
