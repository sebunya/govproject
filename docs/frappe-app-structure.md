# NileGov Stack Frappe App Structure

> [!NOTE]
> Static structure is prepared. Runtime validation will be completed in Pass 2B inside a real Frappe bench/site.

This document details the module directory paths and file organization conventions for custom **DocTypes** in the **NileGov Stack** application.

---

## Path & Module Mapping

* **App Name:** `nilegov_stack`
* **Python Package Path:** `apps/nilegov_stack/nilegov_stack/`
* **Module Declared in `modules.txt`:** `NileGov Stack`
* **Scrubbed Module Folder:** `nilegov_stack`

### The Expected Path
Following Frappe conventions, custom DocTypes are stored in the scrubbed module folder directory under the app's python package:
```text
apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/<doctype_folder>/
```

Within each DocType subdirectory, Frappe expects exactly:
1. `<doctype_folder>.json` (the document schema descriptor)
2. `<doctype_folder>.py` (the Gunicorn/Python controller class extending `frappe.model.document.Document`)

---

## 13 Custom DocTypes and Paths

The following directories are established under `apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/`:
1. `nilegov_citizen_profile/`
2. `nilegov_service_type/`
3. `nilegov_service_request/`
4. `nilegov_consent_record/`
5. `nilegov_evidence_document/`
6. `nilegov_simulated_identity_verification/`
7. `nilegov_case_note/`
8. `nilegov_sla_rule/`
9. `nilegov_sla_event/`
10. `nilegov_escalation_record/`
11. `nilegov_citizen_notification/`
12. `nilegov_audit_event/`
13. `nilegov_integration_simulation_log/`

---

## Deferred Runtime Verification (Pass 2B)

Since `bench` is not locally available and no Frappe database site exists on the host machine, standard runtime operations (migrating database columns, seeding data, executing Gunicorn controller pipelines, or verifying actual user permissions in the browser) are deferred.

In **Pass 2A (Static Persistence Layer Build)**, we verify these configurations using:
* Automated Python schema parsing tests checking for key configurations, Link types, fields, and forbidden terminology.
* Pure Python controller syntax compilation verification.
* Static checklist validation.

During **Pass 2B (Frappe Bench Validation)**, we will run the containerized bench environment to prove:
* Database migration completes (`bench migrate`).
* Seed data patches execute cleanly without duplicate inserts.
* Role fixtures populate the DB.
* Permission hooks load and restrict query sets.
