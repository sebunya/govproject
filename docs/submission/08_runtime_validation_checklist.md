# NileGov Stack Runtime Validation Checklist

This checklist tracks the deployment, setup, database migration, and browser testing steps required once a working Docker/Linux container host is available.

---

## 1. Environment Requirements & Diagnostics

Before running the stack, confirm the presence of a working Docker host by running:
```bash
# Verify Docker version (must return Client and Server version info)
docker version

# Verify container lists (should execute without socket connection errors)
docker ps

# Verify Compose CLI
docker compose version
```

* **Recommended Host:** Clean Linux VPS (Ubuntu 22.04 LTS or Rocky Linux 9) with Docker and Docker Compose installed.
* **Known Blocker on Current Host:** The macOS host lacks `qemu-img`, which prevents Colima daemon startup. Homebrew installation is blocked on source dependency compilations.

---

## 2. Docker Compose Deployment Commands

From the root directory of the cloned repository, execute:
```bash
# 1. Boot the containers in detached mode
docker compose -f deployment/docker-compose.yml up -d

# 2. Verify all containers are running and healthy
docker compose -f deployment/docker-compose.yml ps
```

| Container Node | Required Status | Purpose | Verified |
| :--- | :--- | :--- | :--- |
| `backend` | Running | Gunicorn Web server & Bench | [ ] |
| `db` | Running | MariaDB database engine | [ ] |
| `redis-cache` | Running | Cache storage | [ ] |
| `redis-queue` | Running | Queue manager | [ ] |

---

## 3. Site Provisioning & Database Setup

Initialize the bench site `nilegov.local` by running:
```bash
# 1. Create a new site (uses passwords specified in deployment env)
docker compose -f deployment/docker-compose.yml exec backend bench new-site nilegov.local --mariadb-root-password admin --admin-password admin --no-mariadb-socket

# 2. Install the custom NileGov Stack application
docker compose -f deployment/docker-compose.yml exec backend bench --site nilegov.local install-app nilegov_stack

# 3. Run migrations to trigger the custom seeding patches
docker compose -f deployment/docker-compose.yml exec backend bench --site nilegov.local migrate
```

---

## 4. Seed Data Verification Checklist

### Fictional Service Requests
- [ ] **Submitted:** Record `req_pass3_001` (NIN `CF900000000000`, Name *Demo Citizen A*, linked to `CP-001`, SLA state *Within SLA*).
- [ ] **Under Review:** Record `req_pass3_002` (NIN `CF900000000001`, Name *Demo Citizen B*, linked to `CP-002`, SLA state *At Risk*, at risk flag active).
- [ ] **Information Required:** Record `req_pass3_003` (NIN `CF900000000002`, Name *Demo Citizen C*, linked to `CP-003`, SLA state *Overdue*, overdue flag active, escalation state *Not Escalated*).
- [ ] **Payment Pending:** Record `req_pass3_004` (NIN `None` / empty placeholder NIN `CF999999999999`, Name *Demo Citizen D*, linked to `CP-004`, SLA state *Within SLA*).
- [ ] **Payment Verified:** Record `req_pass3_005` (NIN `CF900000000004`, Name *Demo Citizen E*, linked to `CP-005`, SLA state *Overdue*, overdue flag active, escalation state *Escalation Recommended*).
- [ ] **Approved:** Record `req_pass3_006` (NIN `CF900000000005`, Name *Demo Citizen F*, linked to `CP-006`, SLA state *Overdue*, overdue flag active, escalation state *Escalated* to *supervisor_demo*, queue *Supervisor Review Queue*).
- [ ] **Ready for Collection:** Record `req_pass3_007` (NIN `CF900000000006`, Name *Demo Citizen G*, linked to `CP-007`, SLA state *Within SLA*).
- [ ] **Closed:** Record `req_pass3_008` (NIN `CF900000000007`, Name *Demo Citizen H*, containing approved closure notes, linked to `CP-008`, SLA state *Met*).
- [ ] **CP-001 (req_pass3_001) Assignment:** Check that assignment status is `Unassigned`, and queue is `National ID Replacement Desk`.
- [ ] **CP-002 (req_pass3_002) Assignment:** Check that assigned officer is `officer_demo`, status is `Assigned`, and queue is `National ID Replacement Desk`.
- [ ] **CP-003 (req_pass3_003) Assignment:** Check that assigned officer is `officer_review`, department is `Verification Desk`, status is `Assigned`, and queue is `Verification Desk`.
- [ ] **CP-004 (req_pass3_004) Assignment:** Check that department is `National ID Replacement Desk`, officer is empty, status is `Unassigned`.
- [ ] **CP-005 (req_pass3_005) Assignment:** Check that assigned officer is `officer_review`, status is `Reassigned`, and reassignment reason is "Verification workload overflow".
- [ ] **CP-006 (req_pass3_006) Assignment:** Check that assigned supervisor is `supervisor_demo`, status is `Supervisor Review`, queue is `Supervisor Review Queue`, and review flag is active.
- [ ] **CP-007 (req_pass3_007) Assignment:** Check that assigned officer is `officer_demo`, status is `Returned to Officer`.
- [ ] **CP-008 (req_pass3_008) Assignment:** Check that assigned officer is `officer_demo`, status is `Closed`, and queue is `Completed Cases Queue`.

