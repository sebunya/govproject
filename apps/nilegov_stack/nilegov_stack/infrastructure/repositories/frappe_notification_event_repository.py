# Frappe-based Notification Event Repository
# Prototype simulation only. No live Government registry access.

try:
    import frappe
except ImportError:
    frappe = None

from typing import Optional, List
from nilegov_stack.application.ports import NotificationEventRepository
from nilegov_stack.domain.notification import NotificationEvent


class FrappeNotificationEventRepository(NotificationEventRepository):
    """Frappe-based repository for persisting and loading Notification Event aggregates."""

    def _check_frappe(self):
        if not frappe:
            raise ImportError("Frappe framework is not loaded in this environment.")

    def save(self, event: NotificationEvent) -> None:
        self._check_frappe()

        # Load or create document
        if frappe.db.exists("NileGov Citizen Notification", event.notification_event_id):
            doc = frappe.get_doc("NileGov Citizen Notification", event.notification_event_id)
        else:
            doc = frappe.new_doc("NileGov Citizen Notification")
            doc.notification_event_id = event.notification_event_id

        doc.service_request = event.service_request_id
        doc.citizen_profile = event.citizen_profile_id
        doc.consent_record = event.consent_record_id
        doc.recipient_type = event.recipient_type
        doc.recipient_reference = event.recipient_reference
        doc.recipient_placeholder = event.recipient_placeholder
        doc.recipient = event.recipient
        doc.channel = event.channel
        doc.message_type = event.message_type
        doc.notification_type = event.notification_type
        doc.message_title = event.message_title
        doc.message_body_preview = event.message_body_preview
        doc.message = event.message
        doc.delivery_status = event.delivery_status
        doc.consent_checked = 1 if event.consent_checked else 0
        doc.consent_status_at_trigger = event.consent_status_at_trigger
        doc.triggered_by_event = event.triggered_by_event
        doc.failure_reason = event.failure_reason
        doc.disclaimer = event.disclaimer

        if event.scheduled_at:
            doc.scheduled_at = frappe.utils.get_datetime(event.scheduled_at)
        if event.simulated_sent_at:
            doc.simulated_sent_at = frappe.utils.get_datetime(event.simulated_sent_at)
            doc.sent_at = doc.simulated_sent_at
        if event.simulated_failed_at:
            doc.simulated_failed_at = frappe.utils.get_datetime(event.simulated_failed_at)

        doc.save(ignore_permissions=True)
        frappe.db.commit()

    def get_by_id(self, event_id: str) -> Optional[NotificationEvent]:
        self._check_frappe()
        if not frappe.db.exists("NileGov Citizen Notification", event_id):
            return None

        doc = frappe.get_doc("NileGov Citizen Notification", event_id)
        return self._map_doc_to_aggregate(doc)

    def get_by_service_request(self, request_id: str) -> List[NotificationEvent]:
        self._check_frappe()
        record_ids = frappe.get_all(
            "NileGov Citizen Notification",
            filters={"service_request": request_id},
            pluck="name"
        )
        results = []
        for rid in record_ids:
            evt = self.get_by_id(rid)
            if evt:
                results.append(evt)
        return results

    def get_by_citizen_profile(self, profile_id: str) -> List[NotificationEvent]:
        self._check_frappe()
        record_ids = frappe.get_all(
            "NileGov Citizen Notification",
            filters={"citizen_profile": profile_id},
            pluck="name"
        )
        results = []
        for rid in record_ids:
            evt = self.get_by_id(rid)
            if evt:
                results.append(evt)
        return results

    def get_by_channel(self, channel: str) -> List[NotificationEvent]:
        self._check_frappe()
        record_ids = frappe.get_all(
            "NileGov Citizen Notification",
            filters={"channel": channel},
            pluck="name"
        )
        results = []
        for rid in record_ids:
            evt = self.get_by_id(rid)
            if evt:
                results.append(evt)
        return results

    def get_by_delivery_status(self, status: str) -> List[NotificationEvent]:
        self._check_frappe()
        record_ids = frappe.get_all(
            "NileGov Citizen Notification",
            filters={"delivery_status": status},
            pluck="name"
        )
        results = []
        for rid in record_ids:
            evt = self.get_by_id(rid)
            if evt:
                results.append(evt)
        return results

    def get_all(self) -> List[NotificationEvent]:
        self._check_frappe()
        record_ids = frappe.get_all("NileGov Citizen Notification", pluck="name")
        results = []
        for rid in record_ids:
            evt = self.get_by_id(rid)
            if evt:
                results.append(evt)
        return results

    def _map_doc_to_aggregate(self, doc) -> NotificationEvent:
        scheduled_at = frappe.utils.get_timestamp(doc.scheduled_at) if doc.scheduled_at else None
        sent_at = frappe.utils.get_timestamp(doc.simulated_sent_at) if doc.simulated_sent_at else None
        failed_at = frappe.utils.get_timestamp(doc.simulated_failed_at) if doc.simulated_failed_at else None

        return NotificationEvent(
            notification_event_id=doc.notification_event_id or doc.name,
            service_request_id=doc.service_request,
            recipient=doc.recipient,
            channel=doc.channel,
            message=doc.message,
            delivery_status=doc.delivery_status or "Draft",
            citizen_profile_id=doc.citizen_profile,
            consent_record_id=doc.consent_record,
            recipient_type=doc.recipient_type or "Citizen",
            recipient_reference=doc.recipient_reference,
            recipient_placeholder=doc.recipient_placeholder,
            message_type=doc.message_type or "Request Received",
            notification_type=doc.notification_type or "Status Update",
            message_title=doc.message_title,
            message_body_preview=doc.message_body_preview,
            consent_checked=bool(doc.consent_checked),
            consent_status_at_trigger=doc.consent_status_at_trigger,
            triggered_by_event=doc.triggered_by_event,
            scheduled_at=scheduled_at,
            simulated_sent_at=sent_at,
            simulated_failed_at=failed_at,
            failure_reason=doc.failure_reason,
            disclaimer=doc.disclaimer,
            created_at=frappe.utils.get_timestamp(doc.creation),
            updated_at=frappe.utils.get_timestamp(doc.modified)
        )
