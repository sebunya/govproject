# NileGov Stack — Pass 11B Implementation Plan
# Digi-Verse Uganda Limited
# Frappe Native Completeness

> **Prototype simulation only. No live Government registry access.**
> This plan covers pure Frappe-layer completeness work required for
> submission-readiness. No live NIRA, UGHub, URA, NITA-U, MDA, or
> production payment integration is claimed or planned.

---

## 1. Audit Context

- **Audit Date:** 2026-06-02
- **Branch:** main
- **Latest commit:** `9c5b0e9` (Pass 11A walkthrough)
- **Test count:** 525/525 passed
- **Python compile:** Clean
- **`.env` tracked:** No

---

## 2. Frappe-Native Gap Table

| # | Feature Area | Status | Evidence Found | Gap | Risk if Ignored | Sub-pass | Code Now? | Runtime Validation? | Priority |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Reporting Snapshot DocType** | Missing | No `nilegov_reporting_snapshot/` directory in `doctype/`. Domain model exists at `domain/reporting_snapshot.py`. | No Frappe DocType JSON, no controller, no JS, no schema test entry | Evaluators cannot see M&E data in Frappe Desk. Central reporting feature invisible. | 11B-1 | Yes | Yes | **Critical** |
| 2 | **Role fixtures — hooks.py mismatch** | Broken | `hooks.py` fixtures list: `["Citizen","Service Desk Officer","Supervisor","Registry Liaison Officer","MDA Leadership","MDA Administrator","System Administrator"]`. `permission_policy.py` defines 8 NileGov-prefixed roles: `NileGov Citizen Officer`, `NileGov Records Officer`, etc. `seed_roles.py` seeds old names. `interfaces/permissions.py` references old names. `test_doctype_schemas.py` asserts old names. | **Three independent sources use different role names**: hooks.py, application/permission_policy.py, and interfaces/permissions.py. At runtime all role checks in permissions.py will silently fail because old roles will never match the NileGov-prefixed roles. DocType permission rows all say `System Manager` only. | Role mismatch means no role-based access control works at runtime. Any evaluator logging in will either see nothing or see everything. **Highest severity runtime gap.** | 11B-2 | Yes | Yes | **Critical** |
| 3 | **Permission rows in DocType JSON** | Partial | All 15 DocType JSON files declare only `["System Manager"]` as the permitted role. The application domain defines 8 operational roles. | 7 operational roles have no permission rows in any DocType JSON. Officers, supervisors, records staff, payment staff, M&E viewers, MDA admins, system auditors all have zero DocType access at runtime. | Evaluators using non-admin accounts will not be able to open any DocType. Demo is invisible without `System Manager`. | 11B-2 | Yes | Yes | **Critical** |
| 4 | **Workspace navigation** | Partial | `nilegov_case_operations.json` exists with 4 shortcuts. `roles` array references old roles (`Service Desk Officer`, `Supervisor`, `System Administrator`). No links block, no charts block. | Workspace is basic, uses old role names, has no navigation links to Service Catalogue, SLA Rules, Reporting, etc. No charts or number cards. | Evaluators see a nearly empty workspace. Navigation is guesswork. | 11B-3 | Yes | Yes | **High** |
| 5 | **DocType JavaScript form scripts** | Critical gap | Only `nilegov_service_request.js` exists (2 simulated action buttons). 14 other DocTypes have no `.js` file. | No JS scripts for: Case Note, Citizen Profile, Evidence Document, Payment Record, Consent Record, SLA Rule, SLA Event, Escalation Record, Citizen Notification, Audit Event, Service Catalogue, Service Type, Integration Simulation Log, Simulated Identity Verification. | Evaluators see blank, inert forms. Custom buttons, status-based field hiding, conditional logic, and officer workflow actions are all absent. | 11B-4 | Yes | Yes | **High** |
| 6 | **Custom Desk buttons / whitelisted actions** | Partial | `nilegov_service_request.py` has 10 whitelisted methods. No JS exposes the majority of them (only identity check and payment check are in JS). Assign Officer, Escalate Case, Resolve Escalation, etc. are unreachable without JS buttons. | 8 of 10 whitelisted methods are wired up in Python but never called from the Frappe Desk UI because no JS triggers them. | Officers cannot perform most actions from the Frappe UI. The main workflow loop is broken in demo. | 11B-4 | Yes | Yes | **High** |
| 7 | **Query Reports** | Missing | No `report/` directory found anywhere under `nilegov_stack/`. | No Frappe Query Reports defined for: Case Status Summary, SLA Compliance, Officer Workload, Pending Payments, M&E Snapshot view. | Evaluators have no reporting view. M&E data is invisible at Frappe Desk level. | 11B-5 | Yes | Yes | **High** |
| 8 | **Dashboard charts / number cards** | Missing | `workspace.json` `charts` array is empty. No dashboard or number card JSON found. | No live counters or charts on the workspace for: total open cases, SLA breached count, pending payments, escalated cases. | Workspace feels like an empty shell. No "at a glance" data visible. | 11B-5 | Yes | Yes | **High** |
| 9 | **Print formats / PDF outputs** | Missing | No `print_format/` directory found. | No print format for: Service Request acknowledgement letter, Payment receipt, Citizen notification summary. | Evaluators cannot generate any output documents. Paper-trail proof of concept is absent. | 11B-6 | Yes | Yes | **Medium** |
| 10 | **Citizen Web Form / portal intake** | Missing | No `web_form/` directory found. `interfaces/frappe/pages/` is empty (`__init__.py` only). | No citizen-facing intake form. Citizens cannot self-submit. Demo relies entirely on officer-created records. | Citizen self-service narrative is broken. A core pitch element is absent. | 11B-7 | Yes | Yes | **High** |
| 11 | **REST/API endpoint scaffolding** | Stub only | `interfaces/frappe/api/__init__.py` exists but contains only a comment header. No `@frappe.whitelist()` endpoints defined here. Whitelisted methods exist only on DocType controllers. | No dedicated API module. API interoperability layer implemented in domain (Pass 8A-9B) but has no Frappe-callable REST surface beyond controller-embedded methods. | Integration partners cannot call any endpoint by name. API readiness narrative is incomplete. | 11B-7 | Yes | Yes | **Medium** |
| 12 | **Integration Simulation Log runtime usage** | Partial | DocType JSON and domain model exist. No JS form script to trigger simulation. No report to review simulation history. | Log records are created by domain code but there is no Frappe UI path to: view recent simulations, retry, or inspect payloads. | Integration readiness demo is invisible to evaluators. | 11B-4 | Yes | Yes | **Medium** |
| 13 | **Notifications / internal alerts** | Partial | `nilegov_citizen_notification` DocType exists (23 fields). Domain event model exists. No Frappe Email Alert, No SMS configuration, no Notification trigger setup. | Real notification delivery is not configured. Only domain-level `NotificationEvent` objects exist in memory. | Notification readiness is demo-only by assertion, not by evidence. | 11B-6 | Yes | Yes | **Medium** |
| 14 | **Assignment rules / ToDo readiness** | Missing | No Frappe Assignment Rule JSON defined. Service Request JS does call `assign_officer` whitelisted method but no automatic routing. | No automated assignment queue logic. Officers must be manually assigned every time. No auto-assignment based on queue or department. | Supervisor workflow demo requires manual steps that a real system would automate. | 11B-6 | Yes | Yes | **Low** |
| 15 | **Search / case lookup** | Partial | `nilegov_service_request` has fields for NIN, reference number, citizen name. No `search_fields` declared in JSON. | Without `search_fields`, Frappe search bar cannot find service requests by NIN or reference number. Officers must scroll through lists. | Simple lookup demo fails. Evaluators cannot find a specific case. | 11B-3 | Yes | Yes | **High** |
| 16 | **Form tours / onboarding** | Missing | No form tour JSON found. | No guided walkthrough for first-time demo users. | Minor: evaluators familiar with Frappe will manage without it. | Deferred | No | No | **Low** |
| 17 | **Data import / export** | Partial | Frappe has built-in CSV import. No custom import template or export configuration. | No pre-built import template for bulk citizen profile or service request seeding. | Demo seeding relies entirely on `seed_demo_records.py` patch. | Deferred | No | No | **Low** |
| 18 | **Setup wizard / installation readiness** | Partial | `patches.txt` lists three idempotent patches. No `after_install` hook. | `after_install` hook in `hooks.py` is absent. On fresh install, patches must be run manually via `bench migrate`. | First-time install may confuse evaluators if the demo environment is not pre-seeded. | 11B-8 | Yes | No | **Medium** |
| 19 | **File attachment governance** | Partial | `nilegov_evidence_document` has a `file` Link field. No Frappe File Type restriction, no max size config, no attachment folder policy. | Any file type can be attached. No governance policy enforced at Frappe level. | Minor for prototype. Would be critical for production. | Deferred | No | No | **Low** |
| 20 | **Runtime smoke tests** | Pending | Integration test exists at `tests/integration/test_pass2_demo_flow.py` but uses MagicMock (no live Frappe). | No actual Frappe runtime test has been run. All 525 tests pass in-memory only. | Cannot claim runtime correctness without a deployed bench. | Runtime-only | No | Yes | **Critical (deferred)** |

