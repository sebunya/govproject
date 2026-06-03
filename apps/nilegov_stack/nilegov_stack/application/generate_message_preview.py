# Use case: Generate Notification Message Preview
# Prototype simulation only. No live Government registry access.

from typing import Dict, Any, Tuple
from nilegov_stack.domain.notification import NotificationMessageType

class GenerateMessagePreview:
    def execute(self, message_type: str, request_ref: str, citizen_name: str, extra_params: Dict[str, Any] = None) -> Tuple[str, str]:
        params = {
            "ref": request_ref,
            "name": citizen_name,
        }
        if extra_params:
            params.update(extra_params)

        # Standard Lost National ID demo message templates
        if message_type == NotificationMessageType.RECEIVED:
            title = f"NileGov ID Replacement Received: {params['ref']}"
            body = (
                f"Dear {params['name']}, your Lost National ID replacement request has been successfully submitted "
                f"under reference number {params['ref']}. Prototype simulation only. No live registry access."
            )
        elif message_type == NotificationMessageType.REVIEW:
            title = f"NileGov Case Under Review: {params['ref']}"
            body = (
                f"Dear {params['name']}, your request {params['ref']} has been assigned and is now under review by "
                f"the Service Desk. Prototype simulation only."
            )
        elif message_type == NotificationMessageType.INFO_REQUIRED:
            title = f"NileGov Action Required: {params['ref']}"
            reason = params.get("reason", "Please provide clear supporting documentation.")
            body = (
                f"Dear {params['name']}, additional information is required for case {params['ref']}. "
                f"Officer Notes: {reason}. Please log into the portal to upload documents."
            )
        elif message_type == NotificationMessageType.PAY_PENDING:
            title = f"NileGov Fee Pending: {params['ref']}"
            amount = params.get("amount", 15000.0)
            body = (
                f"Dear {params['name']}, a prototype processing fee of UGX {amount:,.2f} is pending for case {params['ref']}. "
                f"Please simulate fee verification on the portal. No real payment required."
            )
        elif message_type == NotificationMessageType.PAY_VERIFIED:
            title = f"NileGov Fee Verified: {params['ref']}"
            body = (
                f"Dear {params['name']}, your simulated payment for case {params['ref']} has been successfully verified. "
                f"Case review will now resume."
            )
        elif message_type == NotificationMessageType.APPROVED:
            title = f"NileGov Replacement Request Approved: {params['ref']}"
            body = (
                f"Dear {params['name']}, your Lost National ID replacement request {params['ref']} has been approved. "
                f"Printing simulation has commenced."
            )
        elif message_type == NotificationMessageType.READY:
            title = f"NileGov Card Ready for Collection: {params['ref']}"
            body = (
                f"Dear {params['name']}, your replacement National ID card under case {params['ref']} is ready for collection "
                f"at the Ntinda Desk, Kampala. Please present this confirmation."
            )
        elif message_type == NotificationMessageType.CLOSED:
            title = f"NileGov Case Closed: {params['ref']}"
            body = (
                f"Dear {params['name']}, case {params['ref']} has been closed as completed. Thank you for using NileGov Stack."
            )
        elif message_type == NotificationMessageType.REJECTED:
            title = f"NileGov Case Rejected: {params['ref']}"
            reason = params.get("reason", "Documents did not match registry records.")
            body = (
                f"Dear {params['name']}, your replacement request {params['ref']} was rejected. Reason: {reason}."
            )
        elif message_type == NotificationMessageType.RISK:
            title = f"NileGov SLA WARNING - At Risk: {params['ref']}"
            body = (
                f"SLA warning: Case {params['ref']} has exceeded its at-risk processing threshold and requires immediate attention."
            )
        elif message_type == NotificationMessageType.OVERDUE:
            title = f"NileGov SLA BREACH - Overdue: {params['ref']}"
            body = (
                f"SLA breach: Case {params['ref']} has exceeded allowed response/resolution limits."
            )
        elif message_type == NotificationMessageType.ESCALATED:
            title = f"NileGov SLA Escalated: {params['ref']}"
            supervisor = params.get("supervisor", "Supervisor Review Queue")
            reason = params.get("reason", "Resolution breach")
            body = (
                f"Casework escalation: Case {params['ref']} has been escalated to {supervisor}. Reason: {reason}."
            )
        elif message_type == NotificationMessageType.RETURNED:
            title = f"NileGov Case Returned: {params['ref']}"
            body = (
                f"Casework update: Case {params['ref']} has been cleared by supervisor and returned to the assigned desk officer."
            )
        else:
            title = f"NileGov Casework Update: {params['ref']}"
            body = f"Case {params['ref']} has been updated. Prototype simulation only."

        return title, body
