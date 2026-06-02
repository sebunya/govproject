# Pass 11B Task Checklist
# NileGov Stack — Frappe Native Completeness

## Status: 11B-8D COMPLETE ✅

## Pass 11B-8D: Final Frappe-Native Evidence Manifest ✅ COMPLETE
- [x] Create final evidence manifest `docs/submission/14_frappe_native_evidence_manifest.md`
- [x] Cover all 11 required sections including Capability-to-Artifact Matrix, Asset Register, and Test Coverage
- [x] Update static architecture verification test `test_submission_manifest.py`
- [x] Update runtime validation checklist `docs/submission/08_runtime_validation_checklist.md`
- [x] Update evidence index `docs/submission/13_evidence_index.md`
- [x] Verify all 1401 tests pass successfully
- [x] Ensure dotenv configuration remains untracked and compile checks pass

## Pass 11B-8C: Demo Seed Data, Migration Readiness and Runtime Smoke Checklist ✅ COMPLETE
- [x] Create seed data safety architecture tests `test_seed_data_safety.py`
- [x] Create patch migration readiness architecture tests `test_patch_migration_readiness.py`
- [x] Add "Fresh Bench Runtime Smoke Checklist" to `docs/submission/08_runtime_validation_checklist.md`
- [x] Run unit tests to verify all tests pass (1396/1396 passed)
- [x] Update documentation: `13_evidence_index.md`, `walkthrough.md`
- [x] Run compilation check and final verification command checks

## Pass 11B-8B: Safe Install Hook and Setup Readiness ✅ COMPLETE
- [x] Create install module `install.py`
- [x] Register `after_install` in `hooks.py`
- [x] Create static architecture test suite `tests/architecture/test_install_readiness.py`
- [x] Create unit test suite `tests/unit/test_install_readiness.py`
- [x] Run unit tests to verify all tests pass (1388/1388 passed)
- [x] Update documentation: `13_evidence_index.md`, `08_runtime_validation_checklist.md`, `walkthrough.md`
- [x] Run compilation check and final verification command checks

## Pass 11B-8A: Installation, Fixtures, Migration and Runtime Readiness Audit ✅ COMPLETE
- [x] Run Git status, log, and untracked checks
- [x] Inspect hooks.py, patches, modules.txt, and fixture lists
- [x] Assess install hook risks for seeding data, roles, and configuration
- [x] Build fixture readiness master audit table
- [x] Recommend the Pass 11B-8 split and next steps scope

- [x] Create pure redaction helper module `application/redaction.py`
- [x] Add status lookup API endpoint `get_redacted_case_status_preview` to `public_readiness.py`
- [x] Export status lookup API endpoint in `interfaces/frappe/api/__init__.py`
- [x] Create unit test suite `tests/unit/test_redaction.py`
- [x] Update static and unit test assertions in `test_public_api_scaffold.py` and `test_public_api_scaffold_outputs.py`
- [x] Run unit tests to verify all tests pass (1376/1376 passed)
- [x] Update documentation: `13_evidence_index.md`, `08_runtime_validation_checklist.md`, `walkthrough.md`
- [x] Run compilation check and final verification command checks

## Pass 11B-7C: REST API Envelope Endpoint Scaffolding ✅ COMPLETE
- [x] Create `interfaces/frappe/api/public_readiness.py`
- [x] Implement the 6 required read-only whitelisted API endpoints
- [x] Export endpoints in `interfaces/frappe/api/__init__.py`
- [x] Create static architecture test suite `test_public_api_scaffold.py`
- [x] Create unit test suite `test_public_api_scaffold_outputs.py`
- [x] Run unit tests with pytest to verify all tests pass (1367/1367 passed)
- [x] Update documentation: `13_evidence_index.md`, `08_runtime_validation_checklist.md`, `walkthrough.md`
- [x] Run compilation check and final verification command checks

## Pass 11B-7B: Citizen Web Form Metadata Scaffold ✅ COMPLETE
- [x] Create 3 standard Web Form JSON files under `web_form/`
- [x] Enforce unpublished status (`published=0`) and login requirements (`login_required=1`)
- [x] Include mandatory prototype NIRA disclaimers and field warnings
- [x] Add `Web Form` to fixtures in `hooks.py`
- [x] Create static architecture test suite `test_web_form_definitions.py`
- [x] Run unit tests with pytest to verify all tests pass (1354/1354 passed)
- [x] Update documentation: `13_evidence_index.md`, `08_runtime_validation_checklist.md`, `walkthrough.md`
- [x] Run compilation check and final verification command checks

