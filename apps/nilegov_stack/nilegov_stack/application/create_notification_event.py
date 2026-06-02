# Use case: Create Notification Event
# Prototype simulation only. No live Government registry access.

import time
from typing import Optional, Dict, Any
from nilegov_stack.application.ports import (
    ServiceRequestRepository, CitizenProfileRepository,
    ConsentRecordRepository, NotificationEventRepository
)
from nilegov_stack.domain.notification import (
    NotificationEvent, NotificationDeliveryStatus,
    NotificationChannel, RecipientType, NotificationMessageType
)
from nilegov_stack.application.generate_message_preview import GenerateMessagePreview


class CreateNotificationEvent:
    def __init__(
        self,
        request_repo: ServiceRequestRepository,
        profile_repo: Optional[CitizenProfileRepository] = None,
        consent_repo: Optional[ConsentRecordRepository] = None,
        notification_repo: Optional[NotificationEventRepository] = None
    ):
        self.request_repo = request_repo
        self.profile_repo = profile_repo
        self.consent_repo = consent_repo
        self.notification_repo = notification_repo
        self.preview_service = GenerateMessagePreview()

    def execute(
        self,
        request_id: str,
        message_type: str,
        recipient: Optional[str] = None,
        channel: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        triggered_by_event: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> NotificationEvent:
        t = timestamp if timestamp is not None else time.time()
        req = self.request_repo.get_by_id(request_id)
        if not req:
            raise ValueError(f"Service Request with ID {request_id} not found.")

        # Determine recipient info from citizen profile
        profile_id = req.citizen_profile_id
        profile = None
        if profile_id and self.profile_repo:
            profile = self.profile_repo.get_by_id(profile_id)

        # Resolve recipient address/channel
        if not recipient:
            if profile:
                # Fallback based on profile preferred channel
                pref = profile.preferred_contact_channel or "Phone"
                if pref == "Phone" or pref == "SMS" or pref == "WhatsApp":
                    recipient = profile.phone or req.phone_number
                else:
                    recipient = profile.email or req.email or req.phone_number
            else:
                recipient = req.email or req.phone_number

        if not channel:
            if profile and profile.preferred_contact_channel:
                pref = profile.preferred_contact_channel
                if pref in (NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.WHATSAPP, NotificationChannel.PORTAL):
                    channel = pref
                else:
                    channel = NotificationChannel.EMAIL
            else:
                channel = NotificationChannel.EMAIL

        # Generate message preview
        citizen_name = profile.full_name if profile else req.citizen_name
        title, body = self.preview_service.execute(message_type, req.reference_no, citizen_name, extra_params)

        # Resolve consent
        consent_checked = False
        consent_status = "Missing"
        consent_record_id = None
        delivery_status = NotificationDeliveryStatus.DRAFT

        # System notifications to officers/supervisors don't require citizen consent check
        is_citizen_notification = (recipient != req.assigned_officer_id and recipient != req.assigned_supervisor_id)

        if is_citizen_notification and profile_id and self.consent_repo:
            consent_checked = True
            consents = self.consent_repo.get_by_citizen_profile(profile_id)
            # Find Status Notifications purpose
            status_consent = None
            for c in consents:
                if c.consent_purpose == "Status Notifications":
                    status_consent = c
                    break

            if status_consent:
                consent_record_id = status_consent.consent_record_id
                consent_status = status_consent.consent_status
                # Check if currently active/granted
                if status_consent.is_active(t):
                    delivery_status = NotificationDeliveryStatus.QUEUED
                else:
                    delivery_status = NotificationDeliveryStatus.NOT_REQUIRED
            else:
                # No consent record exists for Status Notifications
                consent_status = "Missing"
                delivery_status = NotificationDeliveryStatus.NOT_REQUIRED
        else:
            # System notification or no consent repo: default to Queued
            consent_checked = True
            consent_status = "Granted"
            delivery_status = NotificationDeliveryStatus.QUEUED

        # Determine Recipient Type
        recipient_type = RecipientType.CITIZEN
        if recipient == req.assigned_officer_id:
            recipient_type = RecipientType.OFFICER
        elif recipient == req.assigned_supervisor_id:
            recipient_type = RecipientType.SUPERVISOR
        elif recipient == req.assigned_department:
            recipient_type = RecipientType.DEPARTMENT_QUEUE

        event_id = f"NOT-{request_id}-{int(t * 1000)}"
        event = NotificationEvent(
            notification_event_id=event_id,
            service_request_id=request_id,
            recipient=recipient,
            channel=channel,
            message=body,
            delivery_status=delivery_status,
            citizen_profile_id=profile_id,
            consent_record_id=consent_record_id,
            recipient_type=recipient_type,
            recipient_reference=recipient,
            recipient_placeholder=recipient,
            message_type=message_type,
            notification_type="Status Update" if is_citizen_notification else "System Alert",
            message_title=title,
            message_body_preview=body[:200],
            consent_checked=consent_checked,
            consent_status_at_trigger=consent_status,
            triggered_by_event=triggered_by_event,
            created_at=t,
            updated_at=t
        )

        if self.notification_repo:
            self.notification_repo.save(event)

        return event