### Fictional Citizen Profiles
- [ ] **CP-001:** Name *Demo Citizen A*, Location *Ntinda, Kampala*, preferred channel *Phone*, status *Active*, NIN *CF900000000000*.
- [ ] **CP-002:** Name *Demo Citizen B*, Location *Bukoto, Kampala* (alternative location check), preferred channel *Email*, status *Active*, NIN *CF900000000001*.
- [ ] **CP-003:** Name *Demo Citizen C*, Location *Ntinda, Kampala*, preferred channel *SMS*, status *Demo Only* (Demo Only status check), NIN *CF900000000002*.
- [ ] **CP-004:** Name *Demo Citizen D*, Location *Ntinda, Kampala*, preferred channel *WhatsApp*, status *Active*, NIN *None* (optional NIN check).

### Fictional Consent Records
- [ ] **Granted Records (CP-001):** Five records (`CON-CP-001-1` through `5`) covering all five required purposes. Ensure purposes like Simulated Identity Verification are `Granted`, and Future MDA Integration is `Pending`.
- [ ] **Withdrawn Record (CP-002):** Record `CON-CP-002-1` for Service Request Processing is status `Withdrawn` with a withdrawal timestamp.
- [ ] **Expired Record (CP-003):** Record `CON-CP-003-1` for Service Request Processing is status `Expired` with an expiry date in the past.

### Fictional Evidence Documents
- [ ] **Police Letter:** Record `EVI-CP001-POL` for `req_pass3_001` (type *Police Letter Placeholder*, status *Submitted*, file *demo-police-letter-placeholder.pdf*).
- [ ] **Affidavit:** Record `EVI-CP001-AFF` for `req_pass3_001` (type *Affidavit Placeholder*, status *Under Review*, file *demo-affidavit-placeholder.pdf*).
- [ ] **Supporting ID:** Record `EVI-CP001-ID` for `req_pass3_001` (type *Supporting ID Placeholder*, status *Accepted*, file *demo-supporting-id-placeholder.pdf*, verified by *officer_demo*).
- [ ] **Payment Receipt:** Record `EVI-CP001-PAY` for `req_pass3_001` (type *Payment Receipt Placeholder*, status *Demo Placeholder*, file *demo-payment-receipt-placeholder.pdf*).
- [ ] **Other Document:** Record `EVI-CP001-OTH` for `req_pass3_001` (type *Other Supporting Document*, status *Requires Replacement*, file *demo-utility-bill-placeholder.pdf*, containing officer notes regarding blurriness).
- [ ] **Rejected Document:** Record `EVI-CP002-REJ` for `req_pass3_002` (type *Other Supporting Document*, status *Rejected*, file *demo-invalid-attachment.pdf*, containing mismatch rejection notes).

