# Citizen Profile Domain Model for NileGov Stack
# Digi-Verse Uganda Limited

from typing import Optional
from nilegov_stack.domain.value_objects import NIN, Email, PhoneNumber


class PreferredContactChannel:
    PHONE = "Phone"
    EMAIL = "Email"
    PORTAL = "Portal"
    SMS = "SMS"
    WHATSAPP = "WhatsApp"
    OFFICER_ASSISTED = "Officer Assisted"
    
    @classmethod
    def all(cls):
        return {cls.PHONE, cls.EMAIL, cls.PORTAL, cls.SMS, cls.WHATSAPP, cls.OFFICER_ASSISTED}


class CitizenProfileStatus:
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ARCHIVED = "Archived"
    DEMO_ONLY = "Demo Only"
    
    @classmethod
    def all(cls):
        return {cls.ACTIVE, cls.INACTIVE, cls.ARCHIVED, cls.DEMO_ONLY}


class CitizenProfile:
    """Domain model representing a citizen profile foundation."""
    
    def __init__(
        self,
        citizen_profile_id: str,
        full_name: str,
        phone: str,
        location: str,
        email: Optional[str] = None,
        division_or_area: Optional[str] = None,
        preferred_contact_channel: str = PreferredContactChannel.PHONE,
        status: str = CitizenProfileStatus.ACTIVE,
        nin: Optional[NIN] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ):
        if not citizen_profile_id:
            raise ValueError("Citizen Profile ID cannot be empty.")
        if not full_name or not full_name.strip():
            raise ValueError("Full name cannot be empty.")
        if not location or not location.strip():
            raise ValueError("Location cannot be empty.")
            
        # Basic validation for phone
        self.phone_vo = PhoneNumber(phone)
        self.phone = phone
        
        # Optional Email validation
        self.email_vo = Email(email) if email else None
        self.email = email
        
        # Preferred Contact Channel check
        if preferred_contact_channel not in PreferredContactChannel.all():
            raise ValueError(f"Invalid preferred contact channel: {preferred_contact_channel}")
            
        # Status check
        if status not in CitizenProfileStatus.all():
            raise ValueError(f"Invalid profile status: {status}")
            
        self.citizen_profile_id = citizen_profile_id
        self.full_name = full_name
        self.location = location
        self.division_or_area = division_or_area
        self.preferred_contact_channel = preferred_contact_channel
        self.status = status
        self.nin = nin
        self.created_at = created_at
        self.updated_at = updated_at

    def update_contact_details(
        self,
        phone: str,
        email: Optional[str] = None,
        preferred_contact_channel: Optional[str] = None
    ):
        """Updates contact info with domain level validation."""
        self.phone_vo = PhoneNumber(phone)
        self.phone = phone
        
        if email:
            self.email_vo = Email(email)
            self.email = email
        else:
            self.email_vo = None
            self.email = None
            
        if preferred_contact_channel:
            if preferred_contact_channel not in PreferredContactChannel.all():
                raise ValueError(f"Invalid preferred contact channel: {preferred_contact_channel}")
            self.preferred_contact_channel = preferred_contact_channel
            
    def validate_safe_demo_data(self):
        """Ensures profile status and details represent demo/testing characteristics."""
        if self.status == CitizenProfileStatus.DEMO_ONLY:
            return True
        # Fictional check: ensure email is a test domain or phone is within mock ranges
        if self.email and not self.email.endswith(".test") and not self.email.endswith("example.ug") and not self.email.endswith("example.test"):
            raise ValueError("Production email domains are prohibited for demo profiles.")
        return True
