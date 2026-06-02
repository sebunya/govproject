# NileGov Stack Demo Walkthrough Script

This script provides step-by-step instructions for demonstrating the **NileGov Stack** service workflow during technical evaluations.

---

## Demo Context: Lost National ID Request
* **Citizen Profile:** Robert Sebunya (NIN: `CF900000000000`)
* **Service requested:** Lost National ID replacement
* **Assigned Officer:** Officer Sebunya (Service Desk Officer)
* **Supervisor:** Supervisor Jane (Supervisor role)

---

## Execution Steps

### Phase 1: Citizen Application & Consent
1. **Citizen Portal Intake:**
   * Open the NileGov Citizen Portal.
   * Click **New Request** and select **Lost National ID Replacement**.
   * Enter applicant details: Name, Email, Phone, and NIN (`CF900000000000`).
2. **Evidence Upload:**
   * Upload the required PDF evidence document: *Police Report of Lost ID*.
   * Click **Next**.
3. **Capture Consent:**
   * A disclaimer appears requiring verification consent:
     * *“I authorize the Ministry to verify my identity details against the simulated national registry for the purpose of this ID replacement application.”*
   * Click **Accept & Sign**. The system captures the digital signature timestamp and transitions status to `Consent Captured`.

### Phase 2: Simulated Identity Check
1. **Trigger Check:**
   * Upon capturing consent, the system initiates the simulated NIRA identity check background job.
   * System calls `IdentityVerificationGateway` inside the integration simulation context.
2. **Review Mock Log:**
   * Open the System Admin console and inspect **Integration Simulation Logs**.
   * Verify the logged response payload showing `success: true` and name match verification flags.
   * The Service Request status changes to `Simulated Identity Check`.

### Phase 3: Case Assignment & Desk Review
1. **Auto-Assignment:**
   * The background scheduler runs, matches the verified case, and assigns it to **Officer Sebunya** (status changes to `Assigned to Officer`).
2. **Desk Evaluation:**
   * Log in as **Officer Sebunya** and open the **NileGov Case and Workflow Operations** workspace.
   * Locate the request in the assigned queue.
   * Click **Start Review**. The system starts the SLA clock, calculating the 24-hour limit (status: `Under Review`).
   * Review citizen details and view the uploaded *Police Report* attachment.

### Phase 4: SLA Breach & Supervisor Escalation
1. **Trigger Escalation (Simulated):**
   * *Option A (System check):* Run the mock time-shift script to trigger an SLA breach.
   * *Option B (Manual):* Click the **Escalate Case** button, entering the reason: *“Verification requires supervisor authorization overrides.”*
   * The status transitions to `Escalated`.
2. **Supervisor Resolution:**
   * Log in as **Supervisor Jane** and navigate to the **Supervisor Review Queue**.
   * Open the escalated case.
   * Review the audit logs and case notes.
   * Click **Approve Resolution** and add the mandatory closure note: *“Verified against simulated backup registry. Approved for card reissue.”*
   * The status changes to `Approved for Next Step` and then automatically terminates at `Closed`.

### Phase 5: Citizen Update & Dashboard Verification
1. **Citizen Tracker Check:**
   * Citizen opens the public tracker page, inputs their reference number (`NLG-REF-XXXXX`), and verifies that status is reported as `Closed` (Resolved).
2. **Leadership Dashboard Verification:**
   * Log in as **MDA Leadership** and inspect the read-only dashboard.
   * Verify the total requests count has updated, pending queue metric decreased, and resolution average charts reflect the case completion.
