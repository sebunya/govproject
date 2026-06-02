# Module: Officer Assignment & Department Queues

## Purpose

The **Officer Assignment & Department Queues** module manages operational routing, workload distribution, and caseworker assignments within the NileGov Stack. It extends the core **Service Request** model to support routing cases through fictional department queues, assigning cases to specific officers or supervisors, and calculating pending case volumes. By providing workload metrics without importing external HR databases, it establishes an audit-safe administrative layer.

---

## Government Use Case

The primary use case demonstrated is the **Lost National ID Replacement** service in Ntinda, Kampala.

### Case Assignment & Supervisor Routing Flow
1. A fictional citizen (e.g. *Demo Citizen A*) submits a replacement request. The case enters the system as `Unassigned` on the **National ID Replacement Desk** queue.
2. The intake coordinator routes the request to a Service Desk Officer (e.g., `officer_demo`), moving the status to `Assigned`.
3. If verification needs deep inspection, the case is assigned to a specialist (e.g., `officer_review`) on the **Verification Desk** queue, with the status updated to `Reassigned`.
4. If a correction is needed, the case can be marked for supervisor review (`supervisor_demo`), moving the status to `Supervisor Review` on the **Supervisor Review Queue**.
5. Once cleared, the supervisor returns the case to the assigned officer, shifting the status back to `Returned to Officer`.
6. Once final decisions are made and collection is logged, the assignment status moves to `Closed` on the **Completed Cases Queue**.

---

## Assignment & Queue Principles

1. **Fictional Caseworkers:** The system uses mock usernames (e.g., `officer_demo`, `supervisor_demo`) to represent roles rather than syncing with active government HR databases.
2. **Workload Transparency:** Operational metrics count cases by status and queue, allowing team leaders to see backlog distributions.
3. **Audit-Trail Accountability:** Reassignment and supervisor escalation actions trigger discrete domain events (e.g., `OfficerReassigned`, `SupervisorReviewRequested`) that register in the immutable database audit trail.
4. **Decoupled Workflow States:** Case assignment states (`Assigned`, `Reassigned`, `Supervisor Review`) track administrative ownership. They run alongside, but do not override, the primary service statuses (`Submitted`, `Under Review`, `Approved`, `Closed`).

---

## Allowed Vocabularies

### Assignment Statuses
* `Unassigned`: Initial state for incoming requests.
* `Assigned`: Active case assigned to a caseworker.
* `Reassigned`: Shifted to a different officer or specialist queue.
* `Supervisor Review`: Escalated to supervisor overview.
* `Returned to Officer`: Cleared by a supervisor and sent back to the caseworker.
* `Closed`: Work completed and archived in completed queues.

### Departments & Desks (Queues)
* **National ID Replacement Desk:** Main intake and administrative queue.
* **Citizen Services Desk:** General inquiry and profile handling desk.
* **Verification Desk:** specialist identity and registry checking queue.
* **Payment Review Desk:** Fee receipt matching queue.
* **Supervisor Review Queue:** Escalated cases requiring supervisor clearance.
* **Completed Cases Queue:** Archived requests that are closed.

---

## Entity Schema & Fields

### NileGov Service Request DocType (Assignment Extensions)

| Fieldname | Fieldtype | Label | Required? | Description / Valid Values |
| :--- | :--- | :--- | :--- | :--- |
| `assigned_officer` | Link | Assigned Officer | No | Links to `User` assigned as casework handler. |
| `assigned_supervisor` | Link | Assigned Supervisor | No | Links to `User` representing supervisor reviewer. |
| `assigned_department` | Select | Assigned Department | No | Select desk name (e.g. `Verification Desk`). |
| `assigned_team` | Data | Assigned Team | No | Team name descriptor. |
| `assigned_at` | Datetime | Assigned At | No | Timestamp of initial assignment. |
| `reassigned_at` | Datetime | Reassigned At | No | Timestamp of the most recent reassignment. |
| `reassignment_reason` | Small Text | Reassignment Reason | No | Officer explanation for case handoff. |
| `supervisor_review_required` | Check | Supervisor Review Required | Yes | Default: 0. Flag indicating active supervisor escalation. |
| `queue_name` | Select | Queue Name | Yes | Approved desks/queues (default: `National ID Replacement Desk`). |
| `assignment_status` | Select | Assignment Status | Yes | Approved assignment statuses (default: `Unassigned`). |

---

## Workflows & Use Cases Supported

* **Assign Officer:** Service (`AssignOfficer`) routing a request to an SDO.
* **Reassign Officer:** Service (`ReassignOfficer`) recording caseworker transfer and reasons.
* **Assign Department/Team:** Service (`AssignDepartmentTeam`) routing requests to specialist desks.
* **Mark Supervisor Review:** Escalates ownership to supervisor review (`MarkSupervisorReview`).
* **Return Case to Officer:** Supervisor returns case back to caseworker (`ReturnCaseToOfficer`).
* **Calculate Workload Metrics:** Service (`CalculateWorkloadMetrics`) compiling unassigned counts, assigned counts, supervisor queues, and workloads.

---

## Testing Summary

Verified by 9 new pytest integration and unit tests (suite total: 182 passing tests):
* **Domain aggregate checks:** Validates creation defaults, status transitions, invalid status handling, and empty note rejection.
* **Use Cases:** Verifies assignments, reassignments with reason, department routing, lists, and workload metrics.
* **Mocks mapping:** Verifies that `FrappeServiceRequestRepository` maps assignment fields and domain events cleanly under mocks.

---

## Deployment & Validation Status

* **Status:** Implemented at code, schema, seed, and test level.
* **Runtime Desk Validation:** Pending deployment to Hetzner or another working Linux/Docker host.
* **Manual Setup Note:** Run `bench --site nilegov.local migrate` on the deployment host to update schema tables and execute the `seed_demo_records` patch.

---

## Claims Registry

### Safe Claims
* Complete domain logic representing queues and workload counters.
* Immutable audit trails for reassignments and escalations.
* Idempotent seeding patch written and registered in `patches.txt`.

### Claims to Avoid
* Live sync with government HRMIS (Human Resource Management Information System).
* Performance appraisals, shift logs, and payroll calculations.
* Automated load balancing or AI-based queue routing.
