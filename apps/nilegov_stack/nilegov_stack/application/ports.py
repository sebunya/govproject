# Application Ports & Interfaces for NileGov Stack
# Digi-Verse Uganda Limited

from abc import ABC, abstractmethod
from typing import Optional, List
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.domain.citizen import CitizenProfile
from nilegov_stack.domain.consent import ConsentRecord
from nilegov_stack.domain.evidence import EvidenceDocument
from nilegov_stack.domain.sla import SLARule
from nilegov_stack.domain.notification import NotificationEvent
from nilegov_stack.domain.payment import PaymentRecord
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem
from nilegov_stack.domain.reporting_snapshot import ReportingSnapshot


class ServiceRequestRepository(ABC):
    """Port interface for persisting and loading Service Request aggregates."""
    
    @abstractmethod
    def save(self, service_request: ServiceRequest) -> None:
        """Persists the state of the Service Request aggregate."""
        pass

    @abstractmethod
    def get_by_id(self, request_id: str) -> Optional[ServiceRequest]:
        """Loads a Service Request aggregate by its unique ID."""
        pass

    @abstractmethod
    def get_by_reference(self, reference_no: str) -> Optional[ServiceRequest]:
        """Loads a Service Request aggregate by its reference number."""
        pass

    @abstractmethod
    def get_by_citizen_profile(self, profile_id: str) -> List[ServiceRequest]:
        """Loads all Service Requests linked to a specific Citizen Profile ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[ServiceRequest]:
        """Loads all Service Requests in the system."""
        pass


class CitizenProfileRepository(ABC):
    """Port interface for persisting and loading Citizen Profile aggregates."""
    
    @abstractmethod
    def save(self, profile: CitizenProfile) -> None:
        """Persists the state of the Citizen Profile."""
        pass

    @abstractmethod
    def get_by_id(self, profile_id: str) -> Optional[CitizenProfile]:
        """Loads a Citizen Profile by its unique ID."""
        pass

    @abstractmethod
    def get_by_nin(self, nin: str) -> Optional[CitizenProfile]:
        """Loads a Citizen Profile by its National Identification Number (NIN)."""
        pass


class ConsentRecordRepository(ABC):
    """Port interface for persisting and loading Consent Records."""
    
    @abstractmethod
    def save(self, consent_record: ConsentRecord) -> None:
        """Persists the state of the Consent Record."""
        pass

    @abstractmethod
    def get_by_id(self, consent_id: str) -> Optional[ConsentRecord]:
        """Loads a Consent Record by its unique ID."""
        pass

    @abstractmethod
    def get_by_citizen_profile(self, profile_id: str) -> List[ConsentRecord]:
        """Loads all Consent Records linked to a specific Citizen Profile ID."""
        pass

    @abstractmethod
    def get_by_service_request(self, request_id: str) -> List[ConsentRecord]:
        """Loads all Consent Records linked to a specific Service Request ID."""
        pass


class NotificationGateway(ABC):
    """Port interface for dispatching citizen notifications."""
    
    @abstractmethod
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Sends a text message to a citizen."""
        pass

    @abstractmethod
    def send_email(self, email_address: str, subject: str, body: str) -> bool:
        """Sends an email message to a citizen."""
        pass


class IdentityVerificationGateway(ABC):
    """Port interface for interacting with simulated registry checks (e.g. NIRA)."""
    
    @abstractmethod
    def verify_identity(self, nin: str) -> dict:
        """Performs simulated registry verification check for a citizen NIN."""
        pass


class PaymentVerificationGateway(ABC):
    """Port interface for interacting with simulated payment systems."""
    
    @abstractmethod
    def verify_payment(self, reference_no: str) -> dict:
        """Performs simulated payment validation check."""
        pass

    @abstractmethod
    def verify_payment_record(self, payment_record: PaymentRecord) -> dict:
        """Performs simulated payment validation check for a specific PaymentRecord aggregate."""
        pass


class EvidenceDocumentRepository(ABC):
    """Port interface for persisting and loading Evidence Documents."""
    
    @abstractmethod
    def save(self, evidence_document: EvidenceDocument) -> None:
        """Persists the state of the Evidence Document."""
        pass

    @abstractmethod
    def get_by_id(self, evidence_id: str) -> Optional[EvidenceDocument]:
        """Loads an Evidence Document by its unique ID."""
        pass

    @abstractmethod
    def get_by_citizen_profile(self, profile_id: str) -> List[EvidenceDocument]:
        """Loads all Evidence Documents linked to a specific Citizen Profile ID."""
        pass

    @abstractmethod
    def get_by_service_request(self, request_id: str) -> List[EvidenceDocument]:
        """Loads all Evidence Documents linked to a specific Service Request ID."""
        pass


