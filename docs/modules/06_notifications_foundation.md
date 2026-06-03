# Module: Notification Events & Simulated Communication Foundation

## Purpose

The **Notification Events & Simulated Communication Foundation** module provides the privacy-respecting communication tracing, logging, and simulation layer for the NileGov Stack. It ensures that whenever service request workflows transition, officers are assigned, or SLA warnings/breaches/escalations occur, the system records the exact notification events that would be dispatched to the citizen, caseworker, or supervisor. 

To maintain strict security and sandbox isolation, the module does not integrate with live third-party email, SMS, WhatsApp gateways, or SMTP servers. Instead, it relies on a simulated gateway that verifies delivery formats and writes clean trace records, verifying that consent checks are adhered to.

---

## Government Use Case

The primary use case is tracing communication during the **Lost National ID Replacement** service:

1. **Request Received:** When a citizen submits a replacement request (`req-1`), a receipt notification event is initiated. The system verifies that the citizen has active consent for `"Status Notifications"`. If consent is granted, the event moves to `Queued` and then is simulated as sent.
2. **Caseworker Assigned:** When the request is assigned to an officer, a draft notification is generated for the officer notifying them of the new task. Since officer/internal notifications do not require citizen consent, they bypass the consent check and queue directly.
3. **SLA Warning & Overdue alerts:** If the case breaches SLA check thresholds, background sweeps generate `SLA At Risk` or `SLA Overdue` notification events targeting the citizen or queue manager, alerting them to the delay.
4. **Supervisor Escalation:** When a case escalates, a notification event is prepared for the designated supervisor (`supervisor_demo`), marking the transfer of administrative responsibility.

---

## Notification & Consent-Aware Principles

1. **Mandatory Consent Check:** When sending notifications of type `Citizen`, the system queries the active consent records. If consent for `"Status Notifications"` is missing, expired, or withdrawn, the delivery status is marked as `Not Required` instead of `Queued` or `Draft`. The primary service request workflow is **not** blocked.
2. **Deterministic Validation:** The simulated gateway parses target emails and phone numbers (e.g. validating phone length/prefixes and email formatting). If a contact is poorly formatted, it moves to `Simulated Failed` with a descriptive reason.
3. **Immutable Disclaimer:** Every record preserves the disclaimer: *"Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."* This prevents confusion during evaluator dry-runs.
4. **Decoupled Delivery Log:** Delivery statuses (`Draft`, `Queued`, `Simulated Sent`, `Simulated Failed`, `Cancelled`, `Not Required`) track the life-cycle of a communication attempt, separate from the primary service request's workflow status.

---

## Allowed Vocabularies

### Recipient Types
* `Citizen`: Fictional citizen profile contact.
* `Officer`: The caseworker currently handling the service request.
* `Supervisor`: The coordinator or queue reviewer handling an escalated task.
* `Department Queue`: Broadcasts to a general department queue target.
* `System`: Logging or telemetry system targets.

### Channels
* `Email`: Simulated SMTP dispatch.
* `SMS`: Simulated cellular short message.
* `WhatsApp`: Simulated IM dispatch.
* `Portal`: Notification shown in the citizen dashboard.
* `Internal Desk`: In-app alert for administrative officers.
* `Other`: Custom fallback channel.

### Message Types
* `Request Received`, `Under Review`, `Information Required`, `Payment Pending`, `Payment Verified`, `Approved`, `Ready for Collection`, `Closed`, `Rejected`, `SLA At Risk`, `SLA Overdue`, `Escalated`, `Returned to Officer`.

### Delivery Statuses
* `Draft`: Initial state prior to consent checking or scheduling.
* `Queued`: Consent checked and ready for simulated gateway delivery.
* `Simulated Sent`: Gateway processed successfully and marked with a timestamp.
* `Simulated Failed`: Gateways processed but failed validation (e.g., malformed recipient format).
* `Cancelled`: Recalled due to administrative overrides or subsequent workflow transitions.
* `Not Required`: Citizen did not grant active status notification consent.

---

## Entity Schema & Fields

