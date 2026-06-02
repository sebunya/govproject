# NileGov Stack Data Model Specification

This document establishes the database schema contract and custom **DocType** definitions configured inside the shared enterprise services layer (MariaDB). These definitions serve as the exact structural blueprints for the database migration pass (Pass 2).

---

## The 13 custom DocType Schemas

### 1. NileGov Citizen Profile
* **Purpose:** Stores authenticated citizen profiles requesting service workflows.
* **Key Fields:**
  * `name` (Data, Primary Key): Unique alphanumeric ID (`NLG-CIT-YYYY-XXXXX`).
  * `nin` (Data, Unique): 14-character Ugandan National Identification Number.
  * `first_name` (Data): Citizen's first name.
  * `last_name` (Data): Citizen's last name.
  * `email` (Data): Contact email address.
  * `phone` (Data): Contact mobile number.
  * `is_active` (Check): System access status toggle.
* **Required Fields:** `nin`, `first_name`, `last_name`, `email`, `phone`.
* **Links:** None.
* **Child Tables:** None.
* **Permissions:** 
  * Citizen: Read (Own profile only).
  * MDA Admin: Read/Write.
  * Officers/Supervisors: Read-only.
* **Audit Requirements:** Log all email/phone detail edits.
* **PII Status:** **Yes** (Contains NIN, Name, Email, Phone).
* **Dashboard Presence:** No (Individual record).

---

### 2. NileGov Service Type
* **Purpose:** Defines the categories of public services available to citizens.
* **Key Fields:**
  * `name` (Data, Primary Key): Service Type Name (e.g. `Lost National ID Replacement`).
  * `description` (Small Text): Instructions on document requirements.
  * `sla_hours` (Int): Allowed response window in hours.
  * `active` (Check): Availability toggle.
* **Required Fields:** `name`, `sla_hours`.
* **Links:** None.
* **Child Tables:** None.
* **Permissions:**
  * Public (Guest/Citizen): Read-only (to browse services).
  * MDA Admin: Read/Write.
  * System Admin: Read/Write.
* **Audit Requirements:** Log adjustments to `sla_hours`.
* **PII Status:** No.
* **Dashboard Presence:** Yes (Used as categorization labels in charts).

---

### 3. NileGov Service Request
* **Purpose:** The primary transactional aggregate tracking intake and workflow progress.
* **Key Fields:**
  * `name` (Data, Primary Key): Unique request ID (`NLG-SR-YYYY-XXXXX`).
  * `reference_no` (Data, Unique): Citizen-facing tracker reference (`NLG-REF-XXXXX`).
  * `citizen_profile` (Link -> `NileGov Citizen Profile`): Applicant profile.
  * `service_type` (Link -> `NileGov Service Type`): Target service category.
  * `status` (Select): State enumeration (Draft, Submitted, Consent Captured, etc.).
  * `assigned_officer` (Link -> `User`): Allocated case reviewer.
  * `sla_deadline` (Datetime): Breach time limit indicator.
  * `has_consent` (Check): Flag tracking citizen consent signature.
  * `identity_verified` (Check): Flag tracking simulated registry check status.
* **Required Fields:** `reference_no`, `citizen_profile`, `service_type`, `status`.
* **Links:** `NileGov Citizen Profile`, `NileGov Service Type`, `User`.
* **Child Tables:** None.
* **Permissions:**
  * Citizen: Read/Write (Draft or More Information Required status; own requests only).
  * Officer: Read/Write (Assigned requests only).
  * Supervisor: Read/Write (All escalated/assigned requests).
  * MDA Leadership: Read-only.
* **Audit Requirements:** Log all status transitions and assignments.
* **PII Status:** **Yes** (Linked directly to citizen profile data).
* **Dashboard Presence:** **Yes** (Primary dataset for caseload and compliance metrics).

---

### 4. NileGov Consent Record
* **Purpose:** Tamper-evident record of citizen consent.
* **Key Fields:**
  * `name` (Data, Primary Key): Consent ID.
  * `service_request` (Link -> `NileGov Service Request`): Target request.
  * `verified` (Check): Legal authorization flag.
  * `ip_address` (Data): Originating connection address.
  * `verified_at` (Datetime): Audit timestamp.
* **Required Fields:** `service_request`, `verified`, `ip_address`, `verified_at`.
* **Links:** `NileGov Service Request`.
* **Child Tables:** None.
* **Permissions:**
  * Citizen: Read-only (Own request consent).
  * Officer/Supervisor: Read-only.
