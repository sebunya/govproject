# Module: Consent Records Foundation

## Purpose

The **Consent Records Foundation** module manages citizen data privacy authorizations within the NileGov Stack. It provides an audit trail documenting when, where, and for what purposes a citizen granted permission to process their data. By decoupling authorization from live integrations, it establishes a privacy-first foundation ready for later Consent Records, Evidence Documents, Notifications, Payments, and future government registry integrations.

---

## Government Use Case

The primary use case demonstrated is the **Lost National ID Replacement** service in Ntinda, Kampala.

### Consent Intake & Enforcement Flow
1. A fictional citizen (e.g. *Demo Citizen A*) reports a lost National ID.
2. During service request intake, the citizen grants consent for data processing.
3. The system creates a series of **Consent Records** linked to the citizen's profile (`CP-001`) and the service request (`req_pass3_001`).
4. Officer-triggered actions (such as Simulated NIRA Identity Check or Simulated Payment Verification) perform a **soft check** against the active consent repository. If active consent is not found for that specific purpose, these checks record a pending/Requires Review status, preventing silent processing.

---

## Privacy & Consent Principles

1. **Explicit Granularity:** Consent is mapped to specific business purposes (e.g. Identity verification, Notifications) rather than a broad all-in-one agreement.
2. **Revocability:** Citizens can withdraw consent at any time, transitioning records to a `Withdrawn` status.
3. **No Legal Alignment Claims:** This module provides a technical blueprint and prototype simulation. It does not replace legal Data Sharing Agreements or represent statutory compliance under the Data Protection and Privacy Act.
4. **Non-Intrusive Soft Enforcement:** A soft-check policy is used to ensure existing demo flows are not disrupted while validating that active consent is checked programmatically.

---

## Allowed Vocabularies

### Consent Purposes
* **Service Request Processing:** Core authority to open and audit cases.
* **Simulated Identity Verification:** Authority to trigger mock NIRA registry matching.
* **Simulated Payment Verification:** Authority to check mock payment status.
* **Status Notifications:** Permission to route transactional SMS, Email, or WhatsApp alerts.
* **Future MDA Integration Readiness:** Scaffolding to onboard future cross-ministry integrations.

### Consent Channels
* `Web Form`
* `Officer Assisted`
* `Portal`
* `Email`
* `Phone`
* `WhatsApp`
* `Other`

### Consent Statuses
* `Granted`
* `Withdrawn`
* `Expired`
* `Not Required`
* `Pending`

---

## Entity Schema & Fields

### NileGov Consent Record DocType

| Fieldname | Fieldtype | Label | Required? | Description / Valid Values |
| :--- | :--- | :--- | :--- | :--- |
| `consent_record_id` | Data | Consent Record ID | Yes | Unique reference (e.g. `CON-CP-001-1`). |
| `citizen_profile` | Link | Citizen Profile | Yes | Links to parent `NileGov Citizen Profile`. |
| `consent_purpose` | Select | Consent Purpose | Yes | Approved purposes list (see above). |
| `consent_channel` | Select | Consent Channel | Yes | Approved channels list (see above). |
| `consent_status` | Select | Consent Status | Yes | `Granted`, `Withdrawn`, `Expired`, `Not Required`, `Pending`. |
| `service_request` | Link | Service Request | No | Optional link to `NileGov Service Request`. |
| `expiry_date` | Date | Expiry Date | No | Optional date when consent automatically expires. |
| `withdrawal_timestamp` | Datetime | Withdrawal Timestamp | No | Records timestamp when consent was revoked. |
| `recorded_by` | Data | Recorded By | No | Actor recording the consent (e.g. `officer_demo`). |
| `notes` | Small Text | Notes | No | Additional remarks. |
| `disclaimer` | Small Text | Disclaimer | Yes | Default: "Prototype simulation only. No live Government registry access." |

*Note: Legacy fields (`consent_statement`, `statement_version`, `consent_given_by`, `consent_given_at`, `ip_address`, `user_agent`) are kept optional to preserve backward compatibility with static schema tests.*

---

## Workflows & Use Cases Supported

* **Create Consent Record:** Application service (`CreateConsentRecord`) registering a granted purpose.
* **Withdraw Consent:** Revokes active consent, recording status as `Withdrawn` (`WithdrawConsent`).
* **Check Active Consent:** Evaluates if a profile has active granted consent for a purpose (`CheckActiveConsent`).
* **Query Records:** Retrieves records by profile or related service request.
* **Soft Verification Enforcement:** Verification handlers query the consent repository to confirm permissions before logging simulated success states.

---

## Testing Summary

Verified by 15 new pytest integration and unit tests (suite total: 150 passing tests):
* **Domain aggregate checks:** Validates creation, status transitions, and expiry checks.
* **Consent checks on simulation:** Proves simulated NIRA registry checks fail/require review if identity verification consent is not active.
* **Patches Seeding:** Verifies mock consent entries are written successfully under unit mocks.

---

## Deployment & Validation Status

* **Status:** Implemented at code, schema, seed, and test level.
* **Runtime Desk Validation:** Pending deployment to Hetzner or another working Linux/Docker host.
* **Manual Setup Note:** Run `bench --site nilegov.local migrate` on the deployment host to update schema tables and execute the `seed_demo_records` patch.

---

## Claims Registry

### Safe Claims
* Fully implemented domain permissions and validation logic.
* Complete Gunicorn-ready database schema definitions.
* Idempotent seeding patch written and registered in `patches.txt`.
* Decoupled architecture allowing pluggable repository swapping.

### Claims to Avoid
* Live authorization sync with government databases.
* Endorsement of statutory legal compliance.
* Formal replacements for Data Sharing Agreements.
