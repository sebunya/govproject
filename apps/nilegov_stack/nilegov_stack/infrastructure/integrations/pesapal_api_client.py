# Pesapal API 3.0 Client & Adapter Integration
# Digi-Verse Uganda Limited
# Prototype sandbox-first implementation. No live payment processed.

import os
import time
import requests
from dataclasses import dataclass
from typing import Optional, Dict, Any


class PesapalError(Exception):
    """Custom exception class for Pesapal integration errors."""
    pass


@dataclass
class PesapalConfig:
    mode: str = "sandbox"
    consumer_key: Optional[str] = None
    consumer_secret: Optional[str] = None
    sandbox_base_url: str = "https://cybqa.pesapal.com/pesapalv3"
    live_base_url: str = "https://pay.pesapal.com/v3"
    callback_url: Optional[str] = None
    cancellation_url: Optional[str] = None
    ipn_url: Optional[str] = None
    ipn_notification_type: str = "POST"
    live_enabled: bool = False

    @classmethod
    def from_env(cls):
        mode = os.environ.get("PESAPAL_MODE", "sandbox").lower()
        live_enabled_str = os.environ.get("PESAPAL_LIVE_ENABLED", "false").lower()
        live_enabled = live_enabled_str in ("true", "1", "yes")

        return cls(
            mode=mode,
            consumer_key=os.environ.get("PESAPAL_CONSUMER_KEY"),
            consumer_secret=os.environ.get("PESAPAL_CONSUMER_SECRET"),
            sandbox_base_url=os.environ.get("PESAPAL_SANDBOX_BASE_URL", "https://cybqa.pesapal.com/pesapalv3"),
            live_base_url=os.environ.get("PESAPAL_LIVE_BASE_URL", "https://pay.pesapal.com/v3"),
            callback_url=os.environ.get("PESAPAL_CALLBACK_URL"),
            cancellation_url=os.environ.get("PESAPAL_CANCELLATION_URL"),
            ipn_url=os.environ.get("PESAPAL_IPN_URL"),
            ipn_notification_type=os.environ.get("PESAPAL_IPN_NOTIFICATION_TYPE", "POST"),
            live_enabled=live_enabled
        )

    def get_base_url(self) -> str:
        if self.mode == "live":
            if not self.live_enabled:
                raise ValueError("Pesapal Live mode is not enabled in environment config (PESAPAL_LIVE_ENABLED=true required).")
            return self.live_base_url
        return self.sandbox_base_url


@dataclass
class PesapalAuthToken:
    token: str
    expiry: float


@dataclass
class PesapalIPNRegistrationResult:
    ipn_id: str
    url: str
    status: str


@dataclass
class PesapalOrderSubmissionResult:
    order_tracking_id: str
    merchant_reference: str
    redirect_url: str


@dataclass
class PesapalTransactionStatusResult:
    payment_method: str
    amount: float
    confirmation_code: str
    payment_status_description: str
    status_code: int
    merchant_reference: str
    currency: str
    masked_payment_account: Optional[str] = None


