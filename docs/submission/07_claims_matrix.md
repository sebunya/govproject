# NileGov Stack Claims Matrix

This matrix classifies the verification status of NileGov Stack features. It dictates the exact wording that must be used during submissions to maintain absolute honesty and avoid overclaims.

| Feature Claim | Status | Technical Evidence | Safe Wording | Wording to Avoid |
| :--- | :--- | :--- | :--- | :--- |
| **Workflow Logic** | **Verified** | Enforced by pure Python domain test suite `test_pass2_demo_flow.py` (150/150 passed). | "Implemented and tested workflow logic." | "Production-tested workflow." |
| **Reference Generation** | **Verified** | Custom autoname code matches `NGS-NIRA-2026-XXXX` format. | "Structured case reference mapping." | "Live registry registered ID." |
| **Status Lifecycle** | **Verified** | Aggregates enforce transitions across the 9 approved statuses. | "9-stage state-enforced transitions." | "Live database workflow engine." |
| **Identity Verification** | **Simulated** | `SimulatedIdentityVerificationGateway` simulates registry lookups with transaction logs. | "Simulated NIRA Identity Verification." | "Connected to NIRA", "Live registry verification." |
| **Payments Foundation & Verification** | **Verified / Implemented but Pending Runtime** | Unit tests in `test_payments.py` pass; `nilegov_payment_record.json` maps amount, channel, status, verification, receipt, and reconciliation attributes. | "Fictional government fee and payment records tracking, simulated verification and receipt generation." | "Connected to MTN MoMo, Airtel Money, Visa, Mastercard, or URA", "Real payment clearance", "Connected to mobile money". |
| **Pesapal API 3.0 Sandbox Adapter** | **Verified / Implemented but Pending Runtime** | Unit tests in `test_pesapal_adapter.py` pass; client and use cases created; 14 provider-specific fields mapped in `nilegov_payment_record.json`. | "Pesapal API 3.0 sandbox adapter foundation implemented. Live mode disabled by default." | "Production payment clearance", "Live mobile money or card processing", "Connected to live Pesapal API". |
| **SLA Tracking & Escalation** | **Verified / Implemented but Pending Runtime** | Unit tests in `test_sla_escalation.py` pass; `nilegov_sla_rule.json` and `nilegov_service_request.json` are updated with SLA response/resolution metrics, at-risk/overdue flags, and supervisor review escalation. | "Fictional SLA tracking, at-risk warnings, and supervisor review escalation." | "Connected to live email/SMS alert systems", "Automatic officer load balancing", "Legal SLA enforcement integration." |
| **Audit Trail** | **Verified** | State changes automatically write immutable entries to database. | "Append-only local audit trail log." | "Blockchain-backed audit", "Decentralized ledger." |
| **Dashboard Metrics** | **Verified** | Pure Python class aggregates operational numbers. | "Calculated workflow metrics." | "Live operational analytics database." |
| **Citizen Profile Foundation** | **Verified / Implemented but Pending Runtime** | Unit tests in `test_citizen_profile.py` pass; `nilegov_citizen_profile.json` is updated with optional NIN and profile reference keys. | "Fictional, NIN-optional citizen profile foundation." | "Connected to real citizen registries", "Enforces real National ID numbers." |
| **Consent Records Foundation** | **Verified / Implemented but Pending Runtime** | Unit tests in `test_consent_record.py` pass; `nilegov_consent_record.json` is updated with purpose, status, and channel vocabularies. | "Fictional, multi-purpose consent records logging permission paths." | "Production consent integrations", "Biometric authorization", "Complies with legal sharing regulations." |
| **Evidence & Document Foundation** | **Verified / Implemented but Pending Runtime** | Unit tests in `test_evidence_document.py` pass; `nilegov_evidence_document.json` is updated with document placeholders, upload channels, and verification logs. | "Fictional, placeholder evidence & document layer." | "Real document verification", "Live police letter verification", "Biometric verification", "OCR validation". |
| **Officer Assignment & Department Queues** | **Verified / Implemented but Pending Runtime** | Unit tests in `test_officer_assignment.py` pass; `nilegov_service_request.json` is updated with assignment statuses, departments, and queue names. | "Fictional, operational case routing and workload queues." | "Integration with government HR systems", "Staff appraisal modules", "Payroll systems". |
| **Frappe DocType Schemas** | **Implemented but Pending Runtime** | 13 custom DocType schemas validated statically by json parser tests. | "Runtime-ready Frappe DocType schemas." | "Deployed DocType schemas." |
| **Desk Actions** | **Implemented but Pending Runtime** | `nilegov_service_request.js` defines buttons mapping to Python endpoints. | "Implemented Desk action buttons." | "Visual browser actions active." |
| **Seed Data** | **Implemented but Pending Runtime** | `seed_demo_records.py` is registered under `patches.txt`. | "Registered database seeding patches." | "Active database records." |
| **REST / API Readiness** | **Verified** | Domain gateways are decoupled from Gunicorn/persistence framework. | "Integration-ready endpoints." | "Active REST API integrations." |
| **Private Cloud Deployment** | **Verified** | Project configures native Docker Compose containing Gunicorn & Redis. | "Docker/Container ready deployment." | "Active cloud-deployed platform." |
| **Notification Events & Simulated Communication** | **Verified / Implemented but Pending Runtime** | Unit tests in `test_notification_events.py` pass; `nilegov_citizen_notification.json` contains recipient type, channel, message type, and delivery status fields with consent status tracking. | "Fictional, consent-aware notification events tracing and communication simulation." | "Connected to live email/SMS/WhatsApp networks", "SMTP server configuration", "Real citizen message delivery". |
| **Service Catalogue & SLA Settings** | **Verified / Implemented but Pending Runtime** | Unit tests in `test_service_catalogue.py` pass; `nilegov_service_catalogue.json` contains 19 configuration fields, defaults mapping, and evidence checklist validations. | "Fictional Service Catalogue configuration layer, default mappings, and required documents checklists." | "Connected to live government registries", "Active Ministry service directories", "Production fee catalog". |
| **M&E / Reporting Foundation** | **Implemented (Pass 11B-1)** | Unit tests in `test_reporting_snapshot.py` pass; `nilegov_reporting_snapshot.json` (Pass 11B-1) is a 40-field Frappe DocType with Int count fields, Code/JSON summary fields, required disclaimer, and NileGov-prefixed permission rows; `test_reporting_snapshot_doctype.py` (41 tests) validates schema, permissions and controller; `FrappeReportingSnapshotRepository` maps all fields to this DocType. | "Fictional M&E reporting snapshots compiling pipeline metrics from demo data." | "Connected to live government dashboards", "Official performance statistics", "Production analytics database". |
| **Future UGHub Onboarding** | **Future Integration** | Pluggable design allows changing gateways without modifying domain logic. | "UGHub-compatible integration points." | "Connected to UGHub", "Onboarded on UGHub." |
| **MDA Deployments** | **Simulated** | Prototype environment is standalone and lacks live connection. | "Prototype simulation only." | "Active pilot in Ntinda", "Live Ministry system." |


