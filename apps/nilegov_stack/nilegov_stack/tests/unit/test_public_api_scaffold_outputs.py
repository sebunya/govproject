# Pass 11B-7C: Public REST API Scaffold — Output Payload Unit Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external integration.
#

import pytest
from nilegov_stack.interfaces.frappe.api.public_readiness import (
    get_service_catalogue_preview,
    get_lost_nid_intake_schema,
    get_evidence_metadata_schema,
    get_consent_capture_schema,
    get_prototype_payment_requirement_preview,
    get_interoperability_disclaimer,
)

# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestPublicAPIScaffoldOutputs:
    def test_get_service_catalogue_preview(self):
        res = get_service_catalogue_preview()
        assert res["success"] is True
        assert "correlation_id" in res
        assert "timestamp" in res
        assert "Prototype" in res["disclaimer"] or "simulation" in res["disclaimer"]
        
        data = res["data"]
        assert isinstance(data["services"], list)
        assert len(data["services"]) == 2
        for s in data["services"]:
            assert "service_code" in s
            assert "service_name" in s
            assert "service_category" in s
            assert "estimated_fee" in s

    def test_get_lost_nid_intake_schema(self):
        res = get_lost_nid_intake_schema()
        assert res["success"] is True
        data = res["data"]
        assert data["doc_type"] == "NileGov Service Request"
        
        fields = {f["fieldname"]: f for f in data["fields"]}
        assert "citizen_full_name" in fields
        assert "nin" in fields
        assert "phone" in fields
        
        # Check NIN is optional in form schema preview
        assert fields["nin"]["reqd"] is False
        assert "Prototype identifier input" in fields["nin"]["description"]

    def test_get_evidence_metadata_schema(self):
        res = get_evidence_metadata_schema()
        assert res["success"] is True
        data = res["data"]
        assert data["doc_type"] == "NileGov Evidence Document"
        
        fields = {f["fieldname"] for f in data["fields"]}
        assert "service_request" in fields
        assert "document_type" in fields
        assert "document_title" in fields
        assert "verification_status" not in fields

    def test_get_consent_capture_schema(self):
        res = get_consent_capture_schema()
        assert res["success"] is True
        data = res["data"]
        assert data["doc_type"] == "NileGov Consent Record"
        
        fields = {f["fieldname"] for f in data["fields"]}
        assert "citizen_profile" in fields
        assert "consent_purpose" in fields
        assert "consent_status" in fields
        assert "consent_given_at" not in fields

    def test_get_prototype_payment_requirement_preview(self):
        res = get_prototype_payment_requirement_preview()
        assert res["success"] is True
        data = res["data"]
        assert data["payment_required"] is True
        assert data["payment_purpose"] == "NID Replacement Processing Fee"
        assert "sandbox" in data["disclaimer"]

    def test_get_interoperability_disclaimer(self):
        res = get_interoperability_disclaimer()
        assert res["success"] is True
        data = res["data"]
        assert data["live_registry_connected"] is False
        assert data["production_payment_connected"] is False
        
        flags = data["connected_systems"]
        for k, v in flags.items():
            assert v is False