### NileGov Citizen Notification DocType
| Fieldname | Fieldtype | Label | Required? | Description / Valid Values |
| :--- | :--- | :--- | :--- | :--- |
| `notification_event_id` | Data | Notification Event ID | Yes | Unique ID (autoname: `field:notification_event_id`). |
| `service_request` | Link | Service Request | Yes | Links to `NileGov Service Request`. |
| `citizen_profile` | Link | Citizen Profile | No | Links to `NileGov Citizen Profile`. |
| `consent_record` | Link | Consent Record | No | Links to `NileGov Consent Record`. |
| `recipient_type` | Select | Recipient Type | Yes | Citizen, Officer, Supervisor, Department Queue, System. |
| `recipient_reference` | Data | Recipient Reference | No | Reference lookup key. |
| `recipient_placeholder` | Data | Recipient Placeholder | No | Visual preview placeholder name. |
| `recipient` | Data | Recipient | Yes | Target phone number or email address. |
| `channel` | Select | Channel | Yes | Email, SMS, WhatsApp, Portal, Internal Desk, Other. |
| `message_type` | Select | Message Type | Yes | The workflow trigger type. |
| `notification_type` | Select | Notification Type | Yes | Status Update, Clarification Request, Case Closure, SLA Warning, SLA Breach, Escalation. |
| `message_title` | Data | Message Title | No | Subject line or brief header. |
| `message_body_preview` | Small Text | Message Body Preview | No | Truncated message content. |
| `message` | Small Text | Message | Yes | Full message content. |
| `delivery_status` | Select | Delivery Status | Yes | Draft, Queued, Simulated Sent, Simulated Failed, Cancelled, Not Required. |
| `consent_checked` | Check | Consent Checked | Yes | Indicates if a privacy check occurred (0 or 1). |
| `consent_status_at_trigger` | Data | Consent Status At Trigger | No | "Granted", "Missing", "Withdrawn", "Expired". |
| `triggered_by_event` | Data | Triggered By Event | No | Trigger source. |
| `scheduled_at` | Datetime | Scheduled At | No | Dispatch schedule time. |
| `simulated_sent_at` | Datetime | Simulated Sent At | No | Dispatch completion timestamp. |
| `simulated_failed_at` | Datetime | Simulated Failed At | No | Dispatch failure timestamp. |
| `failure_reason` | Small Text | Failure Reason | No | Explanation of malformed recipient or gate failure. |
| `disclaimer` | Small Text | Disclaimer | Yes | Hardcoded safety warning text. |

---

## Workflows & Use Cases Supported

* **Create Notification Event (`CreateNotificationEvent`):** Evaluates a service request and maps its profile to active consent records. Generates a notification, marking it as `Queued` or `Not Required`.
* **Queue Notification (`QueueNotificationEvent`):** Transitions draft messages to queue status.
* **Send Notification (`SendSimulatedNotification`):** Invokes the simulated gateway, verifying format. Transitions to `Simulated Sent` or `Simulated Failed`.
* **Cancel Notification (`CancelNotificationEvent`):** Cancels un-dispatched drafts or queued entries.
* **Queries:** Listing of notification events filtered by service request, citizen profile, channel, or delivery status.

---

## Testing Summary

Verified by 7 dedicated unit and integration tests (suite total: 221 passing tests):
* **Domain Validation:** Confirms validation of recipient types, message channels, and delivery statuses. Checks that missing required parameters raise appropriate errors.
* **State Transitions:** Ensures logical progression (`Draft` -> `Queued` -> `Simulated Sent` / `Simulated Failed`). Prevents re-sending or cancelling completed messages.
* **Consent Verification:** Asserts that an active, granted `"Status Notifications"` consent results in a `Queued` message, while withdrawn, expired, or missing consent flags the record as `Not Required`.
* **Gateway Testing:** Tests that `SimulatedNotificationGateway` logs emails and SMS messages locally without network interaction, and marks invalid formats as failed.
* **Workflow Template Integration:** Validates correct templated message outputs for workflow statuses (`Ready for Collection`), SLA risk warnings (`At Risk`), breaches (`SLA Overdue`), and escalations.

---

## Deployment & Validation Status

* **Status:** Fully implemented at domain, application, infrastructure, seed, and unit test level.
* **Local Run Verification:** All 221 pytest unit tests pass cleanly on python 3.14.5.
* **Production Validation:** Defer bench site migration validation until deploying to a Linux host where Frappe framework commands (`bench`) are available.
