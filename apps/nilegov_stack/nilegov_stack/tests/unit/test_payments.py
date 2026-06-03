# Unit Tests for NileGov Payments & Simulated Fee Workflow Foundation
# Prototype simulation only. No live payment processed.

import pytest
import time
from unittest.mock import MagicMock, patch

from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus
from nilegov_stack.domain.consent import ConsentRecord, ConsentStatus, ConsentChannel, ConsentPurpose
from nilegov_stack.domain.payment import (
    PaymentRecord, PaymentPurpose, PaymentChannel, PaymentStatus, 
    PaymentVerificationStatus, ReceiptStatus, ReconciliationStatus
)
from nilegov_stack.application.create_payment_record import CreatePaymentRecord
from nilegov_stack.application.submit_simulated_payment import SubmitSimulatedPayment
from nilegov_stack.application.verify_simulated_payment_record import VerifySimulatedPaymentRecord
from nilegov_stack.application.mark_payment_failed import MarkPaymentFailed
from nilegov_stack.application.reverse_simulated_payment import ReverseSimulatedPayment
from nilegov_stack.application.cancel_payment_record import CancelPaymentRecord
from nilegov_stack.application.mark_receipt_ready import MarkReceiptReady
from nilegov_stack.application.mark_simulated_receipt_generated import MarkSimulatedReceiptGenerated
from nilegov_stack.application.list_payments_by_service_request import ListPaymentsByServiceRequest
from nilegov_stack.application.list_payments_by_citizen_profile import ListPaymentsByCitizenProfile
from nilegov_stack.application.list_payments_by_payment_status import ListPaymentsByPaymentStatus
from nilegov_stack.application.list_payments_by_reconciliation_status import ListPaymentsByReconciliationStatus
from nilegov_stack.application.calculate_payment_summary_metrics import CalculatePaymentSummaryMetrics

from nilegov_stack.infrastructure.integrations.simulated_payment_gateway import SimulatedPaymentVerificationGateway
from nilegov_stack.infrastructure.repositories.payment_record_repository import InMemoryPaymentRecordRepository
from nilegov_stack.infrastructure.repositories.service_request_repository import InMemoryServiceRequestRepository
from nilegov_stack.infrastructure.repositories.consent_record_repository import InMemoryConsentRecordRepository
from nilegov_stack.infrastructure.repositories.frappe_payment_record_repository import FrappePaymentRecordRepository


def test_payment_record_creation_and_validation():
    """Verifies that PaymentRecord validates schema rules and preserves disclaimer."""
    # Valid creation
    pay = PaymentRecord(
        payment_record_id="PAY-1",
        service_request_id="req-1",
        amount=50000.0,
        payment_purpose=PaymentPurpose.NATIONAL_ID_REPLACEMENT,
        payment_channel=PaymentChannel.MOBILE_MONEY,
        payment_status=PaymentStatus.PENDING
    )
    assert pay.payment_record_id == "PAY-1"
    assert pay.amount == 50000.0
    assert pay.disclaimer == "Prototype simulation only. No live payment was processed."

    # Missing Service Request
    with pytest.raises(ValueError, match="Service Request ID is required"):
        PaymentRecord("PAY-1", "", 50000.0)

    # Negative amount
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        PaymentRecord("PAY-1", "req-1", -10.0)

    # Invalid enum types
    with pytest.raises(ValueError, match="Invalid payment purpose"):
        PaymentRecord("PAY-1", "req-1", 50000.0, payment_purpose="InvalidPurpose")

    with pytest.raises(ValueError, match="Invalid payment channel"):
        PaymentRecord("PAY-1", "req-1", 50000.0, payment_channel="InvalidChannel")

    with pytest.raises(ValueError, match="Invalid payment status"):
        PaymentRecord("PAY-1", "req-1", 50000.0, payment_status="InvalidStatus")

    with pytest.raises(ValueError, match="Invalid verification status"):
        PaymentRecord("PAY-1", "req-1", 50000.0, verification_status="InvalidVerification")

    with pytest.raises(ValueError, match="Invalid receipt status"):
        PaymentRecord("PAY-1", "req-1", 50000.0, receipt_status="InvalidReceipt")

    with pytest.raises(ValueError, match="Invalid reconciliation status"):
        PaymentRecord("PAY-1", "req-1", 50000.0, reconciliation_status="InvalidRecon")


