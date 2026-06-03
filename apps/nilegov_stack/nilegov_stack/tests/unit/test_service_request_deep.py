# Unit Tests: Service Request Domain — Deep Coverage
# Digi-Verse Uganda Limited
# Extends test_service_request_domain_placeholder.py with full behaviour coverage.
# Prototype simulation only. No live Government registry access.

import time

import pytest

from nilegov_stack.domain.exceptions import WorkflowTransitionException
from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus
from nilegov_stack.domain.sla import SLARule, SLAState, EscalationState
from nilegov_stack.domain.value_objects import NIN


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_request(
    request_id="REQ-DEEP-001",
    reference_no="NGS-NIRA-2026-DEEP-001",
    nin_str="CF123456789012",
    citizen_name="Deep Test Citizen",
    phone="+256780000001",
    location="Kololo, Kampala",
    description="Lost ID near the park.",
    citizen_profile_id=None,
    created_at=None,
) -> ServiceRequest:
    return ServiceRequest(
        request_id=request_id,
        reference_no=reference_no,
        citizen_nin=NIN(nin_str),
        citizen_name=citizen_name,
        phone_number=phone,
        location=location,
        description=description,
        citizen_profile_id=citizen_profile_id,
        created_at=created_at,
    )


def make_sla_rule(
    rule_id="SLA-NID-001",
    service_type="SVC-LOST-NID",
    response_hours=4,
    resolution_hours=48,
    escalation_threshold_hours=72,
    at_risk_threshold_percent=70,
) -> SLARule:
    return SLARule(
        rule_id=rule_id,
        service_type=service_type,
        response_hours=response_hours,
        resolution_hours=resolution_hours,
        escalation_threshold_hours=escalation_threshold_hours,
        at_risk_threshold_percent=at_risk_threshold_percent,
    )


NOW = 1_717_000_000.0  # Fixed reference timestamp


# ─────────────────────────────────────────────────────────────────────────────
# Creation and defaults
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestCreationDefaults:
    def test_initial_status_is_submitted(self):
        r = make_request()
        assert r.status == WorkflowStatus.SUBMITTED

    def test_initial_identity_status_requires_review(self):
        r = make_request()
        assert r.identity_status == "Requires Review"

    def test_initial_payment_status_not_required(self):
        r = make_request()
        assert r.payment_status == "Not Required"

    def test_initial_payment_amount_zero(self):
        r = make_request()
        assert r.payment_amount == 0.0

    def test_initial_assignment_status_unassigned(self):
        r = make_request()
        assert r.assignment_status == "Unassigned"

    def test_initial_sla_state_not_applicable(self):
        r = make_request()
        assert r.sla_state == SLAState.NOT_APPLICABLE

    def test_initial_escalation_state_not_escalated(self):
        r = make_request()
        assert r.escalation_state == EscalationState.NOT_ESCALATED

    def test_initial_at_risk_flag_false(self):
        r = make_request()
        assert r.at_risk_flag is False

    def test_initial_overdue_flag_false(self):
        r = make_request()
        assert r.overdue_flag is False

    def test_initial_supervisor_review_false(self):
        r = make_request()
        assert r.supervisor_review_required is False

    def test_initial_notes_list_empty(self):
        r = make_request()
        assert r.notes == []

    def test_initial_events_has_one_request_submitted_event(self):
        r = make_request()
        assert len(r.events) == 1
        assert "RequestSubmitted" in type(r.events[0]).__name__

    def test_reference_no_stored(self):
        r = make_request(reference_no="NGS-NIRA-2026-ZZZZ")
        assert r.reference_no == "NGS-NIRA-2026-ZZZZ"

    def test_citizen_profile_id_optional(self):
        r = make_request(citizen_profile_id=None)
        assert r.citizen_profile_id is None

    def test_citizen_profile_id_stored_when_provided(self):
        r = make_request(citizen_profile_id="CP-DEEP-001")
        assert r.citizen_profile_id == "CP-DEEP-001"

    def test_service_type_is_none_initially(self):
        r = make_request()
        assert r.service_type is None

    def test_service_catalogue_item_id_is_none_initially(self):
        r = make_request()
        assert r.service_catalogue_item_id is None