---

## 3. Role Name Conflict — Detail

This is the **highest-severity** finding and must be resolved in Pass 11B-2.

| Source | Role Names Used |
|---|---|
| `hooks.py` fixtures | `Citizen`, `Service Desk Officer`, `Supervisor`, `Registry Liaison Officer`, `MDA Leadership`, `MDA Administrator`, `System Administrator` |
| `seed_roles.py` | Same 7 old names |
| `interfaces/permissions.py` | Same 7 old names (`Citizen`, `Service Desk Officer`, `Supervisor`, `MDA Leadership`, `MDA Administrator`) |
| `workspace.json` roles array | `Service Desk Officer`, `Supervisor`, `System Administrator` |
| All 15 DocType JSON `permissions` arrays | `System Manager` only |
| `application/permission_policy.py` | 8 NileGov-prefixed roles |
| `test_permission_hardening.py` (Pass 11A) | 8 NileGov-prefixed roles |
| `test_doctype_schemas.py` | Asserts old role names are in `hooks.py` (will continue to pass) |

**Decision required before coding Pass 11B-2:**
Three options exist:

- **Option A (Recommended):** Standardise on 8 NileGov-prefixed roles everywhere. Update `hooks.py`, `seed_roles.py`, `interfaces/permissions.py`, all DocType JSON permission rows, `workspace.json`, and `seed_demo_records.py`. Update `test_doctype_schemas.py` role assertions. Old roles become aliases in `seed_roles.py` (seeded as well for backward compat).
- **Option B:** Keep old roles for Frappe layer; keep NileGov-prefixed roles only in `permission_policy.py` (application/domain). Accept the inconsistency and document it.
- **Option C:** Delete `permission_policy.py` NileGov-prefixed roles and adopt old role names everywhere. (Not recommended — degrades domain layer design.)

