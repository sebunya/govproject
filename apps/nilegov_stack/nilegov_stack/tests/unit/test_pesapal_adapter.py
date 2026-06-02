# Unit Tests for Pesapal API 3.0 Adapter & Use Cases
# Digi-Verse Uganda Limited
# Prototype sandbox-first verification. No live network calls.

import pytest
import time
from unittest.mock import MagicMock, patch
import os

from nilegov_stack.domain.payment import PaymentRecord, PaymentStatus, PaymentVerificationStatus, ReceiptStatus, ReconciliationStatus
from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.infrastructure.integrations.pesapal_api_client import (
    PesapalApiClient, PesapalConfig, PesapalError, PesapalAuthToken,
    PesapalIPNRegistrationResult, PesapalOrderSubmissionResult, PesapalTransactionStatusResult
)
from nilegov_stack.infrastructure.repositories.payment_record_repository import InMemoryPaymentRecordRepository
from nilegov_stack.infrastructure.repositories.service_request_repository import InMemoryServiceRequestRepository
from nilegov_stack.application.register_pesapal_ipn import RegisterPesapalIPN
from nilegov_stack.application.initiate_pesapal_payment import InitiatePesapalPayment
from nilegov_stack.application.refresh_pesapal_payment_status import RefreshPesapalPaymentStatus
from nilegov_stack.application.pesapal_payload_parsers import (
    parse_pesapal_callback_payload, parse_pesapal_ipn_payload, update_payment_record_from_callback_metadata
)


# --- 1. Configuration tests ---

def test_pesapal_config_defaults_and_env():
    """Verifies default settings and behavior from env."""
    # Test default sandbox mode
    with patch.dict(os.environ, {}, clear=True):
        config = PesapalConfig.from_env()
        assert config.mode == "sandbox"
        assert config.live_enabled is False
        assert config.get_base_url() == "https://cybqa.pesapal.com/pesapalv3"

    # Test live mode blocked if not explicitly enabled
    with patch.dict(os.environ, {"PESAPAL_MODE": "live"}, clear=True):
        config = PesapalConfig.from_env()
        assert config.mode == "live"
        assert config.live_enabled is False
        with pytest.raises(ValueError, match="Pesapal Live mode is not enabled"):
            config.get_base_url()

    # Test live mode allowed when explicitly enabled
    with patch.dict(os.environ, {"PESAPAL_MODE": "live", "PESAPAL_LIVE_ENABLED": "true"}, clear=True):
        config = PesapalConfig.from_env()
        assert config.mode == "live"
        assert config.live_enabled is True
        assert config.get_base_url() == "https://pay.pesapal.com/v3"


def test_pesapal_missing_credentials_fails():
    """Verifies that missing consumer_key or consumer_secret fails auth request."""
    config = PesapalConfig(consumer_key=None, consumer_secret=None)
    client = PesapalApiClient(config)
    with pytest.raises(PesapalError, match="Missing Pesapal consumer_key or consumer_secret"):
        client.request_token()


# --- 2. Client & Mocked Adapter tests ---

@patch("requests.Session.post")
def test_request_token_success(mock_post):
    """Verifies token request maps response to PesapalAuthToken."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"token": "mock_bearer_token_123"}
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp

    config = PesapalConfig(consumer_key="fake_key", consumer_secret="fake_secret")
    client = PesapalApiClient(config)
    token_obj = client.request_token()

    assert isinstance(token_obj, PesapalAuthToken)
    assert token_obj.token == "mock_bearer_token_123"
    assert token_obj.expiry > time.time()
    mock_post.assert_called_once()


@patch("requests.Session.post")
def test_register_ipn_url_success(mock_post):
    """Verifies IPN registration maps returned ipn_id."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "ipn_id": "ipn_id_999",
        "url": "http://nilegov.local/ipn",
        "status": "SUCCESS"
    }
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp

    config = PesapalConfig(ipn_url="http://nilegov.local/ipn")
    client = PesapalApiClient(config)
    result = client.register_ipn_url("token_123")

    assert isinstance(result, PesapalIPNRegistrationResult)
    assert result.ipn_id == "ipn_id_999"
    assert result.url == "http://nilegov.local/ipn"
    assert result.status == "SUCCESS"