### Fictional SLA Rules & Escalation Records
- [ ] **SLA Rule Seeded:** SLA Rule `SLA-LOST-NID` linked to service type `LOST_NATIONAL_ID` (response hours = 4, resolution hours = 48, threshold = 80%, escalation threshold = 2 hours).

### Fictional Citizen Notifications
- [ ] **Request Received (Sent):** Record `NOT-req_pass3_001-REC` (Service Request `req_pass3_001`, Recipient `+256700000001`, Channel `SMS`, Type `Request Received`, Delivery Status `Simulated Sent`, consent checked shows true/active, disclaimer present).
- [ ] **Payment Pending (Queued):** Record `NOT-req_pass3_004-PAY` (Service Request `req_pass3_004`, Recipient `+256700000004`, Channel `WhatsApp`, Type `Payment Pending`, Delivery Status `Queued`).
- [ ] **SLA At Risk (Queued):** Record `NOT-req_pass3_002-RSK` (Service Request `req_pass3_002`, Recipient `demo.citizen.b@example.test`, Channel `Email`, Type `SLA At Risk`, Delivery Status `Queued`).
- [ ] **SLA Overdue (Sent):** Record `NOT-req_pass3_003-OVR` (Service Request `req_pass3_003`, Recipient `+256700000003`, Channel `SMS`, Type `SLA Overdue`, Delivery Status `Simulated Sent`).
- [ ] **Escalation Notification (Sent):** Record `NOT-req_pass3_006-ESC` (Service Request `req_pass3_006`, Recipient `supervisor_demo`, Channel `Email`, Type `Escalated`, Delivery Status `Simulated Sent`).

### Fictional Payment Records
- [ ] **Not Required Payment:** Record `PAY-req_pass3_001` (Service Request `req_pass3_001`, Amount `0.0`, Purpose `Not Applicable`, Channel `Not Applicable`, Status `Not Required`, verification status `Not Applicable`).
- [ ] **Pending Payment:** Record `PAY-req_pass3_004` (Service Request `req_pass3_004`, Amount `50000.0`, Status `Pending`, reconciliation status `Pending Reconciliation`).
- [ ] **Verified Payment (Reconciled):** Record `PAY-req_pass3_005` (Service Request `req_pass3_005`, Amount `50000.0`, Status `Verified`, Transaction Ref `SIM-PAY-NIRA-2026-0005`, verification status `Simulated Verified`, reconciliation status `Reconciled`).
- [ ] **Receipt Generated:** Record `PAY-req_pass3_006` (Service Request `req_pass3_006`, Amount `50000.0`, Status `Verified`, Transaction Ref `SIM-PAY-NIRA-2026-0006`, Receipt Ref `SIM-RECEIPT-2026-0006`, receipt status `Simulated Receipt Generated`).
- [ ] **Failed Payment:** Record `PAY-req_pass3_002` (Service Request `req_pass3_002`, Amount `50000.0`, Status `Failed`, Transaction Ref `SIM-PAY-NIRA-2026-0002-FAIL`, verification status `Simulated Failed`, reconciliation status `Mismatch`).
- [ ] **Requires Review (Consent Missing/Withdrawn):** Record `PAY-req_pass3_003` (Service Request `req_pass3_003`, Amount `50000.0`, Status `Submitted`, Transaction Ref `SIM-PAY-NIRA-2026-0003-REVIEW`, verification status `Requires Review`, reconciliation status `Requires Review`).
- [ ] **Pesapal Sandbox Configuration:** Verify environment variables `PESAPAL_MODE` is sandbox, `PESAPAL_LIVE_ENABLED` is false, URLs point to `nile-gov-demo.com`, and client rejects live requests by default.
- [ ] **Pesapal Token & IPN Registration:** Verify `RegisterPesapalIPN` runs successfully in the sandbox environment.
- [ ] **Pesapal Transaction Status Lookup:** Verify `RefreshPesapalPaymentStatus` maps COMPLETED (1), FAILED (2), and REVERSED (3) status codes correctly, enforcing privacy consent validations.