> **Option A is recommended.** It resolves the inconsistency completely and makes the system coherent. It is the only option that survives an evaluator who reads both the code and the running system.

---

## 4. Recommended Pass 11B Split

### Pass 11B-1 — Reporting Snapshot DocType
**Objective:** Create the missing `NileGov Reporting Snapshot` Frappe DocType so M&E data is visible in the Desk.

**Files to create:**
- `nilegov_stack/doctype/nilegov_reporting_snapshot/nilegov_reporting_snapshot.json`
- `nilegov_stack/doctype/nilegov_reporting_snapshot/nilegov_reporting_snapshot.py`
- `nilegov_stack/doctype/nilegov_reporting_snapshot/nilegov_reporting_snapshot.js`
- `nilegov_stack/doctype/nilegov_reporting_snapshot/__init__.py`

**Files to modify:**
- `tests/unit/test_doctype_schemas.py` — add `nilegov_reporting_snapshot` to `EXPECTED_DOCTYPES`

**Files not to touch:**
- `.env`, `hooks.py` (role fix is Pass 11B-2), domain layer, existing tests

**Tests to add:**
- Schema test for Reporting Snapshot fields (snapshot_id, snapshot_name, period_start, period_end, total_requests, disclaimer, etc.)
- Schema test for disclaimer field presence

**Runtime validation required:** Yes — must verify DocType loads in Frappe Desk

**Risk level:** Critical

---

### Pass 11B-2 — Role Fixtures and Permission Rows
**Objective:** Align all role references to 8 NileGov-prefixed roles. Add full permission rows to all 15 DocType JSON files.

**Files to create:**
- None (modifying existing)

**Files to modify:**
- `hooks.py` — update fixtures role list to NileGov-prefixed names
- `patches/seed_roles.py` — update to seed NileGov-prefixed roles (keep old names as aliases for backward compat)
- `patches/seed_demo_records.py` — update `add_roles()` calls to use new role names
- `interfaces/permissions.py` — update all role name string checks
- `nilegov_stack/workspace/nilegov_case_operations/nilegov_case_operations.json` — update `roles` array
- All 15 DocType JSON files — add permission rows for each operational role with correct read/write/create/delete flags per role duty separation model
- `tests/unit/test_doctype_schemas.py` — update `test_role_fixtures_and_patches_exist` assertions

