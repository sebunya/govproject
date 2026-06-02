// Client script for NileGov Service Request form view
// Digi-Verse Uganda Limited
// Prototype simulation only. No live Government registry access.
// Pass 11B-4A: Full action wiring for all 10 whitelisted backend methods.

// ─────────────────────────────────────────────────────────────────────────────
// Constants — must match Python whitelist path exactly
// ─────────────────────────────────────────────────────────────────────────────
const SR_MODULE = 'nilegov_stack.nilegov_stack.doctype.nilegov_service_request.nilegov_service_request';

const METHODS = {
    runSimulatedIdentityCheck : SR_MODULE + '.run_simulated_identity_check',
    verifyPayment             : SR_MODULE + '.verify_payment',
    assignOfficer             : SR_MODULE + '.assign_officer',
    reassignOfficer           : SR_MODULE + '.reassign_officer',
    assignDepartmentTeam      : SR_MODULE + '.assign_department_team',
    markSupervisorReview      : SR_MODULE + '.mark_supervisor_review',
    returnCaseToOfficer       : SR_MODULE + '.return_case_to_officer',
    evaluateSLAState          : SR_MODULE + '.evaluate_sla_state',
    escalateCase              : SR_MODULE + '.escalate_case',
    resolveEscalation         : SR_MODULE + '.resolve_escalation',
};

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Wrapper for frappe.call with standard error handling and post-action refresh.
 * @param {string}   method   - fully-qualified Python method path
 * @param {object}   args     - argument dict
 * @param {string}   successMsg - message shown on success
 * @param {string}   indicator  - 'green' | 'orange' | 'red'
 * @param {object}   frm      - current form instance
 */
function _safeCall(method, args, successMsg, indicator, frm) {
    frappe.call({
        method: method,
        args: args,
        freeze: true,
        freeze_message: __('Processing — prototype simulation only…'),
        callback: function(r) {
            if (r && r.exc) {
                frappe.msgprint({
                    title: __('Action Error'),
                    indicator: 'red',
                    message: __('The action could not be completed. This is a prototype environment — no live system was contacted.')
                });
                return;
            }
            var detail = (r && r.message) ? String(r.message) : 'OK';
            frappe.show_alert({ message: successMsg + ' (' + detail + ')', indicator: indicator || 'green' });
            frm.reload_doc();
        },
        error: function() {
            frappe.msgprint({
                title: __('Action Error'),
                indicator: 'red',
                message: __('Simulated action failed. No live system was contacted. Please try again or check the prototype setup.')
            });
        }
    });
}

/**
 * Ask for confirmation, then call backend.
 */
function _confirm(msg, method, args, successMsg, indicator, frm) {
    frappe.confirm(
        __(msg),
        function() { _safeCall(method, args, successMsg, indicator, frm); }
    );
}