### Fictional M&E / Reporting Snapshots
- [ ] **Daily Summary Snapshot Seeded:** Verify that snapshot `SNAP-DAILY-SUMMARY` exists, generated by `officer_demo`, with total requests = 9, total services = 3, and status breakdown mapping.
- [ ] **Service Performance Snapshot Seeded:** Verify that snapshot `SNAP-SERVICE-PERFORMANCE` exists, tracking `LOST_NATIONAL_ID` specific metrics.
- [ ] **SLA Backlog Snapshot Seeded:** Verify that snapshot `SNAP-SLA-BACKLOG` exists, compiling overdue, escalated, and at-risk queues.
- [ ] **Payments & Notifications Snapshot Seeded:** Verify that snapshot `SNAP-PAYMENTS-NOTIFICATIONS` exists, tracking payment verification and message delivery summaries.

### Fictional Service Catalogue Templates
- [ ] **Lost National ID Catalogue Item:** Record `SVC-LOST-NID` (Service Code `LOST_NATIONAL_ID`, Category `Identity Services`, Fee Required `1`, Default Fee `50000.0`, Provider `Simulated`, SLA Rule `SLA-LOST-NID`, Department & Queue `National ID Replacement Desk`, Status `Active`).
- [ ] **Citizen Complaint Catalogue Item:** Record `SVC-CITIZEN-COMPLAINT` (Service Code `CITIZEN_COMPLAINT`, Category `Citizen Complaints`, Fee Required `0`, Status `Demo Only`).
- [ ] **Environmental Permit Catalogue Item:** Record `SVC-PERMIT-APPLICATION` (Service Code `ENVIRONMENT_PERMIT`, Category `Permit Applications`, Fee Required `1`, Default Fee `250000.0`, Provider `Pesapal Sandbox Ready`, Status `Inactive`).

---

## 5. Browser Testing & Action Checklist

Access the Desk using standard local credentials (e.g. Username `Administrator`, Password `admin` or using the seeded user `officer_demo`):