## API / Interoperability Readiness Claims

| Claim | Status | Evidence | Boundary |
|---|---|---|---|
| API readiness foundation implemented | Implemented | Domain models, envelope helpers and payload builders exist in the application/domain layer | Prototype only |
| REST-ready payload contracts implemented | Implemented | Service request, identity simulation, payment simulation, notification and reporting payload builders exist | Not exposed as live public endpoints yet |
| API success and error envelopes implemented | Implemented | `build_api_envelope.py` provides success and error envelope helpers | Runtime API validation deferred |
| Correlation ID and idempotency key support implemented | Implemented | `generate_integration_keys.py` and domain helpers generate trace keys | No production gateway yet |
| Simulated interoperability request model implemented | Implemented | `interoperability.py` defines `IntegrationRequest` and `IntegrationResponse` | No live government system contacted |
| Integration request repository implemented | Implemented | In-memory repository supports testable simulated requests | Frappe runtime persistence deferred |
| Safe payload builders implemented | Implemented | Builders intentionally exclude raw NIN, payment credentials and contact secrets | Requires runtime validation before production use |
| UGHub/NIRA/URA integration active | Not implemented | No live endpoints or Data Sharing Agreements are configured | Formal onboarding required |
| Pesapal live payment integration active | Not implemented | Sandbox adapter exists; live mode remains disabled | Production activation deferred |

## Roles, Permissions and User Profiles Claims

| Claim | Status | Evidence | Boundary |
|---|---|---|---|
| NileGov role model defined | Implemented | `docs/modules/11_roles_permissions_foundation.md` and `permission_policy.py` | Runtime Frappe role setup pending |
| Canonical NileGov role names aligned across repo | Implemented (Pass 11B-2) | `hooks.py`, `seed_roles.py`, `interfaces/permissions.py`, all 15 DocType JSON files and `workspace.json` now use 8 canonical NileGov-prefixed roles | Runtime Frappe permission validation pending |
| DocType permission rows include NileGov operational roles | Implemented (Pass 11B-2) | All 15 DocType JSON files now carry role-appropriate read/write/create rows per canonical role | Runtime access control validation pending |
| Sensitive DocTypes identified | Implemented | Permission policy helper lists sensitive DocTypes | Runtime permission validation pending |
| Audit and integration logs protected by design | Implemented (Pass 11B-2) | Tests in `test_role_alignment.py` confirm ordinary NileGov roles cannot write protected logs; DocType permission rows enforce read-only for System Auditor | Frappe Role Permission Manager validation pending |
| Payment and evidence duties separated | Implemented (Pass 11B-2) | `test_role_alignment.py` and `test_permission_hardening.py` verify duty separation in both application policy and DocType permission rows | Runtime role enforcement pending |
| M&E Viewer is read-only across operational DocTypes | Implemented (Pass 11B-2) | DocType permission rows grant M&E Viewer read access only; `test_role_alignment.py` verifies no write/create access | Runtime role enforcement pending |
| Live MDA/government access configured | Not implemented | No live government directory or registry access configured | Formal onboarding required |
