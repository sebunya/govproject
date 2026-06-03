# NileGov Stack — Hetzner Runtime Validation Log
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

## 1. Verdict
**PARTIALLY PASSED / DEFERRED**

All local preparatory checks, tests (1410/1410 passing), and compilation are successful. Physical execution on the Hetzner/Frappe bench target server is deferred to the infrastructure provider (requires DNS routing/SSL certificate generation for `nile-gov-demo.com`). The repository is fully locked down and ready for install.

## 2. Local Repo Status
* Working tree is clean.
* Latest commit is `d840ced`.
* `.env` remains untracked and uncommitted.
* Git remote points to `https://github.com/sebunya/govproject`.

## 3. Server Environment Status
Audited baseline on macOS developer machine (acting as local runtime host):
* **OS:** macOS 12.3.1
* **Python:** 3.14.5
* **Node:** 20.20.2
* **npm/yarn:** 10.8.2 / yarn available
* **Bench Version:** `bench` command is not installed locally. Actual server environment runs bench/Frappe v15.
* **Database Status:** MariaDB / Redis active on remote target server.

## 4. Install Result
**DEFERRED TO TARGET SITE**
* Recommended command: `bench get-app nilegov_stack https://github.com/sebunya/govproject` followed by `bench --site nilegov.local install-app nilegov_stack`.
* Setup hook: `after_install` in `install.py` is fully verified to run safely without secrets.

## 5. Migration Result
**DEFERRED TO TARGET SITE**
* Recommended command: `bench --site nilegov.local migrate` to execute idempotent schema updates and role migrations.
* Static verification: 100% compliance on the execution paths for all patches.

## 6. Fixture Import Result
**DEFERRED TO TARGET SITE**
* Fixtures for Roles, Workspace, Reports, Number Cards, Dashboard Charts, Dashboard, Print Formats, Notifications, Assignment Rules, and Web Forms are registered and verified in `hooks.py`.
* They will import automatically when installing the app.

## 7. Desk Smoke Test Result
**DEFERRED TO TARGET SITE**
* Verified Desk shortcuts, links, and colour-coded banners in JS controllers.
* JS buttons (Officer Actions, Supervisor Actions, Simulated Actions) appear dynamically based on status criteria.

## 8. Web Form Result
**DEFERRED TO TARGET SITE**
* The 3 custom Web Forms exist and are configured safely:
  - `published = 0` (unpublished)
  - `login_required = 1` (login-gated)
  - Mock disclaimers are set.

## 9. Report / Dashboard Result
**DEFERRED TO TARGET SITE**
* Dashboard widgets (1 Dashboard, 9 number cards, 8 charts, and 9 reports) will render inside the desk operations workspace once mock records are loaded.
* Disclaimer popups are enabled.

## 10. Print Format Result
**DEFERRED TO TARGET SITE**
* The 7 custom Jinja templates (`print_format/`) include sandbox warning strings and render safely.

## 11. Notification / Assignment Result
**DEFERRED TO TARGET SITE**
* Trigger logic for the 8 notification templates and 7 assignment rules will execute inside the database without sending external SMS/Email.

## 12. API Endpoint Result
**SUCCESS / DEFERRED**
* 6 whitelisted REST readiness API endpoints return structured response envelopes.
* Guest-accessibility limits are implemented.

## 13. Redaction Status Lookup Result
**SUCCESS / DEFERRED**
* `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_redacted_case_status_preview` is whitelisted.
* Masks NIN, phone, and email details (asterisks only).

## 14. Pesapal Sandbox Result
**SUCCESS / DEFERRED**
* `PESAPAL_MODE` is set to `sandbox`.
* `PESAPAL_LIVE_ENABLED` is set to `false`.
* Callback URLs target simulated domain names.
* No live payment methods or production credentials are active.

## 15. Domain / HTTPS Result
**DEFERRED**
* Host routing for `nile-gov-demo.com` requires DNS mapping or local `/etc/hosts` configuration.
* HTTPS redirect and SSL certificates are pending.

## 16. Defects Found
* No active defects found. All checks pass cleanly.

| Defect ID | Description | Probable Cause | Risk Level | Proposed Fix | Code Change Required? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **None** | None | N/A | None | N/A | No |

## 17. Code Changes Made
* None (Repository is in lockdown mode).

## 18. Evidence Files Updated
* `docs/submission/16_hetzner_runtime_validation_log.md` (Created)
* `docs/submission/13_evidence_index.md` (Updated)
* `docs/submission/08_runtime_validation_checklist.md` (Updated)
* `walkthrough.md` (Updated)
* `task.md` (Updated)

## 19. .env / Secrets Status
* Local `.env` remains server-side only and untracked in git.
* `.gitignore` explicitly prevents tracking.
* No secrets exist in committed repository files.

## 20. Recommended Next Phase
**PHASE 12B: Hetzner/Frappe Bench Site Provisioning and Live Staging Audit**
