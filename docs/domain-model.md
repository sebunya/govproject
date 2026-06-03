# NileGov Stack Domain Model Specification

This document defines the core business policies, workflows, and data models of the **NileGov Stack** using domain-driven design principles.

---

## Bounded Contexts & Aggregate Root

The central entity is the **Service Request** aggregate root. It coordinates all associated data structures, state changes, validations, and domain events within the bounded contexts.

```text
                  ┌──────────────────────┐
                  │    Service Type      │
                  └──────────┬───────────┘
                             │ (Classifies)
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                   SERVICE REQUEST (Aggregate Root)           │
│                                                              │
│  * request_id / reference_no                                 │
│  * status (WorkflowStatus)                                   │
│  * dates (submitted, assigned, completed)                    │
│                                                              │
│   ┌────────────────────┐            ┌────────────────────┐   │
│   │  Citizen Profile   │            │   Consent Record   │   │
│   └────────────────────┘            └────────────────────┘   │
│   ┌────────────────────┐            ┌────────────────────┐   │
│   │ Evidence Documents │            │  Simulated ID Ver  │   │
│   └────────────────────┘            └────────────────────┘   │
│   ┌────────────────────┐            ┌────────────────────┐   │
│   │     Case Notes     │            │ SLA & Esc Events   │   │
│   └────────────────────┘            └────────────────────┘   │
│   ┌────────────────────┐            ┌────────────────────┐   │
│   │   Notifications    │            │    Audit Events    │   │
│   └────────────────────┘            └────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

The Service Request aggregate root encapsulates:
1. **Citizen Profile:** Reference to the applicant (NIN, Name, Contact, Address).
2. **Service Type:** The specific request type (e.g., *Lost National ID replacement*).
3. **Consent Records:** Audit-verified citizen permission details.
4. **Evidence Documents:** Document references (file path, hash, audit classification).
5. **Simulated Identity Verification:** Log of the identity check simulation result.
6. **Case Notes:** Chronological dialogue and logs added by case officers.
7. **SLA & Escalation Events:** Deadline rules, current status, and breach tracking.
8. **Citizen Notifications:** Log of outgoing SMS/Email status updates.
9. **Audit Log:** Append-only audit trail of state changes.

---

## Bounded Context Boundaries

1. **Citizen Service Intake Context:** Focuses on the citizen's application journey, validating identity requirements (NIN structure), recording consent, and collecting attachments.
2. **Case Management Context:** Manages officer workflow queues, assignment algorithms, case note annotations, reviews, and supervisor escalations.
3. **SLA and Escalation Context:** Defines SLA policies per Service Type and automates state changes to `Escalated` if processing windows breach.
4. **Evidence Management Context:** Ensures secure handling of attachments, checks file type permissions, and logs validation statuses.
5. **Integration Simulation Context:** Handles interactions with mocked external systems (NIRA registry checks, URA tax validations, UGHub bus messages).
6. **Audit and Compliance Context:** Automatically captures system actions, hashing states to prevent unauthorized log tampering.

---

## Workflow Statuses & State Transitions

The NileGov workflow utilizes strict state transitions to enforce accountability.

| Status | Allowed Next Statuses | Description |
| :--- | :--- | :--- |
| **Draft** | `Submitted` | Request created by citizen, editable. |
| **Submitted** | `Consent Captured`, `Withdrawn` | Request sent; requires citizen verification. |
| **Consent Captured** | `Simulated Identity Check`, `Withdrawn` | Legal consent confirmed by applicant. |
| **Simulated Identity Check** | `Assigned to Officer`, `Rejected` | Verification simulation completed. |
| **Assigned to Officer** | `Under Review` | System assigns the case to an active desk. |
| **Under Review** | `More Information Required`, `Approved for Next Step`, `Escalated`, `Rejected` | Desk officer evaluates submitted evidence. |
| **More Information Required**| `Under Review`, `Withdrawn` | Citizen requested to update attachments. |
| **Escalated** | `Supervisor Review` | SLA breached; case flagged for review. |
| **Supervisor Review** | `Approved for Next Step`, `Rejected` | Supervisor reviews escalated files. |
| **Approved for Next Step** | `Closed` | Authorized processing complete. |
| **Closed** | None (Terminal) | Request resolved successfully. |
| **Rejected** | None (Terminal) | Request rejected with closure note. |
| **Withdrawn** | None (Terminal) | Citizen aborted the request. |

---

## Core Domain Rules

These constraints are coded inside the pure Python domain layer. They fail transactions immediately if violated:

1. **Consent Requirement:** A service request cannot transition to `Submitted` or `Consent Captured` status without capturing a valid signature/verification record.
2. **Identity Prerequisite:** A request cannot proceed to `Simulated Identity Check` until the consent record is verified.
3. **Queue Restriction:** A request cannot be assigned to an officer queue unless the identity simulation check has been successfully logged.
4. **SLA Initialization:** A request cannot transition to `Under Review` without calculating and assigning an SLA deadline.
5. **Mandatory Documentation:** A request cannot transition to `Closed` or `Rejected` without a decision note and audit footprint.
6. **Domain Event Propagation:** Every major state transition (Submission, Assignment, SLA breach, Decision) must emit a domain event.
7. **Audit Compliance:** Every domain event must write a read-only record in the system audit logs.
8. **Real-time Status Sync:** The citizen-visible status must automatically reflect internal workflow state changes.
9. **Simulation Safeguard:** Simulated integration results must be clearly labeled as non-authoritative mockup logs to prevent database poisoning.
10. **Strict Path Execution:** Any attempt to perform invalid workflow status transitions must raise a `WorkflowTransitionException` and log a security alert.
