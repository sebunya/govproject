# Unit Tests for NileGov Notification Events & Simulated Communication Foundation
# Prototype simulation only. No live Government registry access.

import pytest
import time
from unittest.mock import MagicMock, patch
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus
from nilegov_stack.domain.citizen import CitizenProfile
from nilegov_stack.domain.consent import ConsentRecord, ConsentStatus, ConsentChannel
from nilegov_stack.domain.sla import SLARule
from nilegov_stack.domain.notification import (
    NotificationEvent, RecipientType, NotificationChannel,
    NotificationDeliveryStatus, NotificationMessageType
)
from nilegov_stack.application.create_notification_event import CreateNotificationEvent
from nilegov_stack.application.queue_notification_event import QueueNotificationEvent
from nilegov_stack.application.mark_notification_sent import MarkNotificationSent
from nilegov_stack.application.mark_notification_failed import MarkNotificationFailed
from nilegov_stack.application.cancel_notification_event import CancelNotificationEvent
from nilegov_stack.application.list_notifications_by_service_request import ListNotificationsByServiceRequest
from nilegov_stack.application.list_notifications_by_citizen_profile import ListNotificationsByCitizenProfile
from nilegov_stack.application.list_notifications_by_channel import ListNotificationsByChannel
from nilegov_stack.application.list_notifications_by_delivery_status import ListNotificationsByDeliveryStatus
from nilegov_stack.application.send_simulated_notification import SendSimulatedNotification
from nilegov_stack.infrastructure.notifications.simulated_notification_gateway import SimulatedNotificationGateway
from nilegov_stack.infrastructure.repositories.service_request_repository import InMemoryServiceRequestRepository
from nilegov_stack.infrastructure.repositories.citizen_profile_repository import InMemoryCitizenProfileRepository
from nilegov_stack.infrastructure.repositories.consent_record_repository import InMemoryConsentRecordRepository
from nilegov_stack.infrastructure.repositories.notification_event_repository import InMemoryNotificationEventRepository
from nilegov_stack.infrastructure.repositories.frappe_notification_event_repository import FrappeNotificationEventRepository


def test_notification_event_creation_and_validation():
    """Verifies that Notification Events validate their schema fields and preserve the disclaimer."""
    # Valid creation
    evt = NotificationEvent(
        notification_event_id="NOT-1",
        service_request_id="req-1",
        recipient="demo@example.test",
        channel=NotificationChannel.EMAIL,
        message="Hello World"
    )
    assert evt.notification_event_id == "NOT-1"
    assert "Prototype simulation only." in evt.disclaimer

    # Missing fields raises ValueError
    with pytest.raises(ValueError, match="Service Request ID is required"):
        NotificationEvent("NOT-1", "", "demo", "Email", "Msg")
    with pytest.raises(ValueError, match="Recipient reference is required"):
        NotificationEvent("NOT-1", "req-1", "", "Email", "Msg")
    with pytest.raises(ValueError, match="Message content is required"):
        NotificationEvent("NOT-1", "req-1", "demo", "Email", "")

    # Invalid recipient type
    with pytest.raises(ValueError, match="Invalid recipient type"):
        NotificationEvent("NOT-1", "req-1", "demo", "Email", "Msg", recipient_type="Invalid")

    # Invalid channel
    with pytest.raises(ValueError, match="Invalid channel"):
        NotificationEvent("NOT-1", "req-1", "demo", "InvalidChannel", "Msg")

    # Invalid delivery status
    with pytest.raises(ValueError, match="Invalid delivery status"):
        NotificationEvent("NOT-1", "req-1", "demo", "Email", "Msg", delivery_status="Invalid")

    # Invalid message type
    with pytest.raises(ValueError, match="Invalid message type"):
        NotificationEvent("NOT-1", "req-1", "demo", "Email", "Msg", message_type="Invalid")


