# Frappe-based Service Catalogue Repository
# Prototype service catalogue only. Not connected to a live government service registry.

try:
    import frappe
except ImportError:
    frappe = None

from typing import Optional, List
import json
from nilegov_stack.application.ports import ServiceCatalogueRepository
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem


class FrappeServiceCatalogueRepository(ServiceCatalogueRepository):
    """Frappe-based repository for persisting and loading Service Catalogue items."""

    def _check_frappe(self):
        if not frappe:
            raise ImportError("Frappe framework is not loaded in this environment.")

    def save(self, item: ServiceCatalogueItem) -> None:
        self._check_frappe()

        # Load or create document
        if frappe.db.exists("NileGov Service Catalogue", item.service_catalogue_id):
            doc = frappe.get_doc("NileGov Service Catalogue", item.service_catalogue_id)
        else:
            doc = frappe.new_doc("NileGov Service Catalogue")
            doc.service_catalogue_id = item.service_catalogue_id

        doc.service_name = item.service_name
        doc.service_code = item.service_code
        doc.responsible_mda_placeholder = item.responsible_mda_placeholder
        doc.service_category = item.service_category
        doc.service_description = item.service_description
        
        # Serialize list as comma-separated values
        doc.required_documents = ", ".join(item.required_documents) if item.required_documents else ""
        
        doc.fee_required = 1 if item.fee_required else 0
        doc.default_fee_amount = item.default_fee_amount
        doc.default_currency = item.default_currency
        doc.default_payment_purpose = item.default_payment_purpose
        doc.default_payment_provider = item.default_payment_provider
        doc.default_sla_rule = item.default_sla_rule
        doc.responsible_department = item.responsible_department
        doc.responsible_queue = item.responsible_queue
        doc.workflow_template = item.workflow_template
        doc.active_status = item.active_status
        doc.public_visibility = item.public_visibility
        doc.disclaimer = item.disclaimer

        doc.save(ignore_permissions=True)
        frappe.db.commit()

    def get_by_id(self, item_id: str) -> Optional[ServiceCatalogueItem]:
        self._check_frappe()
        if not frappe.db.exists("NileGov Service Catalogue", item_id):
            return None

        doc = frappe.get_doc("NileGov Service Catalogue", item_id)
        return self._map_doc_to_aggregate(doc)

    def get_by_code(self, service_code: str) -> Optional[ServiceCatalogueItem]:
        self._check_frappe()
        records = frappe.get_all(
            "NileGov Service Catalogue",
            filters={"service_code": service_code},
            pluck="name"
        )
        if not records:
            return None
        return self.get_by_id(records[0])

    def get_all(self) -> List[ServiceCatalogueItem]:
        self._check_frappe()
        records = frappe.get_all("NileGov Service Catalogue", pluck="name")
        results = []
        for rid in records:
            item = self.get_by_id(rid)
            if item:
                results.append(item)
        return results

    def get_active(self) -> List[ServiceCatalogueItem]:
        self._check_frappe()
        records = frappe.get_all(
            "NileGov Service Catalogue",
            filters={"active_status": "Active"},
            pluck="name"
        )
        results = []
        for rid in records:
            item = self.get_by_id(rid)
            if item:
                results.append(item)
        return results

    def get_demo(self) -> List[ServiceCatalogueItem]:
        self._check_frappe()
        records = frappe.get_all(
            "NileGov Service Catalogue",
            filters={"active_status": "Demo Only"},
            pluck="name"
        )
        results = []
        for rid in records:
            item = self.get_by_id(rid)
            if item:
                results.append(item)
        return results

    def get_by_category(self, category: str) -> List[ServiceCatalogueItem]:
        self._check_frappe()
        records = frappe.get_all(
            "NileGov Service Catalogue",
            filters={"service_category": category},
            pluck="name"
        )
        results = []
        for rid in records:
            item = self.get_by_id(rid)
            if item:
                results.append(item)
        return results

    def _map_doc_to_aggregate(self, doc) -> ServiceCatalogueItem:
        created_ts = None
        if doc.creation:
            created_ts = frappe.utils.get_timestamp(doc.creation)

        updated_ts = None
        if doc.modified:
            updated_ts = frappe.utils.get_timestamp(doc.modified)

        # Parse required documents
        docs_str = doc.required_documents or ""
        docs_list = [d.strip() for d in docs_str.split(",") if d.strip()]

        return ServiceCatalogueItem(
            service_catalogue_id=doc.service_catalogue_id or doc.name,
            service_name=doc.service_name,
            service_code=doc.service_code,
            responsible_mda_placeholder=doc.responsible_mda_placeholder,
            service_category=doc.service_category,
            service_description=doc.service_description,
            required_documents=docs_list,
            fee_required=bool(doc.fee_required),
            default_fee_amount=float(doc.default_fee_amount or 0.0),
            default_currency=doc.default_currency or "UGX",
            default_payment_purpose=doc.default_payment_purpose or "Not Applicable",
            default_payment_provider=doc.default_payment_provider or "Not Applicable",
            default_sla_rule=doc.default_sla_rule,
            responsible_department=doc.responsible_department,
            responsible_queue=doc.responsible_queue,
            workflow_template=doc.workflow_template or "Standard Application Workflow",
            active_status=doc.active_status or "Active",
            public_visibility=doc.public_visibility or "Demo Visible",
            created_at=created_ts,
            updated_at=updated_ts
        )