// ─────────────────────────────────────────────────────────────────────────────
// Status indicator helper — renders a colour-coded banner above the form
// ─────────────────────────────────────────────────────────────────────────────
function _showStatusIndicator(frm) {
    // Remove existing indicator if any
    frm.dashboard.clear_headline();

    var status   = frm.doc.internal_status   || '';
    var slaState = frm.doc.sla_state         || '';
    var payStatus= frm.doc.payment_status    || '';
    var escState = frm.doc.escalation_status || '';

    var parts = [];
    if (status)    parts.push('<b>Status:</b> ' + status);
    if (slaState)  parts.push('<b>SLA:</b> ' + slaState);
    if (payStatus) parts.push('<b>Payment:</b> ' + payStatus);
    if (escState && escState !== 'None') parts.push('<b>Escalation:</b> ' + escState);

    if (parts.length === 0) return;

    // Choose colour based on SLA urgency
    var colour = 'blue';
    if (slaState === 'Overdue' || escState === 'Escalated') { colour = 'red'; }
    else if (slaState === 'At Risk') { colour = 'orange'; }
    else if (status === 'Closed' || status === 'Collected') { colour = 'green'; }

    frm.dashboard.set_headline_alert(
        '<span style="color:' + colour + ';">' + parts.join(' &nbsp;|&nbsp; ') + '</span>'
    );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main form event handler
// ─────────────────────────────────────────────────────────────────────────────
frappe.ui.form.on('NileGov Service Request', {

    // ── onload ────────────────────────────────────────────────────────────────
    onload: function(frm) {
        // Prototype banner — always visible
        if (!frm.is_new()) {
            frm.set_intro(
                __('⚠ Prototype workflow. Identity, payment and interoperability checks are ' +
                   'simulated unless explicitly validated in a sandbox runtime environment. ' +
                   'No live NIRA, UGHub, URA or payment gateway is contacted.'),
                'orange'
            );
        }
    },

    // ── refresh ───────────────────────────────────────────────────────────────
    refresh: function(frm) {
        if (frm.is_new()) return;

        // Status indicator banner
        _showStatusIndicator(frm);

        var doc = frm.doc;

        // ── Group A: Simulated Verification Actions ───────────────────────────
        var GROUP_SIM = __('Simulated Actions');

        // 1. Simulated Identity Check — available when identity_status suggests review needed
        if (!['Verified', 'Failed'].includes(doc.identity_status)) {
            frm.add_custom_button(
                __('Run Simulated Identity Check'),
                function() {
                    _confirm(
                        'This will run a simulated identity check using fictional NIRA data. ' +
                        'No live NIRA registry will be contacted. Proceed?',
                        METHODS.runSimulatedIdentityCheck,
                        { request_id: doc.name },
                        __('Simulated Identity Check complete'),
                        'green',
                        frm
                    );
                },
                GROUP_SIM
            );
        }

        // 2. Simulated Payment Verification — available when payment is pending
        if (doc.payment_status === 'Pending' || doc.payment_status === 'Initiated') {
            frm.add_custom_button(
                __('Run Simulated Payment Verification'),
                function() {
                    _confirm(
                        'This will run a simulated payment verification. ' +
                        'No live payment gateway or Pesapal will be contacted. Proceed?',
                        METHODS.verifyPayment,
                        { request_id: doc.name },
                        __('Simulated Payment Verification complete'),
                        'green',
                        frm
                    );
                },
                GROUP_SIM
            );
        }

        // 3. Refresh SLA State — safe read-only evaluation, always available
        frm.add_custom_button(
            __('Refresh SLA State'),
            function() {
                _safeCall(
                    METHODS.evaluateSLAState,
                    { request_id: doc.name },
                    __('SLA state refreshed'),
                    'blue',
                    frm
                );
            },
            GROUP_SIM
        );

        // ── Group B: Officer Assignment ───────────────────────────────────────
        var GROUP_ASSIGN = __('Officer Actions');

        // 4. Assign Officer — available when not yet assigned
        if (!doc.assigned_officer || doc.assignment_status === 'Unassigned') {
            frm.add_custom_button(
                __('Assign Officer'),
                function() {
                    frappe.prompt(
                        [{ label: __('Officer User ID'), fieldname: 'officer_id', fieldtype: 'Data', reqd: 1 }],
                        function(values) {
                            _confirm(
                                'Assign this request to officer "' + values.officer_id + '"?',
                                METHODS.assignOfficer,
                                { request_id: doc.name, officer_id: values.officer_id },
                                __('Officer assigned'),
                                'green',
                                frm
                            );
                        },
                        __('Assign Officer'),
                        __('Assign')
                    );
                },
                GROUP_ASSIGN
            );
        }

        // 5. Reassign Officer — available when already assigned
        if (doc.assigned_officer && doc.assignment_status !== 'Unassigned') {
            frm.add_custom_button(
                __('Reassign Officer'),
                function() {
                    frappe.prompt(
                        [
                            { label: __('New Officer User ID'), fieldname: 'new_officer_id', fieldtype: 'Data', reqd: 1 },
                            { label: __('Reason for Reassignment'), fieldname: 'reason', fieldtype: 'Small Text', reqd: 1 }
                        ],
                        function(values) {
                            _confirm(
                                'Reassign this request to officer "' + values.new_officer_id + '"? ' +
                                'The reassignment reason will be recorded.',
                                METHODS.reassignOfficer,
                                { request_id: doc.name, new_officer_id: values.new_officer_id, reason: values.reason },
                                __('Officer reassigned'),
                                'orange',
                                frm
                            );
                        },
                        __('Reassign Officer'),
                        __('Reassign')
                    );
                },
                GROUP_ASSIGN
            );
        }

        // 6. Assign Department / Team
        frm.add_custom_button(
            __('Assign Department / Team'),
            function() {
                frappe.prompt(
                    [
                        { label: __('Department'), fieldname: 'department', fieldtype: 'Data', reqd: 1 },
                        { label: __('Team (optional)'), fieldname: 'team', fieldtype: 'Data', reqd: 0 }
                    ],
                    function(values) {
                        _safeCall(
                            METHODS.assignDepartmentTeam,
                            { request_id: doc.name, department: values.department, team: values.team || null },
                            __('Department / Team assigned'),
                            'green',
                            frm
                        );
                    },
                    __('Assign Department / Team'),
                    __('Assign')
                );
            },
            GROUP_ASSIGN
        );

        // ── Group C: Supervisor / Escalation Actions ──────────────────────────
        var GROUP_SUP = __('Supervisor Actions');

        // 7. Mark for Supervisor Review
        if (doc.supervisor_review_required || doc.internal_status === 'Under Review') {
            frm.add_custom_button(
                __('Send to Supervisor Review'),
                function() {
                    frappe.prompt(
                        [{ label: __('Supervisor User ID'), fieldname: 'supervisor_id', fieldtype: 'Data', reqd: 1 }],
                        function(values) {
                            _confirm(
                                'Send this request to supervisor "' + values.supervisor_id + '" for review?',
                                METHODS.markSupervisorReview,
                                { request_id: doc.name, supervisor_id: values.supervisor_id },
                                __('Case sent to Supervisor Review'),
                                'orange',
                                frm
                            );
                        },
                        __('Supervisor Review'),
                        __('Send')
                    );
                },
                GROUP_SUP
            );
        }

        // 8. Return Case to Officer (after supervisor review)
        if (doc.assigned_supervisor && doc.internal_status === 'Under Review') {
            frm.add_custom_button(
                __('Return Case to Officer'),
                function() {
                    _confirm(
                        'Return this case from supervisor review back to the assigned officer?',
                        METHODS.returnCaseToOfficer,
                        { request_id: doc.name },
                        __('Case returned to officer'),
                        'blue',
                        frm
                    );
                },
                GROUP_SUP
            );
        }

        // 9. Escalate Case
        if (doc.escalation_status !== 'Escalated' && doc.internal_status !== 'Closed') {
            frm.add_custom_button(
                __('Escalate Case'),
                function() {
                    frappe.prompt(
                        [
                            { label: __('Supervisor User ID'), fieldname: 'supervisor_id', fieldtype: 'Data', reqd: 1 },
                            { label: __('Escalation Reason'), fieldname: 'reason', fieldtype: 'Small Text', reqd: 1 }
                        ],
                        function(values) {
                            _confirm(
                                'Escalate this case to supervisor "' + values.supervisor_id + '"? ' +
                                'This action will be audit-logged.',
                                METHODS.escalateCase,
                                { request_id: doc.name, supervisor_id: values.supervisor_id, reason: values.reason },
                                __('Case escalated'),
                                'red',
                                frm
                            );
                        },
                        __('Escalate Case'),
                        __('Escalate')
                    );
                },
                GROUP_SUP
            );
        }

        // 10. Resolve Escalation — only when actually escalated
        if (doc.escalation_status === 'Escalated') {
            frm.add_custom_button(
                __('Resolve Escalation'),
                function() {
                    _confirm(
                        'Mark this escalation as resolved? The case will return to normal processing.',
                        METHODS.resolveEscalation,
                        { request_id: doc.name },
                        __('Escalation resolved'),
                        'green',
                        frm
                    );
                },
                GROUP_SUP
            );
        }
    } // end refresh
}); // end frappe.ui.form.on
