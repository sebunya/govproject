# Pass 11B Task Checklist
# NileGov Stack — Frappe Native Completeness

## Status: 11B-2 COMPLETE — Next: 11B-1 (Reporting Snapshot DocType)

---

## Pass 11B-1: Reporting Snapshot DocType
- [ ] Create `nilegov_reporting_snapshot.json` DocType schema
- [ ] Create `nilegov_reporting_snapshot.py` controller
- [ ] Create `nilegov_reporting_snapshot.js` form script
- [ ] Create `__init__.py`
- [ ] Update `test_doctype_schemas.py` EXPECTED_DOCTYPES
- [ ] Run full test suite (must remain 620+/all green)
- [ ] Commit

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

## Pass 11B-6: Print Formats, Notification Config, Assignment Rules
- [ ] Create nilegov_service_request_acknowledgement print format JSON
- [ ] Create nilegov_payment_receipt print format JSON
- [ ] Create nilegov_citizen_notification_summary print format JSON
- [ ] Add architecture test: print format directories exist
- [ ] Run full test suite
- [ ] Commit

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