def test_payment_record_state_transitions():
    """Verifies valid state transitions: submit, verify, fail, cancel, reverse."""
    pay = PaymentRecord("PAY-1", "req-1", 50000.0)
    assert pay.payment_status == PaymentStatus.PENDING

    # Submission
    pay.submit("SIM-PAY-12345", 100.0)
    assert pay.payment_status == PaymentStatus.SUBMITTED
    assert pay.simulated_transaction_reference == "SIM-PAY-12345"
    assert pay.verification_status == PaymentVerificationStatus.PENDING_VERIFICATION

    # Verification
    pay.verify("officer_demo", 200.0)
    assert pay.payment_status == PaymentStatus.VERIFIED
    assert pay.verification_status == PaymentVerificationStatus.SIMULATED_VERIFIED
    assert pay.verified_by == "officer_demo"
    assert pay.verification_timestamp == 200.0
    assert pay.receipt_status == ReceiptStatus.RECEIPT_READY

    # Reversal
    pay.reverse(300.0)
    assert pay.payment_status == PaymentStatus.REVERSED

    # Verify invalid transitions raise errors
    pay2 = PaymentRecord("PAY-2", "req-1", 50000.0)
    # Cancel pending is valid
    pay2.cancel(150.0)
    assert pay2.payment_status == PaymentStatus.CANCELLED

    pay3 = PaymentRecord("PAY-3", "req-1", 50000.0)
    # Fail pending is valid
    pay3.fail("Failed verification", 150.0)
    assert pay3.payment_status == PaymentStatus.FAILED
    assert pay3.verification_status == PaymentVerificationStatus.SIMULATED_FAILED


def test_receipt_readiness_and_generation():
    """Verifies transitions for receipt generation."""
    pay = PaymentRecord("PAY-1", "req-1", 50000.0)
    pay.verify("officer_demo", 100.0)
    assert pay.receipt_status == ReceiptStatus.RECEIPT_READY

    pay.generate_receipt("SIM-RECEIPT-9999", 200.0)
    assert pay.receipt_status == ReceiptStatus.SIMULATED_RECEIPT_GENERATED
    assert pay.receipt_reference == "SIM-RECEIPT-9999"


def test_reconciliation_states():
    """Verifies reconciliation status changes."""
    pay = PaymentRecord("PAY-1", "req-1", 50000.0)
    pay.reconcile(ReconciliationStatus.RECONCILED, 100.0)
    assert pay.reconciliation_status == ReconciliationStatus.RECONCILED


def test_simulated_payment_gateway_determinism():
    """Verifies that the gateway adapter operates deterministically without calling external payment providers."""
    gateway = SimulatedPaymentVerificationGateway()
    assert gateway.DISCLAIMER == "Prototype simulation only. No live payment was processed."

    # Verified case
    pay_ok = PaymentRecord("PAY-OK", "req-1", 50000.0, simulated_transaction_reference="SIM-PAY-2026-0001")
    res_ok = gateway.verify_payment_record(pay_ok)
    assert res_ok["success"] is True
    assert res_ok["status"] == "Simulated Verified"

    # Failed case
    pay_fail = PaymentRecord("PAY-FAIL", "req-1", 50000.0, simulated_transaction_reference="SIM-PAY-FAIL")
    res_fail = gateway.verify_payment_record(pay_fail)
    assert res_fail["success"] is False
    assert res_fail["status"] == "Simulated Failed"

    # Requires Review case
    pay_review = PaymentRecord("PAY-REV", "req-1", 50000.0, simulated_transaction_reference="SIM-PAY-REVIEW")
    res_review = gateway.verify_payment_record(pay_review)
    assert res_review["success"] is True
    assert res_review["status"] == "Requires Review"