## Pass 11B-7A: Web Form, Public Status Lookup and REST API Surface Audit ✅ COMPLETE
- [x] Audit existing `web_form/`, `www/`, and `interfaces/frappe/api/` directories
- [x] Classify intake, lookup, and payment fields for public safety and redaction
- [x] Design proposed scaffolding split and redact constraints
- [x] Update implementation_plan.md and task.md planning files

## Pass 11B-6D: Assignment Rules and ToDo Readiness ✅ COMPLETE
- [x] Create 7 standard Assignment Rule JSON files under `assignment_rule/`
- [x] Add `Assignment Rule` to fixtures in `hooks.py`
- [x] Create static architecture test suite `test_assignment_rule_definitions.py`
- [x] Run unit tests with pytest to verify all tests pass (1328/1328 passed)
- [x] Update documentation: `13_evidence_index.md`, `08_runtime_validation_checklist.md`, `walkthrough.md`
- [x] Run compilation check and final verification command checks

## Pass 11B-6C: Simulated Notification Templates ✅ COMPLETE
- [x] Create 8 standard Notification JSON files under `notification/`
- [x] Add `Notification` to fixtures in `hooks.py`
- [x] Create static architecture test suite `test_notification_definitions.py`
- [x] Run unit tests with pytest to verify all tests pass (1284/1284 passed)
- [x] Update documentation: `13_evidence_index.md`, `08_runtime_validation_checklist.md`, `walkthrough.md`
- [x] Run compilation check and final verification command checks


## Pass 11B-1: Reporting Snapshot DocType ✅ COMPLETE
- [x] Create `nilegov_reporting_snapshot/` directory
- [x] Create `nilegov_reporting_snapshot.json` — 40-field DocType with NileGov-prefixed permissions
- [x] Create `nilegov_reporting_snapshot.py` controller (validates snapshot_name, disclaimer, no live-gov claims)
- [x] Create `__init__.py`
- [x] Update `test_doctype_schemas.py` EXPECTED_DOCTYPES (16 DocTypes total)
- [x] Update `test_role_alignment.py` ALL_DOCTYPES (16 DocTypes total)
- [x] Create `tests/unit/test_reporting_snapshot_doctype.py` (41 new tests, 14 classes)
- [x] Add workspace shortcut for M&E Reporting Snapshots
- [x] Run full test suite: **668/668 passed** (+48 vs Pass 11B-2 baseline)
- [x] Compile: **CLEAN**
- [x] Commit + push to main


## Pass 11B-2: Role Fixtures and Permission Rows ✅ COMPLETE
- [x] Update `hooks.py` fixtures list → NileGov-prefixed roles
- [x] Update `patches/seed_roles.py` → NileGov-prefixed roles (old names as legacy aliases)
- [x] Update `patches/seed_demo_records.py` → new role names
- [x] Update `interfaces/permissions.py` → NileGov-prefixed roles + canonical constants
- [x] Update `workspace.json` roles array → canonical roles
- [x] Update all 15 DocType JSON permission rows (4–9 NileGov roles each)
- [x] Update `test_doctype_schemas.py` role assertions
- [x] Create `tests/permissions/test_role_alignment.py` (94+ new tests)
- [x] Run full test suite: **620/620 passed**
- [x] Compile: **CLEAN**
- [x] Commit + push to main

- [ ] Update `hooks.py` fixtures list → NileGov-prefixed roles
- [ ] Update `patches/seed_roles.py` → NileGov-prefixed roles
- [ ] Update `patches/seed_demo_records.py` → new role names
- [ ] Update `interfaces/permissions.py` → NileGov-prefixed roles
- [ ] Update `workspace.json` roles array
- [ ] Update all 15 DocType JSON permission rows (5–8 roles each)
- [ ] Update `test_doctype_schemas.py` role assertions
- [ ] Run full test suite (must remain 525+/all green)
- [ ] Commit

## Pass 11B-3: Workspace Navigation and Search Fields
- [ ] Add links block to `nilegov_case_operations.json`
- [ ] Add `search_fields` to service_request JSON
- [ ] Add `search_fields` to citizen_profile JSON
- [ ] Run full test suite
- [ ] Commit

## Pass 11B-4: JavaScript Form Scripts and Custom Buttons
- [ ] Create JS for nilegov_case_note
- [ ] Create JS for nilegov_citizen_profile
- [ ] Create JS for nilegov_evidence_document
- [ ] Create JS for nilegov_payment_record
- [ ] Create JS for nilegov_consent_record
- [ ] Create JS for nilegov_sla_rule
- [ ] Create JS for nilegov_sla_event
- [ ] Create JS for nilegov_escalation_record
- [ ] Create JS for nilegov_citizen_notification
- [ ] Create JS for nilegov_audit_event
- [ ] Create JS for nilegov_service_catalogue
- [ ] Create JS for nilegov_service_type
- [ ] Create JS for nilegov_integration_simulation_log
- [ ] Create JS for nilegov_simulated_identity_verification
- [ ] Extend nilegov_service_request.js with all 8 remaining custom buttons
- [ ] Add architecture test: all DocTypes have .js
- [ ] Run full test suite
- [ ] Commit