def test_notification_event_state_transitions():
    """Verifies valid state transitions: queue, cancel, send, fail."""
    evt = NotificationEvent(
        notification_event_id="NOT-1",
        service_request_id="req-1",
        recipient="demo@example.test",
        channel=NotificationChannel.EMAIL,
        message="Hello World"
    )
    assert evt.delivery_status == NotificationDeliveryStatus.DRAFT

    evt.queue()
    assert evt.delivery_status == NotificationDeliveryStatus.QUEUED

    evt.simulated_send(12345.0)
    assert evt.delivery_status == NotificationDeliveryStatus.SIMULATED_SENT
    assert evt.simulated_sent_at == 12345.0

    # Once sent, it cannot be cancelled or queued
    with pytest.raises(ValueError, match="Cannot cancel a completed notification"):
        evt.cancel()
    with pytest.raises(ValueError, match="Cannot queue a completed notification"):
        evt.queue()

    # Verify failure transition
    evt2 = NotificationEvent(
        notification_event_id="NOT-2",
        service_request_id="req-1",
        recipient="demo@example.test",
        channel=NotificationChannel.EMAIL,
        message="Hello World"
    )
    evt2.simulated_fail(67890.0, "Gateway offline")
    assert evt2.delivery_status == NotificationDeliveryStatus.SIMULATED_FAILED
    assert evt2.simulated_failed_at == 67890.0
    assert evt2.failure_reason == "Gateway offline"


def test_consent_aware_notification_behavior():
    """Verifies that citizen consent dictates whether notifications queue or transition to not required."""
    request_repo = InMemoryServiceRequestRepository()
    profile_repo = InMemoryCitizenProfileRepository()
    consent_repo = InMemoryConsentRecordRepository()
    notification_repo = InMemoryNotificationEventRepository()

    # Setup profile & request
    nin = NIN("CF900000000000")
    profile = CitizenProfile("CP-1", "Demo Citizen A", "+256700000001", "Ntinda", nin=nin)
    profile_repo.save(profile)

    req = ServiceRequest("req-1", "NGS-NIRA-2026-0001", nin, "Demo Citizen A", "+256700000001", "Ntinda", "Lost ID", citizen_profile_id="CP-1")
    request_repo.save(req)

    use_case = CreateNotificationEvent(request_repo, profile_repo, consent_repo, notification_repo)

    # 1. Missing consent -> defaults to NOT_REQUIRED
    evt_missing = use_case.execute("req-1", NotificationMessageType.RECEIVED, timestamp=100.0)
    assert evt_missing.consent_checked is True
    assert evt_missing.consent_status_at_trigger == "Missing"
    assert evt_missing.delivery_status == NotificationDeliveryStatus.NOT_REQUIRED

    # 2. Expired consent -> NOT_REQUIRED
    expired_consent = ConsentRecord("CON-1", "CP-1", "Status Notifications", ConsentChannel.PHONE, expiry_time=50.0, consent_status=ConsentStatus.EXPIRED)
    consent_repo.save(expired_consent)
    evt_expired = use_case.execute("req-1", NotificationMessageType.RECEIVED, timestamp=100.0)
    assert evt_expired.delivery_status == NotificationDeliveryStatus.NOT_REQUIRED

    # 3. Withdrawn consent -> NOT_REQUIRED
    withdrawn_consent = ConsentRecord("CON-1", "CP-1", "Status Notifications", ConsentChannel.PHONE, consent_status=ConsentStatus.WITHDRAWN)
    consent_repo.save(withdrawn_consent)
    evt_withdrawn = use_case.execute("req-1", NotificationMessageType.RECEIVED, timestamp=100.0)
    assert evt_withdrawn.delivery_status == NotificationDeliveryStatus.NOT_REQUIRED

    # 4. Active/Granted consent -> QUEUED
    granted_consent = ConsentRecord("CON-1", "CP-1", "Status Notifications", ConsentChannel.PHONE, consent_status=ConsentStatus.GRANTED)
    consent_repo.save(granted_consent)
    evt_granted = use_case.execute("req-1", NotificationMessageType.RECEIVED, timestamp=100.0)
    assert evt_granted.delivery_status == NotificationDeliveryStatus.QUEUED