**Files not to touch:**
- `.env`, domain layer, `application/permission_policy.py` (already correct)

**Tests to add:**
- Test that all DocType JSON files declare at least 5 permission rows
- Test that no DocType has `Guest` access
- Test that `NileGov M&E Viewer` has read-only access to Reporting Snapshot DocType
- Test that `NileGov System Auditor` has read access to Audit Event

**Runtime validation required:** Yes — role-based access must be verified in a live bench

**Risk level:** Critical

---

### Pass 11B-3 — Workspace Navigation, Search Fields, Metadata
**Objective:** Enrich the workspace with a full navigation links block, correct role list, and add `search_fields` to key DocTypes.

**Files to create:**
- None

**Files to modify:**
- `nilegov_stack/workspace/nilegov_case_operations/nilegov_case_operations.json` — add `links` block (links to all 15+ DocTypes in logical groups), update `roles` array, add NileGov-prefixed shortcuts
- `nilegov_stack/doctype/nilegov_service_request/nilegov_service_request.json` — add `search_fields` (nin, reference_no, citizen_full_name)
- `nilegov_stack/doctype/nilegov_citizen_profile/nilegov_citizen_profile.json` — add `search_fields` (nin, full_name, phone)

**Files not to touch:**
- `.env`, domain layer, all test files (no new tests needed for workspace content)

**Tests to add:**
- Schema test that `search_fields` is declared in service_request and citizen_profile JSON

**Runtime validation required:** Yes — workspace must load and navigate correctly in a live bench

**Risk level:** High

---

### Pass 11B-4 — JavaScript Form Scripts and Custom Buttons
**Objective:** Add `.js` form scripts for all 14 DocTypes currently lacking them. Wire up all existing whitelisted Python methods to UI buttons.

**Files to create:**
- `nilegov_case_note/nilegov_case_note.js`
- `nilegov_citizen_profile/nilegov_citizen_profile.js`
- `nilegov_evidence_document/nilegov_evidence_document.js`
- `nilegov_payment_record/nilegov_payment_record.js`
- `nilegov_consent_record/nilegov_consent_record.js`
- `nilegov_sla_rule/nilegov_sla_rule.js`
- `nilegov_sla_event/nilegov_sla_event.js`
- `nilegov_escalation_record/nilegov_escalation_record.js`
- `nilegov_citizen_notification/nilegov_citizen_notification.js`
- `nilegov_audit_event/nilegov_audit_event.js`
- `nilegov_service_catalogue/nilegov_service_catalogue.js`
- `nilegov_service_type/nilegov_service_type.js`
- `nilegov_integration_simulation_log/nilegov_integration_simulation_log.js`
- `nilegov_simulated_identity_verification/nilegov_simulated_identity_verification.js`

**Files to modify:**
- `nilegov_service_request/nilegov_service_request.js` — add remaining custom buttons (Assign Officer, Escalate Case, Resolve Escalation, Supervisor Review, Return to Officer, Evaluate SLA)

**Files not to touch:**
- `.env`, domain layer, Python controllers

**Tests to add:**
- Architecture test: all DocTypes have a `.js` file present on disk
- Test that service_request.js references all major whitelisted methods

**Runtime validation required:** Yes — buttons must appear and invoke correctly in a live bench

**Risk level:** High

---

### Pass 11B-5 — Query Reports and Dashboard Charts
**Objective:** Create Frappe Query Reports for the 5 most important views. Add number cards to the workspace.

**Files to create:**
- `nilegov_stack/report/nilegov_case_status_summary/nilegov_case_status_summary.json`
- `nilegov_stack/report/nilegov_case_status_summary/nilegov_case_status_summary.py`
- `nilegov_stack/report/nilegov_sla_compliance/nilegov_sla_compliance.json`
- `nilegov_stack/report/nilegov_sla_compliance/nilegov_sla_compliance.py`
- `nilegov_stack/report/nilegov_officer_workload/nilegov_officer_workload.json`
- `nilegov_stack/report/nilegov_officer_workload/nilegov_officer_workload.py`
- `nilegov_stack/report/nilegov_pending_payments/nilegov_pending_payments.json`
- `nilegov_stack/report/nilegov_pending_payments/nilegov_pending_payments.py`
- `nilegov_stack/report/nilegov_me_snapshot/nilegov_me_snapshot.json`
- `nilegov_stack/report/nilegov_me_snapshot/nilegov_me_snapshot.py`