- [ ] **Workspace check:** Navigate to `http://nilegov.local:8000/app/nilegov-case-operations`. Confirm the dashboard layout renders and dashboard counters match seeded numbers.
- [ ] **Workspace Reports section check:** Confirm the new `I. Reports and Dashboards` section is visible and contains links to Case Operations Dashboard and all 9 custom report definitions.
- [ ] **Workspace Case Operations Dashboard link check:** Click the link on the workspace and verify it navigates to the dashboard containing 8 charts and 9 number cards.
- [ ] **Workspace Reports links check:** Click each of the 9 report links. Verify they navigate to the corresponding Report Builder views. Confirm that proper disclaimers (e.g. simulated context, sandbox notification warnings) appear onload.
- [ ] **SLA Rules List check:** Navigate to `http://nilegov.local:8000/app/nilegov-sla-rule`. Verify that the rule `SLA-LOST-NID` renders.
- [ ] **Service Catalogue List check:** Navigate to `http://nilegov.local:8000/app/nilegov-service-catalogue`. Confirm that the list renders and shows all 3 seeded templates (`SVC-LOST-NID`, `SVC-CITIZEN-COMPLAINT`, `SVC-PERMIT-APPLICATION`) with correct active statuses.
- [ ] **Service Catalogue detail check:** Open `SVC-LOST-NID` details. Verify that `required_documents` lists all three placeholders, the fee is set to 50000.0, the default provider is `Simulated`, the workflow template is `Replacement Request Workflow`, and the mandatory disclaimer warning is visible.
- [ ] **Citizen Profile List check:** Navigate to `http://nilegov.local:8000/app/nilegov-citizen-profile`. Confirm that the seeded profiles render.
- [ ] **Consent Records List check:** Navigate to `http://nilegov.local:8000/app/nilegov-consent-record`. Verify that the list renders and displays granted, pending, expired, and withdrawn consent flags correctly.
- [ ] **Consent detail verification check:** Open withdrawn consent record `CON-CP-002-1` and verify the status shows Withdrawn.
- [ ] **Evidence List check:** Navigate to `http://nilegov.local:8000/app/nilegov-evidence-document`. Verify that the list renders and shows all 6 seeded evidence documents with their statuses.
- [ ] **Evidence detail verification check:** Open accepted document `EVI-CP001-ID` and verify the status shows Accepted, verified by shows `officer_demo`, and a link to consent record `CON-CP-001-1` is present.
- [ ] **Evidence replacement check:** Open document `EVI-CP001-OTH` and confirm the verification status shows Requires Replacement, and the officer notes display the request for a clear photo.
- [ ] **Officer Workload metrics check:** From dashboard or console check, run `CalculateWorkloadMetrics`. Verify that caseloads show unassigned counts = 2, supervisor count = 1, and workloads map correctly to fictional officer usernames.
- [ ] **SLA State verification check:** Open request `req_pass3_002` and verify `sla_state` shows `At Risk` and `at_risk_flag` is active. Open request `req_pass3_003` and verify `sla_state` shows `Overdue` and `overdue_flag` is active.
- [ ] **SLA Escalation Recommended check:** Open request `req_pass3_005` and verify `escalation_state` shows `Escalation Recommended`.
- [ ] **SLA Escalation trigger check:** In request `req_pass3_005`, trigger official escalation. Verify escalation state changes to `Escalated`, escalated to supervisor is set, and case moves to supervisor review queue.
- [ ] **Escalation Resolve check:** Open escalated request `req_pass3_006` in Desk, click resolve action. Confirm escalation status changes to `Resolved`, queue resets to `National ID Replacement Desk`, and assignment status updates to `Returned to Officer`.
- [ ] **Reassignment action check:** Open request `req_pass3_002` in Desk, trigger officer reassignment. Confirm status updates to `Reassigned` and reason log is visible.
- [ ] **Supervisor return check:** Open request `req_pass3_006` in Desk, click return action. Confirm status changes to `Returned to Officer` and queue resets to `National ID Replacement Desk`.
- [ ] **Profile detail check:** Open profile `CP-004`. Verify that the profile has no NIN value and does not show validation errors, demonstrating the optional National ID support.
- [ ] **Request detail & Link check:** Open request record `req_pass3_001`. Confirm `citizen_profile` links to `CP-001`.
- [ ] **NIRA check:** Open request record `req_pass3_001`. Expand **Simulated Actions** dropdown and click `Trigger Simulated NIRA Verification`. Confirm success alert shows and NIN Match field updates.
- [ ] **Payment check:** Open pending payment record `req_pass3_004`. Click `Trigger Simulated Payment Verification`. Confirm success alert shows and status moves to approved.
- [ ] **Payment Record List check:** Navigate to `http://nilegov.local:8000/app/nilegov-payment-record`. Confirm the list renders and displays all 8 seeded payment records with correct statuses.
- [ ] **Payment Record detail check:** Open verified record `PAY-req_pass3_005`. Confirm payment status shows Verified, verification status shows Simulated Verified, verified by is `officer_demo`, and the mandatory disclaimer warning is visible.
- [ ] **Reconciliation review check:** Open record `PAY-req_pass3_003`. Verify that status shows Submitted, verification status shows Requires Review, reconciliation status shows Requires Review, and failure reason notes "Consent missing.".
- [ ] **Citizen Notification List check:** Navigate to `http://nilegov.local:8000/app/nilegov-citizen-notification`. Verify that the list renders and shows all 11 seeded notification events.
- [ ] **Notification detail verification check:** Open sent notification `NOT-req_pass3_001-REC`. Verify the status shows Simulated Sent, consent checked shows true/active, and the disclaimer warning is visible.
- [ ] **Standard Notifications list check:** Navigate to `http://nilegov.local:8000/app/notification`. Confirm that the 8 standard NileGov Notification definitions (`NileGov Officer Assigned Alert`, `NileGov Evidence Incomplete Alert`, `NileGov Payment Pending Review Alert`, `NileGov SLA At Risk Alert`, `NileGov SLA Overdue Alert`, `NileGov Escalation Assigned Alert`, `NileGov Case Closed Alert`, `NileGov Simulated Citizen Status Update`) exist and are enabled.
- [ ] **Standard Notification detail verification:** Open `NileGov Simulated Citizen Status Update` and confirm that it triggers on `Save` for `NileGov Citizen Notification` when `doc.delivery_status in ['Queued', 'Simulated Sent']`, targets the recipient role `NileGov Citizen Officer`, and has the required simulated status update disclaimer.
- [ ] **Assignment Rules list check:** Navigate to `http://nilegov.local:8000/app/assignment-rule`. Confirm that all 7 standard NileGov Assignment Rule definitions (`NileGov Submitted Request Queue Assignment`, `NileGov Evidence Review Assignment`, `NileGov Payment Review Assignment`, `NileGov SLA At Risk Supervisor Assignment`, `NileGov SLA Overdue Supervisor Assignment`, `NileGov Escalation Review Assignment`, `NileGov Closure Review Assignment`) exist and are enabled.
- [ ] **Assignment Rule detail verification:** Open `NileGov SLA Overdue Supervisor Assignment`. Verify that it applies to DocType `NileGov Service Request`, triggers when `doc.sla_state == 'Overdue'`, priority is `3`, and maps to role `NileGov SLA Supervisor` (under `assign_to_role`). Confirm that the prototype disclaimer is visible in the description.
- [ ] **Web Forms list check:** Navigate to `http://nilegov.local:8000/app/web-form`. Confirm that the 3 standard NileGov Web Forms (`NileGov Lost National ID Replacement Intake`, `NileGov Evidence Supplement Metadata`, `NileGov Citizen Consent Capture`) exist, are unpublished (`published=0`), and login-required (`login_required=1`).
- [ ] **Web Form detail check:** Open `NileGov Lost National ID Replacement Intake` and verify that the exposed fields are safe and that the mandatory prototype disclaimer warning is shown in the introduction text.
- [ ] **Audit Trail check:** Scroll to the bottom of the form page. Confirm that the timeline logs status changes, SLA assignments, and simulation transaction IDs correctly.
- [ ] **M&E Snapshots List check:** If DocType is deployed, navigate to `http://nilegov.local:8000/app/nilegov-reporting-snapshot`. Confirm that the list renders the 4 seeded snapshots (`SNAP-DAILY-SUMMARY`, `SNAP-SERVICE-PERFORMANCE`, `SNAP-SLA-BACKLOG`, `SNAP-PAYMENTS-NOTIFICATIONS`) with correct statuses and metadata.
- [ ] **M&E Snapshot detail check:** Open snapshot `SNAP-DAILY-SUMMARY` detail page. Confirm the mandatory fictional reporting disclaimer is displayed, start/end period bounds match generation parameters, and dynamic breakdowns (such as requests by queue and status) render without errors.



