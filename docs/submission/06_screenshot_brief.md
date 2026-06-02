# NileGov Stack Screenshot and UI Capture Brief

This brief defines the specific screens to be captured once a working Frappe/Docker host runtime is available. It outlines the URL paths, key user elements, and the value arguments for Ministry evaluators.

---

## Required Screenshot List

### 1. NileGov Case Operations Workspace
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-case-operations`
* **Purpose:** Demonstrates the centralized workspace dashboard designed for desk officers.
* **What Must Be Visible:**
  - Sidebar showing `NileGov Case Operations` under the active module.
  - Shortcut counter cards with filtered numbers for `New Requests`, `Requests Under Review`, `Payment Pending Cases`, and `Ready for Collection`.
* **Value to Evaluator:** Proves the simplicity of operations queue monitoring in Frappe Desk.
* **Runtime Status:** Pending working Frappe container host.

### 2. Service Request List View (Officer Queue)
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-service-request`
* **Purpose:** Displays the active work queue containing the 9 seeded Ntinda, Kampala requests.
* **What Must Be Visible:**
  - Standard list view layout.
  - Case references (`req_pass3_001` through `req_pass3_009`) with corresponding NIN and Name details.
  - Status badges mapping correctly across the lifecycle.
* **Value to Evaluator:** Confirms that case status sorting and assignment fields are ready.
* **Runtime Status:** Pending working host.

### 3. Submitted Case Detail Screen (Intake Form)
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-service-request/req_pass3_001`
* **Purpose:** Displays the citizen intake form populated with lost card replacement details.
* **What Must Be Visible:**
  - Location field displaying `Ntinda, Kampala`.
  - Citizen name `Robert Sebunya` and reference `NGS-NIRA-2026-0001`.
  - Check box marked `Consent Confirmed` representing legal consent capture.
* **Value to Evaluator:** Proves correct intake data structure mapping and consent audit trails.
* **Runtime Status:** Pending working host.

### 4. Simulated NIRA Verification Action Button
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-service-request/req_pass3_001`
* **Purpose:** Shows where officers trigger the simulated identity check.
* **What Must Be Visible:**
  - A custom button group dropdown labelled **Simulated Actions**.
  - Dropdown button named `Trigger Simulated NIRA Verification`.
* **Value to Evaluator:** Displays clear separation between manual tasks and automated simulations.
* **Runtime Status:** Pending working host.

### 5. Simulated NIRA Verification Result
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-service-request/req_pass3_001`
* **Purpose:** Displays the alert success toast and matching status updates.
* **What Must Be Visible:**
  - Success alert text: `Simulated NIRA Verification result: Matched`.
  - Status field `Identity Verification Status` changed from `Requires Review` to `Matched`.
* **Value to Evaluator:** Confirms correct transaction callbacks and database updates.
* **Runtime Status:** Pending working host.

### 6. Simulated Payment Verification Action Button
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-service-request/req_pass3_004`
* **Purpose:** Shows where payment matching is triggered for pending cases.
* **What Must Be Visible:**
  - Form status displaying `Payment Pending`.
  - A button labelled `Trigger Simulated Payment Verification` under the actions dropdown.
* **Value to Evaluator:** Proves the payment tracking process flow.
* **Runtime Status:** Pending working host.

### 7. Simulated Payment Verification Result
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-service-request/req_pass3_004`
* **Purpose:** Shows payment matches.
* **What Must Be Visible:**
  - Success toast alert: `Simulated Payment Verification status: Verified`.
  - Field `Payment Status` updated to `Verified`.
* **Value to Evaluator:** Proves mock payment flow logic.
* **Runtime Status:** Pending working host.

### 8. SLA Overdue Indicator (Milestone Breach Alert)
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-service-request/req_pass3_009`
* **Purpose:** Demonstrates visual alerts for cases that breach standard processing hours.
* **What Must Be Visible:**
  - SLA Deadline date representing a past timestamp.
  - A red visual warning label or indicator flag marking the case status as overdue.
* **Value to Evaluator:** Shows how the prototype ensures processing accountability.
* **Runtime Status:** Pending working host.

### 9. Audit Timeline (Immutable History Trail)
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-service-request/req_pass3_001#timeline`
* **Purpose:** Displays the history log at the bottom of the form.
* **What Must Be Visible:**
  - Timeline cards tracking status transitions.
  - Logs capturing the identity simulation event.
* **Value to Evaluator:** Proves that all modifications are logged for security.
* **Runtime Status:** Pending working host.

### 10. Management Metrics / Workspace Counters
* **Expected Browser Path:** `http://nilegov.local:8000/app/nilegov-case-operations`
* **Purpose:** Shows that supervisor views update after action items are completed.
* **What Must Be Visible:**
  - Counters decrementing `New Requests` and incrementing `Payment Pending Cases`.
* **Value to Evaluator:** Proves structural integrity of the workspace.
* **Runtime Status:** Pending working host.