@patch("requests.Session.post")
def test_submit_order_success(mock_post):
    """Verifies order submission sends payload and returns tracking ID and redirect URL."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "order_tracking_id": "tracking_xyz",
        "merchant_reference": "PAY-REF-001",
        "redirect_url": "https://cybqa.pesapal.com/payment/xyz"
    }
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp

    client = PesapalApiClient(PesapalConfig(callback_url="http://nilegov.local/callback"))
    pay_record = PaymentRecord("PAY-REF-001", "req-1", 50000.0)
    billing = {"email_address": "citizen@example.com", "phone_number": "+256700000001"}
    
    result = client.submit_order("token_123", pay_record, billing, "ipn_id_999")

    assert isinstance(result, PesapalOrderSubmissionResult)
    assert result.order_tracking_id == "tracking_xyz"
    assert result.redirect_url == "https://cybqa.pesapal.com/payment/xyz"


@patch("requests.Session.get")
def test_get_transaction_status_completed(mock_get):
    """Verifies get status mapping for COMPLETED transaction."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "payment_method": "Mobile Money",
        "amount": 50000.0,
        "confirmation_code": "PESA-CONF-1",
        "payment_status_description": "Completed successfully",
        "status_code": 1,
        "merchant_reference": "PAY-REF-001",
        "currency": "UGX",
        "payment_account": "256700***001"
    }
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp

    client = PesapalApiClient()
    res = client.get_transaction_status("token_123", "tracking_xyz")

    assert res.status_code == 1
    assert res.confirmation_code == "PESA-CONF-1"
    assert res.masked_payment_account == "256700***001"


# --- 3. Use Case & Flow tests ---

def test_initiate_pesapal_payment_flow():
    """Verifies that InitiatePesapalPayment updates PaymentRecord correctly."""
    repo = InMemoryPaymentRecordRepository()
    pay_record = PaymentRecord("PAY-001", "req-100", 50000.0)
    repo.save(pay_record)

    client_mock = MagicMock(spec=PesapalApiClient)
    client_mock.config = PesapalConfig(mode="sandbox")
    client_mock.request_token.return_value = PesapalAuthToken("token_val", time.time() + 300)
    client_mock.submit_order.return_value = PesapalOrderSubmissionResult("tracking_xyz", "PAY-001", "https://redirect.com")

    use_case = InitiatePesapalPayment(repo, client_mock)
    billing = {"email_address": "test@test.com"}
    updated = use_case.execute("PAY-001", billing, "ipn_123", timestamp=100.0)

    assert updated.provider == "Pesapal Sandbox"
    assert updated.provider_mode == "sandbox"
    assert updated.provider_order_tracking_id == "tracking_xyz"
    assert updated.provider_redirect_url == "https://redirect.com"
    assert updated.provider_ipn_id == "ipn_123"
    assert updated.payment_status == PaymentStatus.SUBMITTED