def test_simulated_gateway_determinism():
    """Verifies that the SimulatedNotificationGateway processes events cleanly without network interactions."""
    gateway = SimulatedNotificationGateway()
    evt = NotificationEvent(
        notification_event_id="NOT-1",
        service_request_id="req-1",
        recipient="demo@example.test",
        channel=NotificationChannel.EMAIL,
        message="Hello email",
        message_title="Verify Email"
    )

    success = gateway.send_simulated_notification(evt)
    assert success is True
    assert len(gateway.email_logs) == 1
    assert gateway.email_logs[0]["email_address"] == "demo@example.test"
    assert gateway.email_logs[0]["subject"] == "Verify Email"

    # SMS check
    evt_sms = NotificationEvent(
        notification_event_id="NOT-2",
        service_request_id="req-1",
        recipient="+256700000001",
        channel=NotificationChannel.SMS,
        message="Hello SMS"
    )
    success_sms = gateway.send_simulated_notification(evt_sms)
    assert success_sms is True
    assert len(gateway.sms_logs) == 1
    assert gateway.sms_logs[0]["phone_number"] == "+256700000001"


def test_workflow_and_sla_notification_generation():
    """Verifies that workflow status transitions and SLA warnings generate correct notification events."""
    request_repo = InMemoryServiceRequestRepository()
    profile_repo = InMemoryCitizenProfileRepository()
    consent_repo = InMemoryConsentRecordRepository()
    notification_repo = InMemoryNotificationEventRepository()

    nin = NIN("CF900000000000")
    profile = CitizenProfile("CP-1", "Demo Citizen A", "+256700000001", "Ntinda", nin=nin)
    profile_repo.save(profile)

    req = ServiceRequest("req-1", "NGS-NIRA-2026-0001", nin, "Demo Citizen A", "+256700000001", "Ntinda", "Lost ID", citizen_profile_id="CP-1")
    request_repo.save(req)

    # Active status consent
    consent = ConsentRecord("CON-1", "CP-1", "Status Notifications", ConsentChannel.PHONE, consent_status=ConsentStatus.GRANTED)
    consent_repo.save(consent)

    use_case = CreateNotificationEvent(request_repo, profile_repo, consent_repo, notification_repo)

    # 1. Workflow transition notification (Ready for Collection)
    evt1 = use_case.execute("req-1", NotificationMessageType.READY, timestamp=100.0)
    assert evt1.delivery_status == NotificationDeliveryStatus.QUEUED
    assert "ready for collection" in evt1.message.lower()

    # 2. SLA At Risk Warning notification
    evt2 = use_case.execute("req-1", NotificationMessageType.RISK, timestamp=100.0)
    assert evt2.delivery_status == NotificationDeliveryStatus.QUEUED
    assert "at-risk" in evt2.message.lower()

    # 3. SLA Overdue Breach notification
    evt3 = use_case.execute("req-1", NotificationMessageType.OVERDUE, timestamp=100.0)
    assert evt3.delivery_status == NotificationDeliveryStatus.QUEUED
    assert "sla breach" in evt3.message.lower()

    # 4. Supervisor Escalated notification
    evt4 = use_case.execute("req-1", NotificationMessageType.ESCALATED, extra_params={"supervisor": "supervisor_demo", "reason": "delay"}, timestamp=100.0)
    assert evt4.delivery_status == NotificationDeliveryStatus.QUEUED
    assert "escalated to supervisor_demo" in evt4.message.lower()