## Pass 11B-5: Query Reports and Dashboard Charts
- [ ] Create nilegov_case_status_summary report (.json + .py)
- [ ] Create nilegov_sla_compliance report (.json + .py)
- [ ] Create nilegov_officer_workload report (.json + .py)
- [ ] Create nilegov_pending_payments report (.json + .py)
- [ ] Create nilegov_me_snapshot report (.json + .py)
- [ ] Add number cards to workspace charts block
- [ ] Add architecture test: all report directories have .json and .py
- [ ] Run full test suite
- [ ] Commit

## Pass 11B-6B: Print Formats ✅ COMPLETE
- [x] Create nilegov_service_request_acknowledgement print format JSON
- [x] Create nilegov_lost_nid_case_summary print format JSON
- [x] Create nilegov_simulated_payment_receipt print format JSON
- [x] Create nilegov_evidence_review_sheet print format JSON
- [x] Create nilegov_sla_escalation_memo print format JSON
- [x] Create nilegov_case_closure_certificate print format JSON
- [x] Create nilegov_m_e_summary_brief print format JSON
- [x] Add architecture test for print formats
- [x] Run full test suite: 1226/1226 passed
- [x] Commit


## Pass 11B-7: Citizen Web Form and REST API Scaffolding
- [ ] Create nilegov_citizen_intake web form (.json + .py)
- [ ] Populate interfaces/frappe/api/__init__.py with 3–5 whitelisted endpoints
- [ ] Add test: api/__init__.py exposes expected functions
- [ ] Add test: web_form JSON is valid
- [ ] Run full test suite
- [ ] Commit

## Pass 11B-8: Installation Hooks and Final Audit
- [ ] Create nilegov_stack/install.py with after_install()
- [ ] Add after_install hook to hooks.py
- [ ] Add test: install.py exists and exposes after_install
- [ ] Update walkthrough.md with Pass 11B summary
- [ ] Update README.md installation steps
- [ ] Run full test suite
- [ ] Final git push to main

## Pass 11B-4A: Service Request JS Action Wiring ✅ COMPLETE
- [x] Audit existing JS (2 buttons, no banner, no error handling)
- [x] Audit Python whitelist (10 methods confirmed)
- [x] Upgrade nilegov_service_request.js — prototype banner, status indicator
- [x] Wire all 10 whitelisted methods into 3 button groups
- [x] Add confirmation dialogs for all state-changing actions
- [x] Add unified error handling and reload on success
- [x] Create tests/architecture/test_service_request_js_actions.py (38 tests, 14 classes)
- [x] Run full test suite: 863/863 passed
- [x] Compile: CLEAN
- [x] Commit + push to main

## Pass 11B-4B: Supporting DocType JS Helpers ✅ COMPLETE
- [x] Audit 4 DocTypes (0 existing JS, 0 whitelisted methods each)
- [x] Created nilegov_evidence_document.js — prototype banner, status indicator, navigation
- [x] Created nilegov_payment_record.js — sandbox banner, payment/verify status, simulated amount
- [x] Created nilegov_escalation_record.js — escalation banner, status, supervisor action pointer
- [x] Created nilegov_reporting_snapshot.js — M&E banner, metric headline, disclaimer reinforcement
- [x] Created tests/architecture/test_supporting_doctype_js_helpers.py (77 tests, 12 classes)
- [x] Run full test suite: 941/941 passed
- [x] Compile: CLEAN
- [x] Commit + push to main

## Pass 11B-5-0: Frappe Reporting and Dashboard Audit ✅ COMPLETE
- [x] git status: clean (adbc52c)
- [x] .env: untracked
- [x] Checked report/, dashboard_chart/, number_card/, dashboard/ — all absent
- [x] Checked hooks.py — no report or dashboard fixtures
- [x] Audited 9 DocTypes for field existence
- [x] Identified 2 field corrections (service_catalogue→service_type, resolved_at→completed_at)
- [x] Assessed all 9 target reports → all Report Builder JSON, no blockers
- [x] Assessed 9 number cards + 8 charts → all safe to implement
- [x] Wrote implementation_plan.md
- [x] 11B-5A: Implement 9 reports + 9 number cards + 8 charts + 1 dashboard (36 files)
- [x] 11B-5B: Workspace report shortcuts, docs update