class PesapalApiClient:
    def __init__(self, config: Optional[PesapalConfig] = None, session: Optional[requests.Session] = None):
        self.config = config or PesapalConfig.from_env()
        self.session = session or requests.Session()

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def request_token(self) -> PesapalAuthToken:
        if not self.config.consumer_key or not self.config.consumer_secret:
            raise PesapalError("Missing Pesapal consumer_key or consumer_secret in configuration.")

        base_url = self.config.get_base_url()
        url = f"{base_url}/api/Auth/RequestToken"
        payload = {
            "consumer_key": self.config.consumer_key,
            "consumer_secret": self.config.consumer_secret
        }

        try:
            response = self.session.post(url, json=payload, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise PesapalError(f"Failed to request Pesapal token: {str(e)}")

        token = data.get("token")
        if not token:
            error_msg = data.get("error", {}).get("message", "Unknown auth error")
            raise PesapalError(f"Pesapal auth error: {error_msg}")

        return PesapalAuthToken(
            token=token,
            expiry=time.time() + 300
        )

    def register_ipn_url(self, token: str) -> PesapalIPNRegistrationResult:
        if not self.config.ipn_url:
            raise PesapalError("Missing PESAPAL_IPN_URL in configuration.")

        base_url = self.config.get_base_url()
        url = f"{base_url}/api/URLSetup/RegisterIPN"
        payload = {
            "url": self.config.ipn_url,
            "ipn_notification_type": self.config.ipn_notification_type
        }

        try:
            response = self.session.post(url, json=payload, headers=self._get_headers(token), timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise PesapalError(f"Failed to register Pesapal IPN: {str(e)}")

        ipn_id = data.get("ipn_id")
        if not ipn_id:
            error_msg = data.get("error", {}).get("message", "Unknown IPN registration error")
            raise PesapalError(f"Pesapal IPN registration error: {error_msg}")

        return PesapalIPNRegistrationResult(
            ipn_id=ipn_id,
            url=data.get("url", self.config.ipn_url),
            status=data.get("status", "SUCCESS")
        )

    def submit_order(self, token: str, payment_record, billing_address: Dict[str, Any], notification_id: str) -> PesapalOrderSubmissionResult:
        merchant_ref = payment_record.payment_record_id
        if not merchant_ref:
            raise PesapalError("Merchant reference is required to submit order.")

        base_url = self.config.get_base_url()
        url = f"{base_url}/api/Transactions/SubmitOrderRequest"

        payload = {
            "id": merchant_ref,
            "currency": payment_record.currency,
            "amount": payment_record.amount,
            "description": payment_record.payment_purpose,
            "callback_url": self.config.callback_url,
            "notification_id": notification_id,
            "billing_address": billing_address
        }

        if self.config.cancellation_url:
            payload["cancellation_url"] = self.config.cancellation_url

        try:
            response = self.session.post(url, json=payload, headers=self._get_headers(token), timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise PesapalError(f"Failed to submit Pesapal order: {str(e)}")

        order_tracking_id = data.get("order_tracking_id")
        redirect_url = data.get("redirect_url")

        if not order_tracking_id or not redirect_url:
            error_msg = data.get("error", {}).get("message", "Unknown submit order error")
            raise PesapalError(f"Pesapal submit order error: {error_msg}")

        return PesapalOrderSubmissionResult(
            order_tracking_id=order_tracking_id,
            merchant_reference=data.get("merchant_reference", merchant_ref),
            redirect_url=redirect_url
        )

    def get_transaction_status(self, token: str, order_tracking_id: str) -> PesapalTransactionStatusResult:
        if not order_tracking_id:
            raise PesapalError("Order tracking ID is required to look up transaction status.")

        base_url = self.config.get_base_url()
        url = f"{base_url}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"

        try:
            response = self.session.get(url, headers=self._get_headers(token), timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise PesapalError(f"Failed to get Pesapal transaction status: {str(e)}")

        status_code = data.get("status_code")
        if status_code is None:
            error_msg = data.get("error", {}).get("message", "Unknown get status error")
            raise PesapalError(f"Pesapal get status error: {error_msg}")

        try:
            status_code_val = int(status_code)
        except ValueError:
            raise PesapalError(f"Pesapal invalid status_code returned: {status_code}")

        return PesapalTransactionStatusResult(
            payment_method=data.get("payment_method", "UNKNOWN"),
            amount=float(data.get("amount", 0.0)),
            confirmation_code=data.get("confirmation_code", ""),
            payment_status_description=data.get("payment_status_description", ""),
            status_code=status_code_val,
            merchant_reference=data.get("merchant_reference", ""),
            currency=data.get("currency", "UGX"),
            masked_payment_account=data.get("payment_account")
        )

    def map_transaction_status_to_payment_record(
        self,
        payment_record,
        status_result: PesapalTransactionStatusResult,
        timestamp: float,
        checker_name: str
    ) -> None:
        payment_record.provider_payment_method = status_result.payment_method
        payment_record.provider_confirmation_code = status_result.confirmation_code
        payment_record.provider_status_code = str(status_result.status_code)
        payment_record.provider_status_description = status_result.payment_status_description
        payment_record.provider_status_checked_at = timestamp
        payment_record.provider_masked_account = status_result.masked_payment_account

        if status_result.status_code == 1:  # COMPLETED
            # Handle verify transition
            if payment_record.payment_status in ("Submitted", "Pending"):
                payment_record.verify(checker_name, timestamp)
            else:
                payment_record.payment_status = "Verified"
                payment_record.verification_status = "Simulated Verified"
                payment_record.updated_at = timestamp
            payment_record.receipt_reference = status_result.confirmation_code or payment_record.receipt_reference
            payment_record.receipt_status = "Receipt Ready"
            payment_record.reconciliation_status = "Pending Reconciliation"
        elif status_result.status_code == 2:  # FAILED
            payment_record.fail(status_result.payment_status_description or "Pesapal payment failed.", timestamp)
        elif status_result.status_code == 3:  # REVERSED
            payment_record.payment_status = "Reversed"
            payment_record.verification_status = "Requires Review"
            payment_record.reconciliation_status = "Requires Review"
            payment_record.updated_at = timestamp
        elif status_result.status_code == 0:  # INVALID
            payment_record.payment_status = "Failed"
            payment_record.verification_status = "Requires Review"
            payment_record.failure_reason = status_result.payment_status_description or "Invalid Pesapal transaction."
            payment_record.updated_at = timestamp
        else:
            payment_record.flag_for_review(timestamp)