## API / Interoperability Runtime Validation - Deferred

The API / Interoperability Readiness Foundation is implemented at domain/application/test/documentation level.

Runtime validation remains deferred until the system is deployed on Hetzner or another working Linux/Frappe host with public HTTPS.

Validation still required:

- confirm public API route strategy;
- validate Frappe whitelisted endpoint exposure where appropriate;
- validate response envelope structure in browser/API client;
- validate simulated service request payload output;
- validate simulated identity payload output;
- validate simulated payment payload output;
- validate simulated notification payload output;
- validate reporting snapshot payload output;
- confirm no raw NIN, card data, mobile money PINs or secrets are exposed;
- confirm `.env` remains server-local and untracked;
- confirm Pesapal remains sandbox-only unless live mode is explicitly approved later;
- capture screenshots or API client evidence for evaluator pack.

Do not claim live UGHub, NIRA, URA, NITA-U or MDA integration until formal onboarding and production endpoint validation are complete.

## Roles and Permissions Runtime Validation - Deferred

Validate on Hetzner/Frappe runtime:

- create NileGov role profiles;
- assign test users to each role profile;
- confirm Citizen Officer can create/view assigned service requests;
- confirm Records Officer can review evidence but not verify payments;
- confirm Payments Officer can review payments but not approve evidence;
- confirm SLA Supervisor can review escalations;
- confirm M&E Viewer can view reports but not edit operational records;
- confirm System Auditor can view audit/integration logs but not edit them;
- confirm ordinary users cannot delete audit logs;
- confirm ordinary users cannot delete integration simulation logs;
- confirm no role exposes `.env` secrets;
- confirm no role implies live government registry access.

