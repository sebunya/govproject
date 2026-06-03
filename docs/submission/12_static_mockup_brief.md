# NileGov Stack Static Mockup Brief

This brief provides specifications for a designer to create visual layouts representing the NileGov Stack user interface.

> [!WARNING]
> **Honesty & Compliance Rule:**
> All generated visual assets must be clearly labeled:  
> **"Illustrative interface mockup based on implemented workflow logic. Live browser validation pending deployment."**  
> Under no circumstances should these assets be labeled or presented as live browser screenshots of the active prototype.

---

## 1. Frame 1: Case Operations Workspace
* **Layout Structure:** Frappe Desk dashboard layout. Left-side navigation pane with a main center dashboard area.
* **Header:** Title text showing `NileGov Case Operations` with a subtitle: *"Operations Queue Overview"*.
* **Dashboard Widgets:**
  - Standard card widgets displaying big numbers:
    * **New Requests:** Count `1`
    * **Requests Under Review:** Count `2`
    * **Payment Pending Cases:** Count `1`
    * **Ready for Collection:** Count `1`
  - A small tabular panel showing `SLA Escalation Alerts` (capturing overdue items).

---

## 2. Frame 2: Service Request List View
* **Layout Structure:** Tabular grid displaying request queues.
* **Columns:** `ID`, `Reference No`, `Citizen Name`, `Location`, `Internal Status`, `SLA State`.
* **Rows to Render (Seeded Examples):**
  1. `req_pass3_001` \| `NGS-NIRA-2026-0001` \| `Robert Sebunya` \| `Ntinda, Kampala` \| `Submitted` \| `Within SLA`
  2. `req_pass3_004` \| `NGS-NIRA-2026-0004` \| `David Otim` \| `Ntinda, Kampala` \| `Payment Pending` \| `Within SLA`
  3. `req_pass3_009` \| `NGS-NIRA-2026-0009` \| `Alex Mukasa` \| `Ntinda, Kampala` \| `Under Review` \| `Overdue`

---

## 3. Frame 3: Case Detail Page (Intake Form View)
* **Layout Structure:** Split layout. Left pane contains form field groups, right pane contains the Gunicorn/Frappe Desk timeline sidebar.
* **Fields Group 1 (Citizen Details):**
  - Full Name: `Robert Sebunya`
  - NIN: `CF900000000000`
  - Phone: `+256780000000`
  - Location: `Ntinda, Kampala`
* **Fields Group 2 (Compliance & Verification):**
  - Identity Verification Status: `Matched`
  - Payment Status: `Verified`
  - SLA Status: `Within SLA`
* **Form Action Header:**
  - A dropdown button labelled **Simulated Actions** containing options:
    * `Trigger Simulated NIRA Verification`
    * `Trigger Simulated Payment Verification`

---

## 4. Frame 4: Simulated NIRA Verification Success Callback
* **Layout Structure:** Same as Frame 3, but showing interactive callback visual cues.
* **Visual Additions:**
  - A top-center alert notification toast styled in green:  
    `"Simulated NIRA Verification result: Matched"`
  - The field `Identity Verification Status` highlighted as `Matched` with a green check icon.

---

## 5. Frame 5: Audit Timeline (Timeline History Log)
* **Layout Structure:** Bottom timeline container showing audit event logs.
* **Timeline Events:**
  - *Audit Log Item 1:* `"Robert Sebunya submitted request. Reference No generated: NGS-NIRA-2026-0001."` (Timestamp: `2026-06-02 00:45:00`)
  - *Audit Log Item 2:* `"Simulated NIRA Verification executed by officer_sebunya. Status: Matched. Transaction ID: SIM-NIRA-2026-XXXX."` (Timestamp: `2026-06-02 00:47:00`)
  - *Audit Log Item 3:* `"Internal Status transitioned to Payment Pending."` (Timestamp: `2026-06-02 00:47:10`)
