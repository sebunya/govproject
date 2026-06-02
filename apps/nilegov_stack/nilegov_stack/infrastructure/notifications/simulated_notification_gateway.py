# Simulated Notification Gateway
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

from nilegov_stack.application.ports import NotificationGateway


class SimulatedNotificationGateway(NotificationGateway):
    """Simulated Notification Gateway adapter.
    
    Logs notification events instead of performing real integration calls.
    """
    def __init__(self):
        self.sms_logs = []
        self.email_logs = []

    def send_sms(self, phone_number: str, message: str) -> bool:
        log_entry = {
            "phone_number": phone_number,
            "message": message,
            "label": "Test notification event (Simulated SMS)"
        }
        self.sms_logs.append(log_entry)
        return True

    def send_email(self, email_address: str, subject: str, body: str) -> bool:
        log_entry = {
            "email_address": email_address,
            "subject": subject,
            "body": body,
            "label": "Test notification event (Simulated Email)"
        }
        self.email_logs.append(log_entry)
        return True

    def send_simulated_notification(self, event) -> bool:
        """Sends a simulated notification event and logs the call."""
        if not event.recipient or event.recipient == "invalid":
            return False

        if event.channel == "Email":
            return self.send_email(event.recipient, event.message_title or "Update", event.message)
        else:
            return self.send_sms(event.recipient, event.message)