# ─────────────────────────────────────────────────────────────────────────────
# Service type and catalogue item assignment
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceTypeAssignment:
    def test_service_type_can_be_set(self):
        r = make_request()
        r.service_type = "SVC-LOST-NID"
        assert r.service_type == "SVC-LOST-NID"

    def test_service_catalogue_item_id_can_be_set(self):
        r = make_request()
        r.service_catalogue_item_id = "CAT-NID-001"
        assert r.service_catalogue_item_id == "CAT-NID-001"


# ─────────────────────────────────────────────────────────────────────────────
# Internal notes
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestInternalNotes:
    def test_add_note_stores_note(self):
        r = make_request()
        r.add_note("Initial review complete.", "officer_demo", NOW)
        assert len(r.notes) == 1
        assert r.notes[0]["note"] == "Initial review complete."
        assert r.notes[0]["author"] == "officer_demo"

    def test_add_note_emits_note_added_event(self):
        r = make_request()
        r.clear_events()
        r.add_note("Note text.", "officer_demo", NOW)
        event_types = [type(e).__name__ for e in r.events]
        assert "NoteAdded" in event_types

    def test_add_empty_note_raises(self):
        r = make_request()
        with pytest.raises(ValueError):
            r.add_note("", "officer_demo", NOW)

    def test_multiple_notes_accumulate(self):
        r = make_request()
        r.add_note("First note.", "officer_A", NOW)
        r.add_note("Second note.", "officer_B", NOW + 10)
        assert len(r.notes) == 2


# ─────────────────────────────────────────────────────────────────────────────
# Status transitions — happy paths
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestStatusTransitions:
    def test_submitted_to_under_review(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        assert r.status == WorkflowStatus.UNDER_REVIEW

    def test_under_review_to_information_required(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.INFORMATION_REQUIRED, "officer_A", NOW + 1)
        assert r.status == WorkflowStatus.INFORMATION_REQUIRED

    def test_information_required_can_return_to_under_review(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.INFORMATION_REQUIRED, "officer_A", NOW + 1)
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW + 2)
        assert r.status == WorkflowStatus.UNDER_REVIEW

    def test_under_review_to_payment_pending(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_A", NOW + 1)
        assert r.status == WorkflowStatus.PAYMENT_PENDING

    def test_payment_pending_to_payment_verified(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_A", NOW + 1)
        r.update_status(WorkflowStatus.PAYMENT_VERIFIED, "officer_A", NOW + 2)
        assert r.status == WorkflowStatus.PAYMENT_VERIFIED

    def test_payment_verified_to_approved(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_A", NOW + 1)
        r.update_status(WorkflowStatus.PAYMENT_VERIFIED, "officer_A", NOW + 2)
        r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW + 3)
        assert r.status == WorkflowStatus.APPROVED

    def test_approved_to_ready_for_collection(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_A", NOW + 1)
        r.update_status(WorkflowStatus.PAYMENT_VERIFIED, "officer_A", NOW + 2)
        r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW + 3)
        r.update_status(WorkflowStatus.READY_FOR_COLLECTION, "officer_A", NOW + 4)
        assert r.status == WorkflowStatus.READY_FOR_COLLECTION

    def test_ready_for_collection_to_closed(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_A", NOW + 1)
        r.update_status(WorkflowStatus.PAYMENT_VERIFIED, "officer_A", NOW + 2)
        r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW + 3)
        r.update_status(WorkflowStatus.READY_FOR_COLLECTION, "officer_A", NOW + 4)
        r.update_status(WorkflowStatus.CLOSED, "officer_A", NOW + 5)
        assert r.status == WorkflowStatus.CLOSED

    def test_under_review_to_rejected(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.REJECTED, "officer_A", NOW + 1)
        assert r.status == WorkflowStatus.REJECTED

    def test_status_change_emits_status_changed_event(self):
        r = make_request()
        r.clear_events()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        event_types = [type(e).__name__ for e in r.events]
        assert "StatusChanged" in event_types


# ─────────────────────────────────────────────────────────────────────────────
# Status transitions — invalid paths (guard clauses)
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestInvalidTransitions:
    def test_submitted_to_payment_verified_raises(self):
        r = make_request()
        with pytest.raises(WorkflowTransitionException):
            r.update_status(WorkflowStatus.PAYMENT_VERIFIED, "officer_A", NOW)

    def test_submitted_to_closed_raises(self):
        r = make_request()
        with pytest.raises(WorkflowTransitionException):
            r.update_status(WorkflowStatus.CLOSED, "officer_A", NOW)

    def test_submitted_to_approved_raises(self):
        r = make_request()
        with pytest.raises(WorkflowTransitionException):
            r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW)

    def test_closed_cannot_transition_further(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_A", NOW + 1)
        r.update_status(WorkflowStatus.PAYMENT_VERIFIED, "officer_A", NOW + 2)
        r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW + 3)
        r.update_status(WorkflowStatus.READY_FOR_COLLECTION, "officer_A", NOW + 4)
        r.update_status(WorkflowStatus.CLOSED, "officer_A", NOW + 5)
        with pytest.raises(WorkflowTransitionException):
            r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW + 6)

    def test_rejected_cannot_transition_further(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.REJECTED, "officer_A", NOW + 1)
        with pytest.raises(WorkflowTransitionException):
            r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW + 2)

    def test_unknown_status_raises(self):
        r = make_request()
        with pytest.raises(WorkflowTransitionException):
            r.update_status("Mysterious Status", "officer_A", NOW)

    def test_information_required_cannot_directly_jump_to_approved(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.INFORMATION_REQUIRED, "officer_A", NOW + 1)
        with pytest.raises(WorkflowTransitionException):
            r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW + 2)

    def test_payment_pending_cannot_jump_to_approved(self):
        r = make_request()
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_A", NOW + 1)
        with pytest.raises(WorkflowTransitionException):
            r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW + 2)