* **Audit Requirements:** Secure immutable record. Deletions/Edits blocked.
* **PII Status:** **Yes** (Logs signature consent for specific citizen requests).
* **Dashboard Presence:** Yes (Audit metrics).

---

### 5. NileGov Evidence Document
* **Purpose:** Tracks citizen attachments and their review status.
* **Key Fields:**
  * `name` (Data, Primary Key): Attachment ID.
  * `service_request` (Link -> `NileGov Service Request`): Target case.
  * `file_attachment` (Attach): Path to local file system.
  * `file_hash` (Data): SHA-256 validation signature.
  * `verification_status` (Select): Review state (Unchecked, Verified, Rejected).
* **Required Fields:** `service_request`, `file_attachment`, `file_hash`, `verification_status`.
* **Links:** `NileGov Service Request`.
* **Child Tables:** None.
* **Permissions:**
  * Citizen: Read/Write (Own attachments, Draft state only).
  * Officer: Read/Write (Assigned cases).
  * Supervisor: Read/Write.
* **Audit Requirements:** Log hash matches and manual officer review status changes.
* **PII Status:** **Yes** (Contains uploaded police reports/personal files).
* **Dashboard Presence:** No.

---

### 6. NileGov Simulated Identity Verification
* **Purpose:** Mock transaction logs recording registry identity queries.
* **Key Fields:**
  * `name` (Data, Primary Key): Verification ID.
  * `service_request` (Link -> `NileGov Service Request`): Target case.
  * `verified` (Check): Success boolean flag.
  * `gateway_message` (Data): Simulation result details.
  * `checked_at` (Datetime): Event timestamp.
* **Required Fields:** `service_request`, `verified`, `gateway_message`, `checked_at`.
* **Links:** `NileGov Service Request`.
* **Child Tables:** None.
* **Permissions:**
  * System Admin: Read-only.
  * Officer/Supervisor: Read-only.
* **Audit Requirements:** Write-once log. Deletion blocked.
* **PII Status:** **Yes** (Contains registry feedback for a specific NIN).
* **Dashboard Presence:** Yes (Verify rates).

---

### 7. NileGov Case Note
* **Purpose:** Logs chronological dialogue annotations added during reviews.
* **Key Fields:**
  * `name` (Data, Primary Key): Case Note ID.
  * `service_request` (Link -> `NileGov Service Request`): Target case.
  * `author` (Link -> `User`): Annotator.
  * `is_private` (Check): Toggle hiding from citizen portal.
  * `note_content` (Text): Content details.
* **Required Fields:** `service_request`, `author`, `note_content`.
* **Links:** `NileGov Service Request`, `User`.
* **Child Tables:** None.
* **Permissions:**
  * Citizen: Read-only (If `is_private` is unchecked; own cases only).
  * Officer: Read/Write (Assigned requests only).
  * Supervisor: Read/Write.
* **Audit Requirements:** Log creating author. Editing blocked.
* **PII Status:** **Yes** (May contain sensitive reviewer notes on citizens).
* **Dashboard Presence:** No.

---

### 8. NileGov SLA Rule
* **Purpose:** Configures SLA criteria per service category.
* **Key Fields:**
  * `name` (Data, Primary Key): SLA Rule ID.
  * `service_type` (Link -> `NileGov Service Type`): Category target.
  * `limit_hours` (Int): Duration threshold.
* **Required Fields:** `service_type`, `limit_hours`.
* **Links:** `NileGov Service Type`.
* **Child Tables:** None.
* **Permissions:**
  * MDA Admin: Read/Write.
  * Officer/Supervisor: Read-only.
* **Audit Requirements:** Log rule configuration changes.
* **PII Status:** No.
* **Dashboard Presence:** Yes (Target limits comparison).

---

### 9. NileGov SLA Event
* **Purpose:** Logs real milestones relative to target SLAs.
* **Key Fields:**
  * `name` (Data, Primary Key): SLA Event ID.
  * `service_request` (Link -> `NileGov Service Request`): Target case.
  * `step` (Data): Step name (e.g. `Under Review`).
  * `start_time` (Datetime): Entry timestamp.
  * `deadline` (Datetime): Breach timestamp.
  * `breached` (Check): Breached flag.