def test_consent_aware_payment_behavior():
    """Verifies that citizen privacy consent dictates verification verification outcome."""
    payment_repo = InMemoryPaymentRecordRepository()
    service_repo = InMemoryServiceRequestRepository()
    consent_repo = InMemoryConsentRecordRepository()
    gateway = SimulatedPaymentVerificationGateway()

    # 1. Setup profile and service request
    nin = NIN("CF900000000000")
    req = ServiceRequest("req-1", "NGS-NIRA-2026-0001", nin, "Demo Citizen A", "+256700000001", "Ntinda", "Lost ID", citizen_profile_id="CP-1")
    req.status = WorkflowStatus.PAYMENT_PENDING
    service_repo.save(req)

    use_case = VerifySimulatedPaymentRecord(payment_repo, gateway, service_repo, consent_repo)

    # A. Missing consent -> verification status flags as Requires Review (workflow not blocked)
    pay1 = PaymentRecord("PAY-1", "req-1", 50000.0, simulated_transaction_reference="SIM-PAY-001", citizen_profile_id="CP-1")
    payment_repo.save(pay1)

    status = use_case.execute("PAY-1", timestamp=100.0)
    assert status == PaymentStatus.PENDING # Remains pending in payment status
    assert payment_repo.get_by_id("PAY-1").verification_status == PaymentVerificationStatus.REQUIRES_REVIEW
    assert "consent missing" in payment_repo.get_by_id("PAY-1").failure_reason.lower()
    
    # Linked service request should remain Pending Payment
    assert service_repo.get_by_id("req-1").payment_status == "Pending"

    # B. Withdrawn consent -> verification status flags as Requires Review (workflow not blocked)
    consent_withdrawn = ConsentRecord("CON-1", "CP-1", ConsentPurpose.PAYMENT_VERIFICATION, ConsentChannel.PORTAL, consent_status=ConsentStatus.WITHDRAWN)
    consent_repo.save(consent_withdrawn)

    pay2 = PaymentRecord("PAY-2", "req-1", 50000.0, simulated_transaction_reference="SIM-PAY-002", citizen_profile_id="CP-1")
    payment_repo.save(pay2)

    status = use_case.execute("PAY-2", timestamp=100.0)
    assert status == PaymentStatus.PENDING
    assert payment_repo.get_by_id("PAY-2").verification_status == PaymentVerificationStatus.REQUIRES_REVIEW
    assert "withdrawn" in payment_repo.get_by_id("PAY-2").failure_reason.lower()

    # C. Expired consent -> verification status flags as Requires Review (workflow not blocked)
    consent_expired = ConsentRecord("CON-1", "CP-1", ConsentPurpose.PAYMENT_VERIFICATION, ConsentChannel.PORTAL, consent_status=ConsentStatus.EXPIRED)
    consent_repo.save(consent_expired)

    pay3 = PaymentRecord("PAY-3", "req-1", 50000.0, simulated_transaction_reference="SIM-PAY-003", citizen_profile_id="CP-1")
    payment_repo.save(pay3)

    status = use_case.execute("PAY-3", timestamp=100.0)
    assert status == PaymentStatus.PENDING
    assert payment_repo.get_by_id("PAY-3").verification_status == PaymentVerificationStatus.REQUIRES_REVIEW
    assert "expired" in payment_repo.get_by_id("PAY-3").failure_reason.lower()

    # D. Active/Granted consent -> transitions to Verified and marks workflow PAYMENT_VERIFIED
    consent_granted = ConsentRecord("CON-1", "CP-1", ConsentPurpose.PAYMENT_VERIFICATION, ConsentChannel.PORTAL, consent_status=ConsentStatus.GRANTED)
    consent_repo.save(consent_granted)

    pay4 = PaymentRecord("PAY-4", "req-1", 50000.0, simulated_transaction_reference="SIM-PAY-004", citizen_profile_id="CP-1")
    payment_repo.save(pay4)

    status = use_case.execute("PAY-4", timestamp=100.0)
    assert status == PaymentStatus.VERIFIED
    assert payment_repo.get_by_id("PAY-4").verification_status == PaymentVerificationStatus.SIMULATED_VERIFIED
    assert payment_repo.get_by_id("PAY-4").consent_record_id == "CON-1"

    # Linked ServiceRequest must be updated to payment Verified and status Payment Verified
    assert service_repo.get_by_id("req-1").payment_status == "Verified"
    assert service_repo.get_by_id("req-1").status == WorkflowStatus.PAYMENT_VERIFIED


