# Module: SLA Rules & Escalation Foundation

## Purpose

The **SLA Rules & Escalation Foundation** module provides the accountability, timeline tracking, and case escalation layer within the NileGov Stack. It defines service response and resolution timelines, evaluates case progression, flags cases as At Risk or Overdue, and automates routing recommendations to supervisors for cases that exceed escalation thresholds. It uses a clean, simulation-based design without live external notification links.

---

## Government Use Case

The primary use case is the SLA tracking for the **Lost National ID Replacement** service.

1. **Rule Setup:** A standard SLA rule is configured for the `LOST_NATIONAL_ID` service type, defining a **4-hour response deadline** (to assign an officer) and a **48-hour resolution deadline** (to resolve the request).
2. **Case Assignment:** The incoming request `req_pass3_001` gets assigned this SLA rule upon creation, calculating specific `response_due_at` and `resolution_due_at` timestamps.
3. **At Risk Flagting:** If a case is still open and has elapsed more than **80%** of its allowed resolution time (e.g. 41 hours for a 48-hour SLA), it is flagged as `At Risk` (`req_pass3_002`).
4. **Overdue Flagting:** If the response or resolution deadline is breached, it shifts to `Overdue` (`req_pass3_003`).
5. **Escalation Recommendation:** If a case is Overdue by more than **2 hours** (the escalation threshold hours), the system updates the escalation state to `Escalation Recommended` (`req_pass3_005`).
6. **Supervisor Escalation:** The coordinator escalates the case to `supervisor_demo` on the **Supervisor Review Queue** (`req_pass3_006`).
7. **Resolution:** Once cleared, the supervisor resolves the escalation, returning the case to the assigned officer's queue (`Returned to Officer`).

---

## SLA & Escalation Principles

1. **Simple Elapsed Math:** Timeline calculations use simple elapsed-hour math (fictional timeline) rather than a complex calendar engine accounting for holidays or customized business hours.
2. **Mock Escalation Target:** Escalations route to a mock supervisor (`supervisor_demo`) in the `Supervisor Review Queue`, keeping the assigned caseworker intact to preserve ownership accountability.
3. **Decoupled Workflow States:** The SLA state tracks time performance, running alongside but not interfering with the administrative assignment status or primary service request statuses.
4. **Immutable Audit Trails:** SLA assignment, state changes, overdue markers, and escalations trigger domain events (e.g. `SLARuleAssigned`, `SLAStateChanged`, `RequestEscalated`) which write to the immutable database audit trail.

---

## Allowed Vocabularies

### SLA States
* `Within SLA`: Processing is within allowed response/resolution limits.
* `At Risk`: Processing time has exceeded the defined warning threshold (e.g., 80% elapsed).
* `Overdue`: Response or resolution deadline has been breached.
* `Paused`: Case is paused (e.g., awaiting citizen information).
* `Met`: SLA resolved successfully (case is approved/rejected and closed).
* `Not Applicable`: No SLA rule is assigned to this request.

### Escalation States
* `Not Escalated`: Standard state for active processing.
* `Escalation Recommended`: Deadline breached past the buffer threshold, requesting escalation.
* `Escalated`: Formally escalated to a supervisor queue.
* `Supervisor Reviewing`: Supervisor is actively investigating the case.
* `Resolved`: Escalation resolved and returned to normal queues.

---

## Entity Schema & Fields

### NileGov SLA Rule DocType
| Fieldname | Fieldtype | Label | Required? | Description / Valid Values |
| :--- | :--- | :--- | :--- | :--- |
| `sla_rule_id` | Data | SLA Rule ID | Yes | Unique ID (autoname). |
| `service_type` | Link | Service Type | Yes | Links to `NileGov Service Type`. |
| `response_hours` | Int | Response Hours | Yes | Hours allowed for initial officer assignment. |
| `resolution_hours` | Int | Resolution Hours | Yes | Hours allowed for complete case resolution. |
| `at_risk_threshold_percent` | Int | At-Risk Threshold Percent | Yes | Percentage of resolution time before warning (default: 80). |
| `escalation_threshold_hours` | Int | Escalation Threshold Hours | Yes | Overdue buffer hours before escalation recommended. |
| `escalation_queue` | Select | Escalation Queue | Yes | Queue to route to on escalation (default: `Supervisor Review Queue`). |
| `escalation_role` | Data | Escalation Role | Yes | Target role username (default: `supervisor_demo`). |
| `active` | Check | Active | Yes | Default: 1. Flag representing rule status. |
| `notes` | Small Text | Notes | No | Descriptive comments. |
| `disclaimer` | Small Text | Disclaimer | Yes | Default: "Prototype simulation only. No live Government registry access." |