def test_refresh_pesapal_payment_status_completed():
    """Verifies status mapping from COMPLETED status_code to Verified states."""
    pay_repo = InMemoryPaymentRecordRepository()
    srv_repo = InMemoryServiceRequestRepository()

    # Create & submit payment record
    pay_record = PaymentRecord("PAY-001", "req-100", 50000.0, citizen_profile_id="CP-1")
    pay_record.provider_order_tracking_id = "tracking_xyz"
    pay_record.payment_status = PaymentStatus.SUBMITTED
    pay_repo.save(pay_record)

    # Create service request
    sr = ServiceRequest("req-100", "NGS-NIRA-2026-0001", NIN("CF900000000000"), "Citizen A", "+256700000001", "Kampala", "Lost ID")
    sr.status = WorkflowStatus.PAYMENT_PENDING
    srv_repo.save(sr)

    # Mock Pesapal API Client
    client_mock = MagicMock(spec=PesapalApiClient)
    client_mock.config = PesapalConfig(mode="sandbox")
    client_mock.request_token.return_value = PesapalAuthToken("token_val", time.time() + 300)
    client_mock.get_transaction_status.return_value = PesapalTransactionStatusResult(
        payment_method="MTN Mobile Money",
        amount=50000.0,
        confirmation_code="CONF_CODE_OK",
        payment_status_description="Completed",
        status_code=1,
        merchant_reference="PAY-001",
        currency="UGX",
        masked_payment_account="256700***001"
    )
    # Define map method behavior on mock
    real_client = PesapalApiClient()
    client_mock.map_transaction_status_to_payment_record = real_client.map_transaction_status_to_payment_record

    use_case = RefreshPesapalPaymentStatus(pay_repo, client_mock, srv_repo)
    result_status = use_case.execute("PAY-001", verified_by="officer_test", timestamp=200.0)

    # Assert payment states
    updated_pay = pay_repo.get_by_id("PAY-001")
    assert result_status == PaymentStatus.VERIFIED
    assert updated_pay.payment_status == PaymentStatus.VERIFIED
    assert updated_pay.verification_status == PaymentVerificationStatus.SIMULATED_VERIFIED
    assert updated_pay.receipt_status == ReceiptStatus.RECEIPT_READY
    assert updated_pay.reconciliation_status == ReconciliationStatus.PENDING_RECONCILIATION
    assert updated_pay.provider_payment_method == "MTN Mobile Money"
    assert updated_pay.provider_confirmation_code == "CONF_CODE_OK"
    assert updated_pay.provider_masked_account == "256700***001"

    # Assert service request states
    updated_sr = srv_repo.get_by_id("req-100")
    assert updated_sr.payment_status == "Verified"
    assert updated_sr.status == WorkflowStatus.PAYMENT_VERIFIED


def test_refresh_pesapal_payment_status_failed():
    """Verifies status mapping from FAILED status_code to Failed states."""
    pay_repo = InMemoryPaymentRecordRepository()
    srv_repo = InMemoryServiceRequestRepository()

    pay_record = PaymentRecord("PAY-002", "req-200", 50000.0)
    pay_record.provider_order_tracking_id = "tracking_abc"
    pay_repo.save(pay_record)

    sr = ServiceRequest("req-200", "NGS-NIRA-2026-0002", NIN("CF900000000002"), "Citizen B", "+256700000002", "Kampala", "Lost ID")
    sr.status = WorkflowStatus.PAYMENT_PENDING
    srv_repo.save(sr)

    client_mock = MagicMock(spec=PesapalApiClient)
    client_mock.config = PesapalConfig(mode="sandbox")
    client_mock.request_token.return_value = PesapalAuthToken("token_val", time.time() + 300)
    client_mock.get_transaction_status.return_value = PesapalTransactionStatusResult(
        payment_method="Card",
        amount=50000.0,
        confirmation_code="",
        payment_status_description="Insufficient Funds",
        status_code=2,
        merchant_reference="PAY-002",
        currency="UGX"
    )
    real_client = PesapalApiClient()
    client_mock.map_transaction_status_to_payment_record = real_client.map_transaction_status_to_payment_record

    use_case = RefreshPesapalPaymentStatus(pay_repo, client_mock, srv_repo)
    result_status = use_case.execute("PAY-002", verified_by="system", timestamp=200.0)

    updated_pay = pay_repo.get_by_id("PAY-002")
    assert result_status == PaymentStatus.FAILED
    assert updated_pay.payment_status == PaymentStatus.FAILED
    assert updated_pay.verification_status == PaymentVerificationStatus.SIMULATED_FAILED
    assert updated_pay.failure_reason == "Insufficient Funds"

    updated_sr = srv_repo.get_by_id("req-200")
    assert updated_sr.payment_status == "Failed"
    assert updated_sr.status == WorkflowStatus.PAYMENT_PENDING