* **Required Fields:** `service_request`, `step`, `start_time`, `deadline`.
* **Links:** `NileGov Service Request`.
* **Child Tables:** None.
* **Permissions:**
  * System Admin: Read-only.
  * Officer/Supervisor: Read-only.
* **Audit Requirements:** Automated system logs. No manual edits.
* **PII Status:** No.
* **Dashboard Presence:** **Yes** ( casetime and response average benchmarks).

---

### 10. NileGov Escalation Record
* **Purpose:** Documents case escalations on processing breaches.
* **Key Fields:**
  * `name` (Data, Primary Key): Escalation ID.
  * `service_request` (Link -> `NileGov Service Request`): Target case.
  * `reason` (Small Text): Details.
  * `escalated_by` (Link -> `User`): Acting officer or System.
  * `escalated_at` (Datetime): Creation timestamp.
  * `resolution_status` (Select): Pending, Resolved.
* **Required Fields:** `service_request`, `reason`, `escalated_by`, `escalated_at`.
* **Links:** `NileGov Service Request`, `User`.
* **Child Tables:** None.
* **Permissions:**
  * Officer: Read-only.
  * Supervisor: Read/Write.
* **Audit Requirements:** Log resolution supervisor and timestamps.
* **PII Status:** No.
* **Dashboard Presence:** **Yes** (Caseload flags indicators).

---

### 11. NileGov Citizen Notification
* **Purpose:** Outgoing notification log (simulated SMS, Email).
* **Key Fields:**
  * `name` (Data, Primary Key): Notification ID.
  * `service_request` (Link -> `NileGov Service Request`): Target case.
  * `channel` (Select): SMS, Email.
  * `recipient` (Data): Phone number or Email address.
  * `message_body` (Text): Content sent.
  * `sent_at` (Datetime): Timestamp.
  * `status` (Select): Pending, Sent, Failed.
* **Required Fields:** `service_request`, `channel`, `recipient`, `message_body`, `sent_at`, `status`.
* **Links:** `NileGov Service Request`.
* **Child Tables:** None.
* **Permissions:**
  * Citizen: Read-only (Own notifications).
  * Officer/Supervisor: Read-only.
* **Audit Requirements:** Write-once log. Deletion blocked.
* **PII Status:** **Yes** (Contains phone numbers, email addresses, and message logs).
* **Dashboard Presence:** Yes (Dispatch stats).

---

### 12. NileGov Audit Event
* **Purpose:** TAMPER-EVIDENT logs mapping transactional actions.
* **Key Fields:**
  * `name` (Data, Primary Key): Event hash primary signature.
  * `service_request` (Link -> `NileGov Service Request`): Target case.
  * `operator_id` (Link -> `User` or `Citizen`): Actor.
  * `action` (Data): Transition code (Submit, Assign, Close, etc.).
  * `details` (Small Text): Context details.
  * `prev_hash` (Data): Previous log hash signature.
  * `current_hash` (Data): SHA-256 calculated signature.
* **Required Fields:** `operator_id`, `action`, `prev_hash`, `current_hash`.
* **Links:** `NileGov Service Request`.
* **Child Tables:** None.
* **Permissions:**
  * System Admin: Read-only.
  * Supervisor: Read-only.
  * Citizen/Officer: Forbidden.
* **Audit Requirements:** Strict write-once ledger. Any edit/deletion attempt fails database validations.
* **PII Status:** No.
* **Dashboard Presence:** Yes (Security reporting charts).

---

### 13. NileGov Integration Simulation Log
* **Purpose:** Logs transactional interactions with mocked registries.
* **Key Fields:**
  * `name` (Data, Primary Key): Log ID (`SIM-LOG-XXXXXX`).
  * `service_request` (Link -> `NileGov Service Request`): Target case.
  * `timestamp` (Datetime): Time.
  * `gateway_name` (Data): Integration checkpoint (`NIRA`, `URA`, `UGHub`).
  * `request_payload` (Code): Output parameters.
  * `response_payload` (Code): Input parameters.
  * `success` (Check): Success boolean flag.
* **Required Fields:** `timestamp`, `gateway_name`, `success`.
* **Links:** `NileGov Service Request`.
* **Child Tables:** None.
* **Permissions:**
  * System Admin: Read-only.
  * Supervisor: Read-only.
  * Citizen/Officer: Forbidden.
* **Audit Requirements:** Write-once log. Deletion blocked.
* **PII Status:** **Yes** (Contains mock query names, TINs, and NIN details).
* **Dashboard Presence:** Yes (Performance stats).