# ─────────────────────────────────────────────────────────────────────────────
# Closure — SLA flags cleared on terminal states
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestClosure:
    def _closed_request(self) -> ServiceRequest:
        r = make_request(created_at=NOW)
        rule = make_sla_rule()
        r.assign_sla_rule(rule, NOW)
        r.sla_state = SLAState.OVERDUE
        r.at_risk_flag = True
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_A", NOW + 1)
        r.update_status(WorkflowStatus.PAYMENT_VERIFIED, "officer_A", NOW + 2)
        r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW + 3)
        r.update_status(WorkflowStatus.READY_FOR_COLLECTION, "officer_A", NOW + 4)
        r.update_status(WorkflowStatus.CLOSED, "officer_A", NOW + 5)
        return r

    def test_sla_state_set_to_met_on_close(self):
        r = self._closed_request()
        assert r.sla_state == SLAState.MET

    def test_at_risk_flag_cleared_on_close(self):
        r = self._closed_request()
        assert r.at_risk_flag is False

    def test_overdue_flag_cleared_on_close(self):
        r = self._closed_request()
        assert r.overdue_flag is False

    def test_sla_state_set_to_met_on_rejection(self):
        r = make_request(created_at=NOW)
        rule = make_sla_rule()
        r.assign_sla_rule(rule, NOW)
        r.sla_state = SLAState.OVERDUE
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW)
        r.update_status(WorkflowStatus.REJECTED, "officer_A", NOW + 1)
        assert r.sla_state == SLAState.MET