def test_refresh_pesapal_payment_status_reversed_and_invalid():
    """Verifies status mapping from REVERSED and INVALID status_codes to correct states."""
    pay_repo = InMemoryPaymentRecordRepository()

    # A. REVERSED test
    pay_record_a = PaymentRecord("PAY-003a", "req-300", 50000.0)
    pay_record_a.provider_order_tracking_id = "track_rev"
    pay_repo.save(pay_record_a)

    client_mock = MagicMock(spec=PesapalApiClient)
    client_mock.config = PesapalConfig(mode="sandbox")
    client_mock.request_token.return_value = PesapalAuthToken("token_val", time.time() + 300)
    client_mock.get_transaction_status.return_value = PesapalTransactionStatusResult(
        payment_method="Mobile Money",
        amount=50000.0,
        confirmation_code="CONF_REV",
        payment_status_description="Reversed transaction",
        status_code=3,
        merchant_reference="PAY-003a",
        currency="UGX"
    )
    real_client = PesapalApiClient()
    client_mock.map_transaction_status_to_payment_record = real_client.map_transaction_status_to_payment_record

    use_case = RefreshPesapalPaymentStatus(pay_repo, client_mock)
    use_case.execute("PAY-003a", timestamp=200.0)

    updated_pay_a = pay_repo.get_by_id("PAY-003a")
    assert updated_pay_a.payment_status == PaymentStatus.REVERSED
    assert updated_pay_a.verification_status == PaymentVerificationStatus.REQUIRES_REVIEW
    assert updated_pay_a.reconciliation_status == ReconciliationStatus.REQUIRES_REVIEW

    # B. INVALID test
    pay_record_b = PaymentRecord("PAY-003b", "req-300", 50000.0)
    pay_record_b.provider_order_tracking_id = "track_inv"
    pay_repo.save(pay_record_b)

    client_mock.get_transaction_status.return_value = PesapalTransactionStatusResult(
        payment_method="Mobile Money",
        amount=50000.0,
        confirmation_code="",
        payment_status_description="Invalid order reference",
        status_code=0,
        merchant_reference="PAY-003b",
        currency="UGX"
    )

    use_case.execute("PAY-003b", timestamp=200.0)

    updated_pay_b = pay_repo.get_by_id("PAY-003b")
    assert updated_pay_b.payment_status == PaymentStatus.FAILED
    assert updated_pay_b.verification_status == PaymentVerificationStatus.REQUIRES_REVIEW
    assert updated_pay_b.failure_reason == "Invalid order reference"


# --- 4. Payload Parsers tests ---

def test_payload_parsers_without_verification():
    """Verifies callback and IPN payload parsing updates metadata without verifying."""
    pay_record = PaymentRecord("PAY-004", "req-400", 50000.0)
    assert pay_record.payment_status == PaymentStatus.PENDING
    assert pay_record.payment_status == "Pending"

    callback_payload = {
        "OrderTrackingId": "tracking_123_callback",
        "OrderMerchantReference": "PAY-004",
        "OrderNotificationType": "CALLBACK"
    }

    parsed = parse_pesapal_callback_payload(callback_payload)
    assert parsed["order_tracking_id"] == "tracking_123_callback"
    assert parsed["merchant_reference"] == "PAY-004"
    assert parsed["notification_type"] == "CALLBACK"

    # Apply callback metadata to record
    update_payment_record_from_callback_metadata(pay_record, parsed, timestamp=150.0, is_ipn=False)
    assert pay_record.provider_order_tracking_id == "tracking_123_callback"
    assert pay_record.provider_merchant_reference == "PAY-004"
    assert pay_record.provider_callback_received_at == 150.0
    # Crucial security assertion: Callback reception does NOT mark payment verified
    assert pay_record.payment_status == "Pending"

    # Repeat for IPN
    ipn_payload = {
        "orderTrackingId": "tracking_123_ipn",
        "orderMerchantReference": "PAY-004",
        "orderNotificationType": "IPNCHANGE"
    }

    parsed_ipn = parse_pesapal_ipn_payload(ipn_payload)
    update_payment_record_from_callback_metadata(pay_record, parsed_ipn, timestamp=250.0, is_ipn=True)
    assert pay_record.provider_order_tracking_id == "tracking_123_ipn"
    assert pay_record.provider_ipn_received_at == 250.0
    # Crucial security assertion: IPN reception does NOT mark payment verified
    assert pay_record.payment_status == "Pending"
