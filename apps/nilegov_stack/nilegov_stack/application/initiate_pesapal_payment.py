# Use case: Initiate Pesapal Payment
# Digi-Verse Uganda Limited

import time
from typing import Dict, Any, Optional
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.infrastructure.integrations.pesapal_api_client import PesapalApiClient, PesapalConfig


class InitiatePesapalPayment:
    """Application Service to initiate a Pesapal API 3.0 payment flow for a PaymentRecord."""

    def __init__(self, repository: PaymentRecordRepository, api_client: PesapalApiClient):
        self.repository = repository
        self.api_client = api_client

    def execute(self, payment_record_id: str, billing_address: Dict[str, Any], ipn_id: str, timestamp: Optional[float] = None) -> Any:
        payment_record = self.repository.get_by_id(payment_record_id)
        if not payment_record:
            raise ValueError(f"Payment record not found: {payment_record_id}")

        curr_time = timestamp or time.time()

        # Update provider metadata
        config = self.api_client.config
        provider_name = "Pesapal Live" if config.mode == "live" else "Pesapal Sandbox"
        payment_record.provider = provider_name
        payment_record.provider_mode = config.mode
        payment_record.provider_merchant_reference = payment_record.payment_record_id
        payment_record.provider_ipn_id = ipn_id

        # Submit order to Pesapal
        auth_token = self.api_client.request_token()
        result = self.api_client.submit_order(
            token=auth_token.token,
            payment_record=payment_record,
            billing_address=billing_address,
            notification_id=ipn_id
        )

        # Update tracking references and transition state
        payment_record.provider_order_tracking_id = result.order_tracking_id
        payment_record.provider_redirect_url = result.redirect_url
        
        # Submit transaction
        payment_record.submit(result.order_tracking_id, curr_time)

        # Save to repository
        self.repository.save(payment_record)

        return payment_record