**Files to modify:**
- `nilegov_stack/workspace/nilegov_case_operations/nilegov_case_operations.json` — add `charts` block with number cards

**Files not to touch:**
- `.env`, domain layer, DocType JSON files

**Tests to add:**
- Architecture test: all report directories have `.json` and `.py` files
- Test that report JSON files are valid Frappe report format

**Runtime validation required:** Yes — reports must render in Frappe Desk

**Risk level:** High

---

### Pass 11B-6 — Print Formats, Notification Config, Assignment Rules
**Objective:** Add print formats for citizen-facing documents. Configure notification scaffolding. Add basic assignment rule scaffolding.

**Files to create:**
- `nilegov_stack/print_format/nilegov_service_request_acknowledgement/nilegov_service_request_acknowledgement.json`
- `nilegov_stack/print_format/nilegov_payment_receipt/nilegov_payment_receipt.json`
- `nilegov_stack/print_format/nilegov_citizen_notification_summary/nilegov_notification_summary.json`

**Files to modify:**
- None (new print formats are standalone JSON)

**Files not to touch:**
- `.env`, domain layer, DocType JSON files, tests

**Tests to add:**
- Architecture test: print format directories exist and have valid JSON

**Runtime validation required:** Yes — print formats must render in Frappe Desk PDF preview

**Risk level:** Medium

---

### Pass 11B-7 — Citizen Web Form and REST API Scaffolding
**Objective:** Add a Frappe Web Form for citizen intake. Populate `interfaces/frappe/api/__init__.py` with a minimal REST endpoint scaffold.

**Files to create:**
- `nilegov_stack/web_form/nilegov_citizen_intake/nilegov_citizen_intake.json`
- `nilegov_stack/web_form/nilegov_citizen_intake/nilegov_citizen_intake.py`

**Files to modify:**
- `interfaces/frappe/api/__init__.py` — add 3–5 `@frappe.whitelist()` functions (get_service_request_status, list_citizen_requests, submit_citizen_request)

**Files not to touch:**
- `.env`, domain layer, DocType JSON, controller files

**Tests to add:**
- Test that `api/__init__.py` exposes the expected function names
- Test that web_form JSON is valid and references correct DocType

**Runtime validation required:** Yes — web form must be accessible at `/nilegov-citizen-intake` portal URL

**Risk level:** High

---

### Pass 11B-8 — Installation Hooks, After-Install, and Final Audit
**Objective:** Add `after_install` hook so demo data seeds automatically on `bench migrate`. Final schema audit pass.

**Files to create:**
- `nilegov_stack/install.py` — exposes `after_install()` that calls the three patch `execute()` functions

**Files to modify:**
- `hooks.py` — add `after_install = "nilegov_stack.install.after_install"`

**Files not to touch:**
- `.env`, domain layer

**Tests to add:**
- Test that `install.py` exists and exposes `after_install`
- Test that `hooks.py` declares `after_install`

**Documentation to update:**
- `walkthrough.md` — final Pass 11B summary
- `README.md` — update installation steps

**Runtime validation required:** No — install hook is verified by static test; live test deferred to Hetzner bench

**Risk level:** Medium

---

## 5. Files That Must Not Be Touched in Any Sub-pass

- `.env`
- Any file in `.venv/`
- `domain/` Python files (pure domain model — no Frappe imports)
- `application/` Python files (use cases — no Frappe imports)
- Any existing passing test unless specifically listed as a modify target

---

## 6. Runtime Validation Items — Permanently Deferred

The following require a live Frappe/ERPNext bench (Hetzner or equivalent):

- Role-based login and DocType access verification
- Form script button click testing
- Report rendering and data accuracy
- Dashboard chart live data refresh
- Web Form citizen submission end-to-end
- Print format PDF output generation
- `after_install` seeding on fresh install
- SLA timer scheduling
- Notification email delivery

---

## 7. Recommended First Implementation Pass

**Start with Pass 11B-2 (Role Fixtures and Permission Rows).**

Rationale: It is the root cause of every other Frappe-level gap. Without correct roles and permission rows, even a correctly installed system will deny access to every evaluator. Pass 11B-1 (Reporting Snapshot DocType) should follow immediately after, then 11B-4 (JS Form Scripts) as the third priority.

---

## 8. Approval Required

This plan requires user approval before any file is modified.
