# NileGov Stack Demo Video Script

**Title:** NileGov Stack: Digitizing Citizen Services Natively (Lost National ID replacement service demo)  
**Duration:** 10 minutes (600 seconds)  
**Tone:** Professional, direct, and transparent.

---

## 1. Opening (0:00 - 0:30)
* **Visual:** Title slide displaying the NileGov Stack logo, prototype name, and the subtitle: *"Simulated Govt Service Workflow Prototype — Local Desk Customizations."*
* **Narrator (Audio):**
  > "Hello and welcome to this demonstration of the NileGov Stack, a modular public service digitization framework designed for Ministries, Departments, and Agencies. Today, we present a complete case walkthrough using the Lost National ID Replacement service prototype. We will walk through the intake, registry checks, payment verification, SLA monitoring, and final closure of a request from Ntinda, Kampala."

---

## 2. The Problem Space (0:30 - 1:30)
* **Visual:** Slide listing the challenges in manual public service delivery: paper handovers, slow verification times, lacks transparency, and untracked SLAs.
* **Narrator (Audio):**
  > "Government service delivery in many MDAs relies heavily on paper processing. Citizens suffer long wait times, while officers lack centralized views of their work queues. Furthermore, tracking service standards and identifying operational bottlenecks is difficult. Digitizing these workflows requires a lightweight system that is easy to deploy, adaptable, and conforms to local regulatory compliance guidelines without expensive proprietary vendor platform licensing."

---

## 3. Solution Overview (1:30 - 2:30)
* **Visual:** High-level system architecture slide showing the relation between the pure Python core logic and the Frappe Framework runtime.
* **Narrator (Audio):**
  > "NileGov Stack answers this challenge by utilizing the open-source Frappe web framework. It separates the core business state machine — written in decoupled pure Python — from the Gunicorn Web and MariaDB persistence layer. In today's walk-through, we demonstrate the citizen's intake, the officer's evaluation queue, and mock external system integration logs showing how a request progresses across 9 workflow statuses, backed by an immutable audit trail."

---

## 4. Citizen Request Scenario: Ntinda, Kampala (2:30 - 4:00)
* **Visual:** Diagram of the custom `NileGov Service Request` form showing fields populated for a fictional citizen: Full Name *Robert Sebunya*, NIN *CF900000000000*, Location *Ntinda, Kampala*, Reason *Lost ID*, and Police Reference Number *NGS-NIRA-2026-0001*.
* **Narrator (Audio):**
  > "Let's begin with the citizen intake scenario. A citizen in Ntinda, Kampala reports a lost National ID. This creates a new request record under the unique reference NGS-NIRA-2026-0001. The system captures the citizen's PII, location, and crucially, legal consent to share registry data. The request is initially saved with the status of 'Submitted', and an automatic SLA resolution deadline of 48 hours is calculated and stored in the database."

---

## 5. Officer Workflow & Desk Queues (4:00 - 6:00)
* **Visual:** Illustrative view of the `NileGov Case Operations` workspace dashboard. Visual highlights focus on KPI counter widgets for `New Requests`, `Requests Under Review`, and `Payment Pending Cases`.
* **Narrator (Audio):**
  > "Logging into the Frappe Desk as the assigned officer, we land directly on the NileGov Case Operations workspace. This dashboard displays filtered operations queues. Clicking on 'New Requests' displays our Ntinda intake record. The officer assigns the request to themselves and changes the status to 'Under Review', which triggers an immutable entry in the audit event log, establishing accountability."

---

## 6. Simulated NIRA Verification (6:00 - 7:00)
* **Visual:** Detailed detail page of the case showing the **Simulated Actions** dropdown and the button **Trigger Simulated NIRA Verification**.
* **Narrator (Audio):**
  > "Upon initiating the review, the officer must match the citizen's NIN against the National Identification & Registration Authority registry. Since this is a prototype, we invoke a Simulated NIRA Identity Verification check. Clicking this button queries our mock API gateway, returning a success message, changing the status field to 'Matched', and logging the transaction. The transaction logs include clear disclaimers stating that this is a simulated sandbox check only."

---

## 7. Simulated Payment Verification (7:00 - 8:00)
* **Visual:** The request page transitions to `Payment Pending` status, showing the **Trigger Simulated Payment Verification** button.
* **Narrator (Audio):**
  > "With the citizen's identity matched, the request transitions to 'Payment Pending'. The officer triggers the Simulated Payment Verification check. This mocks confirmation of the replacement fee via mobile money or URA portals. Once verified, the payment status changes to 'Verified' and the workflow moves to 'Approved'."

---

## 8. SLA, Audit Trail, and Dashboard Metrics (8:00 - 9:30)
* **Visual:** Zooming in on the **SLA Deadline** field, showing status "Within SLA" for active records, and displaying the timeline audit logging trail.
* **Narrator (Audio):**
  > "Throughout this process, the system dynamically calculates the SLA milestones. For overdue requests, an alert is displayed. At the bottom of the form, the timeline logs all events. Finally, the NileGov Case Operations dashboard counters update in real time, giving supervisors immediate operational visibility."

---

## 9. Closing & Honesty Disclaimer (9:30 - 10:00)
* **Visual:** Final slide showing the implementation status matrix and GitHub repository coordinates.
* **Narrator (Audio):**
  > "The NileGov Stack codebase is fully developed and verified by our 118-check test suite. Live browser Desk validation is currently pending deployment on a working container host environment. All external registry connections are simulated models. NileGov Stack provides a secure, flexible, and integration-ready foundation to help public agencies digitize citizen services. Thank you for your time."