## Public REST API Scaffold Runtime Validation - Deferred
Validate on Hetzner/Frappe runtime:
- [ ] Verify that `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_service_catalogue_preview` is guest-accessible and returns a valid envelope payload.
- [ ] Verify that `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_lost_nid_intake_schema` is guest-accessible, lists `nin` as optional, and returns the warning description.
- [ ] Verify that `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_evidence_metadata_schema` does not leak verification status, officer notes, or file paths.
- [ ] Verify that `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_consent_capture_schema` does not leak consent timestamps.
- [ ] Verify that `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_prototype_payment_requirement_preview` returns a sandbox disclaimer warning.
- [ ] Verify that `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_interoperability_disclaimer` returns all integration status flags as `False`.
- [ ] Confirm all whitelisted endpoints are strictly read-only and enforce disclaimers without interacting with any production gateways.
- [ ] Verify `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_redacted_case_status_preview` returns a missing reference error envelope if called without a reference.
- [ ] Verify `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_redacted_case_status_preview?reference_number=REQ-2026-9999` returns a fully-redacted status dictionary matching the application level redaction rules.
- [ ] Verify that no internal workflow detail (assigned officer, supervisor comments, raw notes) is ever leaked.

## App Installation Hook Validation - Deferred
Validate on fresh bench install:
- [ ] Confirm `bench install-app nilegov_stack` runs without errors.
- [ ] Confirm after install hook outputs setup logs confirming successful execution.
- [ ] Confirm the 8 canonical roles exist in DB immediately after installation.

## Fresh Bench Runtime Smoke Checklist
Validate sequentially on a freshly provisioned bench:
1. **Fixture Loading Verification:**
   - [ ] Check if the NileGov dashboard, number cards, reports, printing layouts, and notification structures import successfully.
   - [ ] Verify that workspace navigation items render and all 16 DocTypes are visible.
2. **Setup Safety Verification:**
   - [ ] Verify that `after_install()` executes without matching `.env` or Pesapal production consumer secrets.
   - [ ] Verify that all 8 canonical roles are created and available for user assignment.
3. **Casework Queue Verification:**
   - [ ] Check if assignment rules correctly import and route requests using demo user assignments only.
   - [ ] Verify that Web Forms are initialized as unpublished (`published=0`) and login-gated (`login_required=1`).
4. **API Safety Verification:**
   - [ ] Call `/api/method/nilegov_stack.interfaces.frappe.api.public_readiness.get_redacted_case_status_preview?reference_number=req_pass3_001` and verify that NIN, Phone, and Email values are masked (asterisks only).
   - [ ] Confirm that no raw NIRA, URA, or live external database connection calls are triggered.




