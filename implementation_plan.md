# NileGov Stack Implementation Plan — Pass 8A-1B: Consent Records Foundation

This plan outlines the design and implementation of the **Consent Records Foundation** for the NileGov Stack. The module provides a privacy and permission management framework, recording citizen consent for data processing without claiming live government registry access.

---

## User Review Required

> [!IMPORTANT]
> **Honesty & Simulated Consent Guidelines:**
> 1. **No live government consent checks:** This module does not implement data sharing agreements or legal compliance with active databases.
> 2. **Environment Blocked Warning:** No local container or native bench environment is running. All validations are offline via pytest and syntax checks. Live Desk and database operations are deferred to a working deployment host.

---

## Audit Findings

* **NileGov Consent Record DocType:** Already exists under `apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_consent_record/`.
* **Field Discrepancies:** The current schema defines fields (`statement_version`, `consent_given_by`, `consent_given_at`, `consent_channel`, `service_request`, `consent_statement`) which are checked strictly by `test_doctype_schemas.py`.
* **Missing Fields:** Needs `citizen_profile`, `consent_purpose`, `consent_status`, `expiry_date`, `withdrawal_timestamp`, `recorded_by`, and a `disclaimer` field.
* **Domain Model:** The current `domain/consent.py` is a primitive stub.
* **Seeding:** No consent records are seeded by the current `seed_demo_records.py` script.

---

## Proposed Changes

### 1. DocType Schema & Controller Updates

#### [MODIFY] [nilegov_consent_record.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_consent_record/nilegov_consent_record.json)
* Update `autoname` to `field:consent_record_id`.
* Add `consent_record_id` (Data, required, unique).
* Add `citizen_profile` (Link to `NileGov Citizen Profile`, required).
* Add `consent_purpose` (Select: "Service Request Processing\nSimulated Identity Verification\nSimulated Payment Verification\nStatus Notifications\nFuture MDA Integration Readiness", required).
* Add `consent_status` (Select: "Granted\nWithdrawn\nExpired\nNot Required\nPending", default: "Granted", required).
* Add `expiry_date` (Date, optional).
* Add `withdrawal_timestamp` (Datetime, optional).
* Add `recorded_by` (Data, optional).
* Add `notes` (Small Text, optional).
* Add `disclaimer` (Small Text, default: "Prototype simulation only. No live Government registry access.").
* Modify existing required fields (`service_request`, `consent_statement`, `statement_version`, `consent_given_by`, `consent_given_at`) to make them optional (`"reqd": 0` or omit).
* Update `consent_channel` options to: `"Web Form\nOfficer Assisted\nPortal\nEmail\nPhone\nWhatsApp\nOther"`.

#### [MODIFY] [nilegov_consent_record.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_consent_record/nilegov_consent_record.py)
* Update validator to enforce the new required fields (`citizen_profile`, `consent_purpose`, `consent_status`, `consent_channel`) and remove validations on the old required fields.

### 2. Domain & Application Logic

#### [MODIFY] [consent.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/consent.py)
* Re-implement `ConsentRecord` domain aggregate.
* Add methods: `withdraw(timestamp)`, `is_active(current_time) -> bool`.
* Add enums for Purposes, Statuses, and Channels.

#### [MODIFY] [ports.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/ports.py)
* Declare `ConsentRecordRepository` interface.

#### [NEW] Use Case Handlers
Create the following pure domain application services:
* `[NEW] create_consent_record.py`
* `[NEW] withdraw_consent.py`
* `[NEW] check_active_consent.py`
* `[NEW] list_citizen_consent_records.py`

### 3. Infrastructure & Repository Adapters

#### [NEW] [consent_record_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/consent_record_repository.py)
* Implement `InMemoryConsentRecordRepository`.

#### [NEW] [frappe_consent_record_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_consent_record_repository.py)
* Implement `FrappeConsentRecordRepository` mapping document objects to domain aggregates.

### 4. Integration & Seeding

#### [MODIFY] [seed_demo_records.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/patches/seed_demo_records.py)
* Seed consent records for `CP-001` (Service Request Processing: Granted, Simulated Identity Verification: Granted, Simulated Payment Verification: Granted, Status Notifications: Granted, Future MDA Integration Readiness: Pending).
* Seed one withdrawn consent example (`CP-002`) and one expired consent example (`CP-003`).

---

## Verification Plan

### Automated Tests
* **Pytest Suite:** Run `.venv/bin/pytest` verifying 135 existing tests and new consent tests.
* **New Tests:** Create `test_consent_record.py` verifying:
  - Consent record creation, withdrawal, active status, and expiry checks.
  - Multi-purpose and channel validations.
  - Repository mapping (InMemory and Frappe mocking).
  - Integration checkpoints check active consent before simulated operations.