def test_use_cases_and_queries():
    """Verifies listing use cases and delivery action workflows."""
    request_repo = InMemoryServiceRequestRepository()
    notification_repo = InMemoryNotificationEventRepository()
    gateway = SimulatedNotificationGateway()

    nin = NIN("CF900000000000")
    req = ServiceRequest("req-1", "NGS-NIRA-2026-0001", nin, "Demo Citizen A", "+256700000001", "Ntinda", "Lost ID")
    request_repo.save(req)

    # Prepare events
    evt1 = NotificationEvent("NOT-1", "req-1", "+256700000001", NotificationChannel.SMS, "Message 1", NotificationDeliveryStatus.DRAFT, message_type=NotificationMessageType.RECEIVED)
    evt2 = NotificationEvent("NOT-2", "req-1", "demo@example.test", NotificationChannel.EMAIL, "Message 2", NotificationDeliveryStatus.QUEUED, message_type=NotificationMessageType.READY)
    evt3 = NotificationEvent("NOT-3", "req-1", "invalid-recipient", NotificationChannel.EMAIL, "Message 3", NotificationDeliveryStatus.QUEUED, message_type=NotificationMessageType.OVERDUE)

    notification_repo.save(evt1)
    notification_repo.save(evt2)
    notification_repo.save(evt3)

    # 1. Queue Event
    queue_uc = QueueNotificationEvent(notification_repo)
    queue_uc.execute("NOT-1")
    assert notification_repo.get_by_id("NOT-1").delivery_status == NotificationDeliveryStatus.QUEUED

    # 2. Cancel Event
    cancel_uc = CancelNotificationEvent(notification_repo)
    cancel_uc.execute("NOT-1")
    assert notification_repo.get_by_id("NOT-1").delivery_status == NotificationDeliveryStatus.CANCELLED

    # 3. Send Event (Success)
    send_uc = SendSimulatedNotification(notification_repo, gateway)
    send_uc.execute("NOT-2", timestamp=200.0)
    assert notification_repo.get_by_id("NOT-2").delivery_status == NotificationDeliveryStatus.SIMULATED_SENT
    assert notification_repo.get_by_id("NOT-2").simulated_sent_at == 200.0

    # 4. Send Event (Failure due to format check)
    send_uc.execute("NOT-3", timestamp=200.0)
    assert notification_repo.get_by_id("NOT-3").delivery_status == NotificationDeliveryStatus.SIMULATED_FAILED
    assert notification_repo.get_by_id("NOT-3").failure_reason is not None

    # 5. Queries
    by_req = ListNotificationsByServiceRequest(notification_repo).execute("req-1")
    assert len(by_req) == 3

    by_channel = ListNotificationsByChannel(notification_repo).execute(NotificationChannel.EMAIL)
    assert len(by_channel) == 2

    by_status = ListNotificationsByDeliveryStatus(notification_repo).execute(NotificationDeliveryStatus.SIMULATED_SENT)
    assert len(by_status) == 1
    assert by_status[0].notification_event_id == "NOT-2"


@patch("frappe.db.exists")
@patch("frappe.new_doc")
@patch("frappe.get_doc")
def test_frappe_notification_event_repository_save(mock_get_doc, mock_new_doc, mock_exists):
    """Verifies that FrappeNotificationEventRepository correctly saves fields to Frappe."""
    mock_exists.return_value = False
    mock_doc = MagicMock()
    mock_new_doc.return_value = mock_doc

    repo = FrappeNotificationEventRepository()
    evt = NotificationEvent(
        notification_event_id="NOT-1",
        service_request_id="req-1",
        recipient="demo@example.test",
        channel=NotificationChannel.EMAIL,
        message="Hello world",
        delivery_status=NotificationDeliveryStatus.QUEUED,
        citizen_profile_id="CP-1",
        consent_record_id="CON-1",
        message_type=NotificationMessageType.READY,
        message_title="Your card is ready",
        consent_checked=True,
        consent_status_at_trigger="Granted",
        disclaimer="Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."
    )

    repo.save(evt)

    mock_exists.assert_any_call("NileGov Citizen Notification", "NOT-1")
    assert mock_doc.service_request == "req-1"
    assert mock_doc.citizen_profile == "CP-1"
    assert mock_doc.consent_record == "CON-1"
    assert mock_doc.recipient == "demo@example.test"
    assert mock_doc.channel == NotificationChannel.EMAIL
    assert mock_doc.message == "Hello world"
    assert mock_doc.delivery_status == NotificationDeliveryStatus.QUEUED
    assert mock_doc.message_type == NotificationMessageType.READY
    assert mock_doc.message_title == "Your card is ready"
    assert mock_doc.consent_checked == 1
    assert mock_doc.consent_status_at_trigger == "Granted"
    assert "Prototype simulation only." in mock_doc.disclaimer

    mock_doc.save.assert_called_once()