# ─────────────────────────────────────────────────────────────────────────────
# Assignment fields
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestAssignment:
    def test_assign_to_officer_sets_officer_id(self):
        r = make_request()
        r.assign_to_officer("officer_001", NOW)
        assert r.assigned_officer_id == "officer_001"

    def test_assign_to_officer_sets_status_to_assigned(self):
        r = make_request()
        r.assign_to_officer("officer_001", NOW)
        assert r.assignment_status == "Assigned"

    def test_assign_to_officer_emits_officer_assigned_event(self):
        r = make_request()
        r.clear_events()
        r.assign_to_officer("officer_001", NOW)
        event_types = [type(e).__name__ for e in r.events]
        assert "OfficerAssigned" in event_types

    def test_reassign_to_officer_updates_officer_and_reason(self):
        r = make_request()
        r.assign_to_officer("officer_001", NOW)
        r.reassign_to_officer("officer_002", "Officer 001 on leave.", NOW + 100)
        assert r.assigned_officer_id == "officer_002"
        assert r.reassignment_reason == "Officer 001 on leave."
        assert r.assignment_status == "Reassigned"

    def test_reassign_emits_officer_reassigned_event(self):
        r = make_request()
        r.assign_to_officer("officer_001", NOW)
        r.clear_events()
        r.reassign_to_officer("officer_002", "Workload balance.", NOW + 100)
        event_types = [type(e).__name__ for e in r.events]
        assert "OfficerReassigned" in event_types

    def test_assign_to_department_sets_queue(self):
        r = make_request()
        r.assign_to_department("Records Department", "NIN Team", NOW)
        assert r.assigned_department == "Records Department"
        assert r.assigned_team == "NIN Team"
        assert r.queue_name == "Records Department"

    def test_mark_supervisor_review_updates_status(self):
        r = make_request()
        r.assign_to_officer("officer_001", NOW)
        r.mark_supervisor_review("supervisor_001", NOW + 50)
        assert r.assignment_status == "Supervisor Review"
        assert r.supervisor_review_required is True
        assert r.assigned_supervisor_id == "supervisor_001"

    def test_return_to_officer_updates_status(self):
        r = make_request()
        r.assign_to_officer("officer_001", NOW)
        r.mark_supervisor_review("supervisor_001", NOW + 50)
        r.return_to_officer(NOW + 100)
        assert r.assignment_status == "Returned to Officer"
        assert r.supervisor_review_required is False

    def test_return_to_officer_raises_if_no_assigned_officer(self):
        r = make_request()
        with pytest.raises(ValueError):
            r.return_to_officer(NOW)

    def test_close_assignment_sets_status_closed(self):
        r = make_request()
        r.assign_to_officer("officer_001", NOW)
        r.close_assignment(NOW + 200)
        assert r.assignment_status == "Closed"


# ─────────────────────────────────────────────────────────────────────────────
# SLA fields
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestSLAFields:
    def test_assign_sla_rule_sets_rule_id(self):
        r = make_request(created_at=NOW)
        rule = make_sla_rule()
        r.assign_sla_rule(rule, NOW)
        assert r.sla_rule_id == "SLA-NID-001"

    def test_assign_sla_rule_calculates_deadlines(self):
        r = make_request(created_at=NOW)
        rule = make_sla_rule(response_hours=4, resolution_hours=48)
        r.assign_sla_rule(rule, NOW)
        assert r.response_due_at == NOW + (4 * 3600)
        assert r.resolution_due_at == NOW + (48 * 3600)

    def test_assign_sla_rule_sets_sla_state_within(self):
        r = make_request(created_at=NOW)
        rule = make_sla_rule()
        r.assign_sla_rule(rule, NOW)
        assert r.sla_state == SLAState.WITHIN_SLA

    def test_sla_evaluate_within_sla(self):
        r = make_request(created_at=NOW)
        rule = make_sla_rule(resolution_hours=48, at_risk_threshold_percent=70)
        r.assign_sla_rule(rule, NOW)
        # Check at 1 hour — well within SLA
        r.evaluate_sla_state(NOW + 3600, rule)
        assert r.sla_state == SLAState.WITHIN_SLA
        assert r.overdue_flag is False

    def test_sla_evaluate_overdue(self):
        r = make_request(created_at=NOW)
        rule = make_sla_rule(response_hours=1, resolution_hours=2, escalation_threshold_hours=4)
        r.assign_sla_rule(rule, NOW)
        # Check after resolution deadline has passed
        r.evaluate_sla_state(NOW + (3 * 3600), rule)
        assert r.sla_state == SLAState.OVERDUE
        assert r.overdue_flag is True

    def test_sla_state_met_on_closed_request(self):
        r = make_request(created_at=NOW)
        rule = make_sla_rule()
        r.assign_sla_rule(rule, NOW)
        r.sla_state = SLAState.OVERDUE
        r.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW + 1)
        r.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_A", NOW + 2)
        r.update_status(WorkflowStatus.PAYMENT_VERIFIED, "officer_A", NOW + 3)
        r.update_status(WorkflowStatus.APPROVED, "officer_A", NOW + 4)
        r.update_status(WorkflowStatus.READY_FOR_COLLECTION, "officer_A", NOW + 5)
        r.update_status(WorkflowStatus.CLOSED, "officer_A", NOW + 6)
        assert r.sla_state == SLAState.MET