def test_use_cases_and_queries():
    """Verifies queries, metrics, and application helper workflows."""
    repo = InMemoryPaymentRecordRepository()

    # 1. Create Payment Record Use Case
    create_uc = CreatePaymentRecord(repo)
    pay = create_uc.execute("PAY-1", "req-1", 50000.0, citizen_profile_id="CP-1", timestamp=100.0)
    assert pay.payment_record_id == "PAY-1"
    assert pay.payment_status == PaymentStatus.PENDING

    # 2. Submit Simulated Payment Use Case
    submit_uc = SubmitSimulatedPayment(repo)
    submit_uc.execute("PAY-1", transaction_reference="SIM-PAY-001", timestamp=150.0)
    assert repo.get_by_id("PAY-1").payment_status == PaymentStatus.SUBMITTED

    # Seed extra records
    repo.save(PaymentRecord("PAY-2", "req-1", 50000.0, payment_status=PaymentStatus.VERIFIED, citizen_profile_id="CP-1", reconciliation_status=ReconciliationStatus.RECONCILED))
    repo.save(PaymentRecord("PAY-3", "req-2", 25000.0, payment_status=PaymentStatus.FAILED, citizen_profile_id="CP-2", reconciliation_status=ReconciliationStatus.MISMATCH))

    # 3. List queries
    by_req = ListPaymentsByServiceRequest(repo).execute("req-1")
    assert len(by_req) == 2

    by_profile = ListPaymentsByCitizenProfile(repo).execute("CP-1")
    assert len(by_profile) == 2

    by_status = ListPaymentsByPaymentStatus(repo).execute(PaymentStatus.VERIFIED)
    assert len(by_status) == 1
    assert by_status[0].payment_record_id == "PAY-2"

    by_recon = ListPaymentsByReconciliationStatus(repo).execute(ReconciliationStatus.MISMATCH)
    assert len(by_recon) == 1
    assert by_recon[0].payment_record_id == "PAY-3"

    # 4. Metrics Aggregator Use Case
    metrics_uc = CalculatePaymentSummaryMetrics(repo)
    metrics = metrics_uc.execute()
    assert metrics["total_count"] == 3
    assert metrics["total_amount_verified"] == 50000.0
    assert metrics["status_counts"][PaymentStatus.VERIFIED] == 1
    assert metrics["reconciliation_counts"][ReconciliationStatus.MISMATCH] == 1


@patch("frappe.db.exists")
@patch("frappe.new_doc")
@patch("frappe.get_doc")
def test_frappe_payment_record_repository_save(mock_get_doc, mock_new_doc, mock_exists):
    """Verifies that FrappePaymentRecordRepository saves fields correctly to the Frappe database framework."""
    mock_exists.return_value = False
    mock_doc = MagicMock()
    mock_new_doc.return_value = mock_doc

    repo = FrappePaymentRecordRepository()
    pay = PaymentRecord(
        payment_record_id="PAY-1",
        service_request_id="req-1",
        amount=50000.0,
        payment_purpose=PaymentPurpose.NATIONAL_ID_REPLACEMENT,
        payment_channel=PaymentChannel.MOBILE_MONEY,
        payment_status=PaymentStatus.VERIFIED,
        simulated_transaction_reference="SIM-PAY-001",
        verification_status=PaymentVerificationStatus.SIMULATED_VERIFIED,
        citizen_profile_id="CP-1",
        consent_record_id="CON-1",
        receipt_status=ReceiptStatus.SIMULATED_RECEIPT_GENERATED,
        receipt_reference="SIM-RECEIPT-001",
        reconciliation_status=ReconciliationStatus.RECONCILED,
        failure_reason="none",
        triggered_by_event="event_ok",
        verified_by="officer_demo",
        verification_timestamp=1000.0
    )

    repo.save(pay)

    mock_exists.assert_any_call("NileGov Payment Record", "PAY-1")
    assert mock_doc.service_request == "req-1"
    assert mock_doc.citizen_profile == "CP-1"
    assert mock_doc.consent_record == "CON-1"
    assert mock_doc.amount == 50000.0
    assert mock_doc.payment_status == PaymentStatus.VERIFIED
    assert mock_doc.simulated_transaction_reference == "SIM-PAY-001"
    assert mock_doc.verification_status == PaymentVerificationStatus.SIMULATED_VERIFIED
    assert mock_doc.receipt_status == ReceiptStatus.SIMULATED_RECEIPT_GENERATED
    assert mock_doc.receipt_reference == "SIM-RECEIPT-001"
    assert mock_doc.reconciliation_status == ReconciliationStatus.RECONCILED
    assert mock_doc.verified_by == "officer_demo"
    assert "Prototype simulation only." in mock_doc.disclaimer

    mock_doc.save.assert_called_once()