### NileGov Service Request DocType (SLA & Escalation Extensions)
| Fieldname | Fieldtype | Label | Required? | Description / Valid Values |
| :--- | :--- | :--- | :--- | :--- |
| `sla_rule` | Link | SLA Rule | No | Links to active `NileGov SLA Rule`. |
| `response_due_at` | Datetime | Response Due At | No | Computed deadline for officer assignment. |
| `resolution_due_at` | Datetime | Resolution Due At | No | Computed deadline for case resolution. |
| `sla_state` | Select | SLA State | Yes | Current SLA state (default: `Not Applicable`). |
| `sla_last_checked_at` | Datetime | SLA Last Checked At | No | Timestamp of the last SLA evaluation sweep. |
| `escalation_state` | Select | Escalation State | Yes | Current escalation state (default: `Not Escalated`). |
| `escalated_at` | Datetime | Escalated At | No | Timestamp of official escalation. |
| `escalated_to` | Link | Escalated To | No | Links to target supervisor `User`. |
| `escalation_reason` | Small Text | Escalation Reason | No | Reason recorded for the escalation. |
| `at_risk_flag` | Check | At Risk | Yes | Flag indicating case has entered the warning window. |
| `overdue_flag` | Check | Overdue | Yes | Flag indicating case has breached deadlines. |

---

## Workflows & Use Cases Supported

* **Create SLA Rule:** Command (`CreateSLARule`) to define new timelines.
* **Assign SLA Rule:** Command (`AssignSLARule`) calculating and writing deadlines to the case.
* **Evaluate SLA State:** Sweeper (`EvaluateSLAState`) calculating progression percentages and marking At Risk/Overdue flags.
* **Escalate Case:** Command (`EscalateCase`) routing case ownership to the supervisor queue.
* **Resolve Escalation:** Command (`ResolveEscalation`) returning case control back to normal desks.
* **Query Listings:** Services listing cases categorized by SLA or escalation status.

---

## Testing Summary

Verified by 6 new pytest unit and integration tests (suite total: 198 passing tests):
* **Domain validation:** Rejects invalid/negative SLA hours and threshold percentages.
* **Deadline calculations:** Asserts computed response and resolution dates.
* **State evaluation progression:** Validates transitions through Within SLA -> At Risk -> Overdue -> Met.
* **Escalation routing:** Asserts that supervisor review is recommended, escalated with reason, and that the assigned caseworker is preserved.
* **Repository integration:** Confirms that `FrappeServiceRequestRepository` maps SLA/escalation fields and saves audit logs correctly under mock tests.

---

## Deployment & Validation Status

* **Status:** Implemented at code, schema, seed, and test level.
* **Runtime Desk Validation:** Pending deployment to a working Linux/Docker/Frappe bench.
* **Manual Setup Note:** Run database migrations (`bench --site nilegov.local migrate`) to apply the schema extensions and run demo seeds.

---

## Claims Registry

### Safe Claims
* Custom SLA rules and dynamic deadline calculators.
* Clean warning thresholds and overdue recommendations.
* Decoupled assignment routing to supervisor queues.
* Full immutable event trail logging.

### Claims to Avoid
* Live email, SMS, or Telegram alerts.
* Business hours calendar configuration (e.g. accounting for weekends or public holidays).
* Automatic reassignment of officers (no automatic load balancer).
* Legal SLA enforcement integration.