# ─────────────────────────────────────────────────────────────────────────────
# Escalation fields
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestEscalation:
    def test_escalate_case_sets_escalation_state(self):
        r = make_request()
        r.escalate_case("supervisor_001", "SLA breached.", NOW)
        assert r.escalation_state == EscalationState.ESCALATED

    def test_escalate_case_sets_escalated_to(self):
        r = make_request()
        r.escalate_case("supervisor_001", "SLA breached.", NOW)
        assert r.escalated_to == "supervisor_001"

    def test_escalate_case_sets_assignment_status_supervisor_review(self):
        r = make_request()
        r.escalate_case("supervisor_001", "SLA breached.", NOW)
        assert r.assignment_status == "Supervisor Review"

    def test_escalate_case_emits_request_escalated_event(self):
        r = make_request()
        r.clear_events()
        r.escalate_case("supervisor_001", "SLA breached.", NOW)
        event_types = [type(e).__name__ for e in r.events]
        assert "RequestEscalated" in event_types

    def test_resolve_escalation_sets_resolved_state(self):
        r = make_request()
        r.escalate_case("supervisor_001", "SLA breached.", NOW)
        r.resolve_escalation(NOW + 3600)
        assert r.escalation_state == EscalationState.RESOLVED

    def test_resolve_escalation_clears_supervisor_review(self):
        r = make_request()
        r.escalate_case("supervisor_001", "SLA breached.", NOW)
        r.resolve_escalation(NOW + 3600)
        assert r.supervisor_review_required is False


# ─────────────────────────────────────────────────────────────────────────────
# Payment status fields
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestPaymentStatus:
    def test_update_payment_status_to_pending(self):
        r = make_request()
        r.update_payment_status("Pending", 50_000.0, NOW)
        assert r.payment_status == "Pending"
        assert r.payment_amount == 50_000.0

    def test_update_payment_status_to_verified(self):
        r = make_request()
        r.update_payment_status("Pending", 50_000.0, NOW)
        r.update_payment_status("Verified", 50_000.0, NOW + 100)
        assert r.payment_status == "Verified"

    def test_update_payment_status_invalid_raises(self):
        r = make_request()
        with pytest.raises(ValueError, match="Invalid payment status"):
            r.update_payment_status("Fraudulent", 50_000.0, NOW)

    def test_update_payment_emits_payment_status_changed_event(self):
        r = make_request()
        r.clear_events()
        r.update_payment_status("Pending", 50_000.0, NOW)
        event_types = [type(e).__name__ for e in r.events]
        assert "PaymentStatusChanged" in event_types


# ─────────────────────────────────────────────────────────────────────────────
# Identity verification
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestIdentityVerification:
    def test_trigger_identity_matched(self):
        r = make_request()
        r.trigger_identity_verification("Matched", "System", NOW)
        assert r.identity_status == "Matched"
        assert r.identity_by == "System"

    def test_trigger_identity_not_matched(self):
        r = make_request()
        r.trigger_identity_verification("Not Matched", "System", NOW)
        assert r.identity_status == "Not Matched"

    def test_trigger_identity_requires_review(self):
        r = make_request()
        r.trigger_identity_verification("Requires Review", "System", NOW)
        assert r.identity_status == "Requires Review"

    def test_trigger_identity_invalid_result_raises(self):
        r = make_request()
        with pytest.raises(ValueError, match="Invalid simulated"):
            r.trigger_identity_verification("Confirmed by Live NIRA", "Live System", NOW)

    def test_trigger_identity_emits_identity_check_completed_event(self):
        r = make_request()
        r.clear_events()
        r.trigger_identity_verification("Matched", "System", NOW)
        event_types = [type(e).__name__ for e in r.events]
        assert "IdentityCheckCompleted" in event_types


# ─────────────────────────────────────────────────────────────────────────────
# No live government claims
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestNoLiveGovClaims:
    def test_identity_verification_only_allows_simulated_results(self):
        """Verified results must not claim live NIRA confirmation."""
        r = make_request()
        allowed = {"Matched", "Not Matched", "Requires Review"}
        for result in allowed:
            r2 = make_request(request_id=f"R-{result}")
            r2.trigger_identity_verification(result, "SimulatedSystem", NOW)
            assert r2.identity_status == result

    def test_forbidden_live_results_are_rejected(self):
        live_claims = [
            "Confirmed by NIRA",
            "Live Registry Verified",
            "UGHub Confirmed",
            "NITA-U Verified",
        ]
        for claim in live_claims:
            r = make_request()
            with pytest.raises(ValueError):
                r.trigger_identity_verification(claim, "Live System", NOW)
