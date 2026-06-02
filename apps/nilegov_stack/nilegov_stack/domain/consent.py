# Consent Record Entity for NileGov Stack
# Digi-Verse Uganda Limited

from typing import Optional


class ConsentPurpose:
    SERVICE_PROCESSING = "Service Request Processing"
    IDENTITY_VERIFICATION = "Simulated Identity Verification"
    PAYMENT_VERIFICATION = "Simulated Payment Verification"
    NOTIFICATIONS = "Status Notifications"
    INTEGRATION_READINESS = "Future MDA Integration Readiness"

    @classmethod
    def all(cls):
        return {
            cls.SERVICE_PROCESSING,
            cls.IDENTITY_VERIFICATION,
            cls.PAYMENT_VERIFICATION,
            cls.NOTIFICATIONS,
            cls.INTEGRATION_READINESS
        }


class ConsentChannel:
    WEB_FORM = "Web Form"
    OFFICER_ASSISTED = "Officer Assisted"
    PORTAL = "Portal"
    EMAIL = "Email"
    PHONE = "Phone"
    WHATSAPP = "WhatsApp"
    OTHER = "Other"

    @classmethod
    def all(cls):
        return {
            cls.WEB_FORM,
            cls.OFFICER_ASSISTED,
            cls.PORTAL,
            cls.EMAIL,
            cls.PHONE,
            cls.WHATSAPP,
            cls.OTHER
        }


class ConsentStatus:
    GRANTED = "Granted"
    WITHDRAWN = "Withdrawn"
    EXPIRED = "Expired"
    NOT_REQUIRED = "Not Required"
    PENDING = "Pending"

    @classmethod
    def all(cls):
        return {
            cls.GRANTED,
            cls.WITHDRAWN,
            cls.EXPIRED,
            cls.NOT_REQUIRED,
            cls.PENDING
        }


class ConsentRecord:
    """Represents a citizen's explicit verification and authorization record."""

    def __init__(
        self,
        consent_record_id: str,
        citizen_profile_id: str,
        consent_purpose: str,
        consent_channel: str,
        consent_status: str = ConsentStatus.GRANTED,
        consent_timestamp: Optional[float] = None,
        service_request_id: Optional[str] = None,
        expiry_time: Optional[float] = None,
        withdrawal_timestamp: Optional[float] = None,
        recorded_by: Optional[str] = None,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ):
        if not consent_record_id:
            raise ValueError("Consent Record ID cannot be empty.")
        if not citizen_profile_id:
            raise ValueError("Citizen Profile ID cannot be empty.")
        if consent_purpose not in ConsentPurpose.all():
            raise ValueError(f"Invalid consent purpose: {consent_purpose}")
        if consent_channel not in ConsentChannel.all():
            raise ValueError(f"Invalid consent channel: {consent_channel}")
        if consent_status not in ConsentStatus.all():
            raise ValueError(f"Invalid consent status: {consent_status}")

        self.consent_record_id = consent_record_id
        self.citizen_profile_id = citizen_profile_id
        self.consent_purpose = consent_purpose
        self.consent_channel = consent_channel
        self.consent_status = consent_status
        self.consent_timestamp = consent_timestamp
        self.service_request_id = service_request_id
        self.expiry_time = expiry_time
        self.withdrawal_timestamp = withdrawal_timestamp
        self.recorded_by = recorded_by
        self.notes = notes
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = created_at
        self.updated_at = updated_at

    def withdraw(self, timestamp: float):
        """Transition the consent record status to Withdrawn."""
        self.consent_status = ConsentStatus.WITHDRAWN
        self.withdrawal_timestamp = timestamp
        self.updated_at = timestamp

    def is_active(self, current_time: float) -> bool:
        """Determines if the consent is currently active and granted."""
        if self.consent_status != ConsentStatus.GRANTED:
            return False
        if self.expiry_time and current_time >= self.expiry_time:
            return False
        return True