class SLARuleRepository(ABC):
    """Port interface for persisting and loading SLA Rule aggregates."""
    
    @abstractmethod
    def save(self, rule: SLARule) -> None:
        """Persists the state of the SLA Rule."""
        pass

    @abstractmethod
    def get_by_id(self, rule_id: str) -> Optional[SLARule]:
        """Loads an SLA Rule by its unique ID."""
        pass

    @abstractmethod
    def get_by_service_type(self, service_type: str) -> Optional[SLARule]:
        """Loads an SLA Rule for a specific service type."""
        pass

    @abstractmethod
    def get_all(self) -> List[SLARule]:
        """Loads all SLA Rules in the system."""
        pass


class NotificationEventRepository(ABC):
    """Port interface for persisting and loading Notification Events."""

    @abstractmethod
    def save(self, event: NotificationEvent) -> None:
        """Persists the Notification Event state."""
        pass

    @abstractmethod
    def get_by_id(self, event_id: str) -> Optional[NotificationEvent]:
        """Retrieves a Notification Event by its unique ID."""
        pass

    @abstractmethod
    def get_by_service_request(self, request_id: str) -> List[NotificationEvent]:
        """Retrieves all Notification Events linked to a specific Service Request ID."""
        pass

    @abstractmethod
    def get_by_citizen_profile(self, profile_id: str) -> List[NotificationEvent]:
        """Retrieves all Notification Events linked to a specific Citizen Profile ID."""
        pass

    @abstractmethod
    def get_by_channel(self, channel: str) -> List[NotificationEvent]:
        """Retrieves all Notification Events routed through a specific channel."""
        pass

    @abstractmethod
    def get_by_delivery_status(self, status: str) -> List[NotificationEvent]:
        """Retrieves all Notification Events in a specific delivery status."""
        pass

    @abstractmethod
    def get_all(self) -> List[NotificationEvent]:
        """Retrieves all Notification Events."""
        pass


class PaymentRecordRepository(ABC):
    """Port interface for persisting and loading Payment Record aggregates."""

    @abstractmethod
    def save(self, payment_record: PaymentRecord) -> None:
        """Persists the PaymentRecord aggregate."""
        pass

    @abstractmethod
    def get_by_id(self, payment_id: str) -> Optional[PaymentRecord]:
        """Loads a PaymentRecord by its unique ID."""
        pass

    @abstractmethod
    def get_by_service_request(self, request_id: str) -> List[PaymentRecord]:
        """Loads all PaymentRecords linked to a specific Service Request ID."""
        pass

    @abstractmethod
    def get_by_citizen_profile(self, profile_id: str) -> List[PaymentRecord]:
        """Loads all PaymentRecords linked to a specific Citizen Profile ID."""
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[PaymentRecord]:
        """Loads all PaymentRecords in a specific payment status."""
        pass

    @abstractmethod
    def get_by_reconciliation_status(self, status: str) -> List[PaymentRecord]:
        """Loads all PaymentRecords in a specific reconciliation status."""
        pass

    @abstractmethod
    def get_all(self) -> List[PaymentRecord]:
        """Loads all PaymentRecords in the system."""
        pass


class ServiceCatalogueRepository(ABC):
    """Port interface for persisting and loading Service Catalogue Item aggregates."""

    @abstractmethod
    def save(self, item: ServiceCatalogueItem) -> None:
        """Persists the state of the Service Catalogue Item."""
        pass

    @abstractmethod
    def get_by_id(self, item_id: str) -> Optional[ServiceCatalogueItem]:
        """Loads a Service Catalogue Item by its unique ID."""
        pass

    @abstractmethod
    def get_by_code(self, service_code: str) -> Optional[ServiceCatalogueItem]:
        """Loads a Service Catalogue Item by its service code."""
        pass

    @abstractmethod
    def get_all(self) -> List[ServiceCatalogueItem]:
        """Loads all Service Catalogue Items."""
        pass

    @abstractmethod
    def get_active(self) -> List[ServiceCatalogueItem]:
        """Loads all Active Service Catalogue Items."""
        pass

    @abstractmethod
    def get_demo(self) -> List[ServiceCatalogueItem]:
        """Loads all Demo Only Service Catalogue Items."""
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[ServiceCatalogueItem]:
        """Loads all Service Catalogue Items in a specific category."""
        pass


class ReportingSnapshotRepository(ABC):
    """Port interface for persisting and loading Reporting Snapshot aggregates."""

    @abstractmethod
    def save(self, snapshot: ReportingSnapshot) -> None:
        """Persists the state of the Reporting Snapshot."""
        pass

    @abstractmethod
    def get_by_id(self, snapshot_id: str) -> Optional[ReportingSnapshot]:
        """Loads a Reporting Snapshot by its unique ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[ReportingSnapshot]:
        """Loads all Reporting Snapshots."""
        pass



