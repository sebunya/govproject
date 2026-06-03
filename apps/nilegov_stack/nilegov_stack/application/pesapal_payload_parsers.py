# Pesapal Callback and IPN Payload Parsers
# Digi-Verse Uganda Limited

import time
from typing import Dict, Any


def parse_pesapal_callback_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts standard fields from Pesapal callback payload."""
    tracking_id = payload.get("OrderTrackingId") or payload.get("orderTrackingId")
    merchant_ref = payload.get("OrderMerchantReference") or payload.get("orderMerchantReference")
    notification_type = payload.get("OrderNotificationType") or payload.get("orderNotificationType")

    return {
        "order_tracking_id": tracking_id,
        "merchant_reference": merchant_ref,
        "notification_type": notification_type
    }


def parse_pesapal_ipn_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts standard fields from Pesapal IPN payload."""
    return parse_pesapal_callback_payload(payload)


def update_payment_record_from_callback_metadata(
    payment_record,
    parsed_metadata: Dict[str, Any],
    timestamp: float,
    is_ipn: bool = False
) -> None:
    """Updates PaymentRecord metadata from callback/IPN without marking verified.
    
    Final payment verification MUST happen via GetTransactionStatus.
    """
    if parsed_metadata.get("order_tracking_id"):
        payment_record.provider_order_tracking_id = parsed_metadata["order_tracking_id"]
    if parsed_metadata.get("merchant_reference"):
        payment_record.provider_merchant_reference = parsed_metadata["merchant_reference"]

    if is_ipn:
        payment_record.provider_ipn_received_at = timestamp
    else:
        payment_record.provider_callback_received_at = timestamp

    payment_record.updated_at = timestamp
