# Frappe-based Citizen Profile Repository
# Prototype simulation only. No live Government registry access.

try:
    import frappe
except ImportError:
    frappe = None

from typing import Optional
from nilegov_stack.application.ports import CitizenProfileRepository
from nilegov_stack.domain.citizen import CitizenProfile, PreferredContactChannel, CitizenProfileStatus
from nilegov_stack.domain.value_objects import NIN


class FrappeCitizenProfileRepository(CitizenProfileRepository):
    """Frappe-based repository for persisting and loading Citizen Profile aggregates."""

    def _check_frappe(self):
        if not frappe:
            raise ImportError("Frappe framework is not loaded in this environment.")

    def save(self, profile: CitizenProfile) -> None:
        self._check_frappe()
        
        # Load or create document
        if frappe.db.exists("NileGov Citizen Profile", profile.citizen_profile_id):
            doc = frappe.get_doc("NileGov Citizen Profile", profile.citizen_profile_id)
        else:
            doc = frappe.new_doc("NileGov Citizen Profile")
            doc.citizen_profile_id = profile.citizen_profile_id
            
        doc.full_name = profile.full_name
        doc.phone = profile.phone
        doc.email = profile.email
        doc.location = profile.location
        doc.division_or_area = profile.division_or_area
        doc.preferred_contact_channel = profile.preferred_contact_channel
        doc.status = profile.status
        doc.nin = str(profile.nin) if profile.nin else None
        
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    def get_by_id(self, profile_id: str) -> Optional[CitizenProfile]:
        self._check_frappe()
        if not frappe.db.exists("NileGov Citizen Profile", profile_id):
            return None
            
        doc = frappe.get_doc("NileGov Citizen Profile", profile_id)
        return self._map_doc_to_aggregate(doc)

    def get_by_nin(self, nin: str) -> Optional[CitizenProfile]:
        self._check_frappe()
        profile_id = frappe.db.get_value("NileGov Citizen Profile", {"nin": nin}, "name")
        if not profile_id:
            return None
        return self.get_by_id(profile_id)

    def _map_doc_to_aggregate(self, doc) -> CitizenProfile:
        nin_vo = NIN(doc.nin) if doc.nin else None
        
        profile = CitizenProfile(
            citizen_profile_id=doc.citizen_profile_id,
            full_name=doc.full_name,
            phone=doc.phone,
            location=doc.location,
            email=doc.email,
            division_or_area=doc.division_or_area,
            preferred_contact_channel=doc.preferred_contact_channel or PreferredContactChannel.PHONE,
            status=doc.status or CitizenProfileStatus.ACTIVE,
            nin=nin_vo,
            created_at=frappe.utils.get_timestamp(doc.creation),
            updated_at=frappe.utils.get_timestamp(doc.modified)
        )
        return profile
