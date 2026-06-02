# Monitoring & Evaluation (M&E) Reporting Foundation

The M&E / Reporting Foundation compiles deterministic performance indicators across service requests, catalog configurations, payment receipts, uploaded evidence documents, and notifications. It provides daily/periodic snapshots representing the state of the service delivery pipeline without loading heavy raw database joins at runtime.

> [!NOTE]
> **Pass 11B-1 complete.** `NileGov Reporting Snapshot` DocType JSON, controller, and `__init__.py` are now present in `nilegov_stack/doctype/nilegov_reporting_snapshot/`. M&E Viewer and System Auditor have read-only permission rows. Runtime Desk persistence remains deferred to Hetzner/Frappe bench.

---

## 1. Domain Architecture & Models

The M&E domain models are defined in `domain/reporting_snapshot.py`.

### 1.1 ReportingSnapshot (Domain Aggregate Root)
A read-only compiled performance state tracking:
*   **reporting_snapshot_id**: Unique identifier (e.g., `SNAP-2026-06-02-001`).
*   **snapshot_name**: Descriptive title (e.g., `Daily Performance Snapshot`).
*   **reporting_period_start** / **reporting_period_end**: UNIX timestamps defining the dataset time boundaries.
*   **generated_at**: Generation timestamp.
*   **generated_by**: The officer or system process that triggered compilation.
*   **source_dataset**: Description of the underlying source data (e.g. `Seeded Fictional Demo Data`).
*   **total_requests**: Overall count of service requests in the dataset.
*   **total_services**: Overall count of service catalogue items.
*   **active_services** & **demo_services**: Counts of active/demo catalog options.
*   **requests_by_status**: Dynamic dictionary mapping statuses (e.g., `Under Review`, `Payment Pending`) to counts.
*   **requests_by_service**: Dynamic dictionary mapping service codes (e.g. `LOST_NATIONAL_ID`) to counts.
*   **requests_by_queue**: Queue-level workload distribution.
*   **requests_by_location**: Regional demand breakdown.
*   **within_sla_count**, **at_risk_count**, **overdue_count**, **escalated_count**: Consolidated SLA monitoring metrics.
*   **evidence_complete_count**, **evidence_incomplete_count**, **evidence_rejected_count**, **evidence_requiring_replacement_count**: Compliance and document verification metrics.
*   **payment_pending_count**, **payment_verified_count**, **payment_failed_count**: Payment volume metrics.
*   **notification_draft_count**, **notification_queued_count**, **notification_simulated_sent_count**, **notification_failed_count**, **notification_cancelled_count**, **notification_not_required_count**: Communication status counts.
*   **officer_workload_summary**: Mapping from assigned officers to case counts.
*   **payment_value_summary**: Mapping of accumulated verified simulated payment value.
*   **disclaimer**: Hardcoded simulation disclaimer to prevent misrepresenting simulated metrics as official statistics.

---

## 2. DocType Schema & Controller

The `NileGov Reporting Snapshot` DocType (Pass 11B-1) provides the Frappe-native schema layer.

### 2.1 Files created in Pass 11B-1
- `nilegov_stack/doctype/nilegov_reporting_snapshot/nilegov_reporting_snapshot.json` — 40-field schema
- `nilegov_stack/doctype/nilegov_reporting_snapshot/nilegov_reporting_snapshot.py` — controller
- `nilegov_stack/doctype/nilegov_reporting_snapshot/__init__.py`

### 2.2 DocType fields
- **Core identity**: `reporting_snapshot_id` (autoname), `snapshot_name` (required), `generated_at` (Datetime), `generated_by`, `source_dataset`
- **Period**: `reporting_period_start`, `reporting_period_end` (Date)
- **Executive metrics**: `total_requests`, `total_services`, `active_services`, `demo_services` (all Int)
- **Summaries**: `requests_by_status`, `requests_by_service`, `requests_by_queue`, `requests_by_location` (Code/JSON)
- **SLA**: `within_sla_count`, `at_risk_count`, `overdue_count`, `escalated_count` (Int)
- **Evidence**: `evidence_complete_count`, `evidence_incomplete_count` (Int)
- **Payment**: `payment_pending_count`, `payment_verified_count`, `payment_failed_count` (Int), `payment_value_summary` (Code/JSON)
- **Notifications**: `notification_queued_count`, `notification_simulated_sent_count`, `notification_failed_count` (Int)
- **Workload**: `officer_workload_summary` (Code/JSON)
- **Governance**: `disclaimer` (Small Text, required)

### 2.3 Controller Validations
The controller in `nilegov_reporting_snapshot.py` enforces:
*   Presence of `snapshot_name`.
*   Disclaimer is always set to the required prototype text (defaulted if blank, reset if altered).
*   Forbidden live-integration keywords are blocked in user-editable text fields.

### 2.4 Permission model
| Role | Access |
|---|---|
| NileGov M&E Viewer | Read, Export, Print, Report |
| NileGov SLA Supervisor | Read, Print |
| NileGov MDA Admin | Read, Print |
| NileGov System Auditor | Read, Export, Print, Report |
| NileGov System Manager | Full |
| System Manager | Full |
| Ordinary operational roles | No access |

---

## 3. Repositories & Use Cases

### 3.1 Repositories
*   **ReportingSnapshotRepository**: Abstract port definition.
*   **InMemoryReportingSnapshotRepository**: Volatile repository for unit test isolation.
*   **FrappeReportingSnapshotRepository**: Database integration mapping JSON strings to dict properties. Now aligned to the `NileGov Reporting Snapshot` DocType created in Pass 11B-1.

### 3.2 Use Cases
*   **GenerateReportingSnapshot**:
    1. Gathers all requests, catalog configurations, payments, and notifications from their repositories.
    2. Gathers evidence documents per service request by querying `get_by_service_request(req_id)`.
    3. Runs deterministic aggregates mapping counts and lists.
    4. Computes evidence completeness per request by verifying against required document types defined in the catalog item.
    5. Saves the compiled snapshot to the repository and returns it.

---

## 4. Seeding Prototype Snapshots

The patch `patches/seed_demo_records.py` seeds 4 distinct snapshots:
1.  `SNAP-DAILY-SUMMARY`: Baseline summary of general pipeline activities.
2.  `SNAP-SERVICE-PERFORMANCE`: Specific tracking of `LOST_NATIONAL_ID` and SLA performance.
3.  `SNAP-SLA-BACKLOG`: Focuses on breached/overdue queue backlogs.
4.  `SNAP-PAYMENTS-NOTIFICATIONS`: Aggregates financial volume and citizen communications.

---

## 5. Fictional Disclaimer & Limitations

> [!WARNING]
> All metrics and reporting dashboards are generated from fictional seed data. No live government performance statistics, financial values, or NIRA/NileGov service metrics are computed.

---

## 6. Verification

*   **Unit Tests**: `tests/unit/test_reporting_snapshot.py` verifies domain model validations and aggregate logic.
*   **DocType Tests (Pass 11B-1)**: `tests/unit/test_reporting_snapshot_doctype.py` verifies DocType JSON structure, all required fields, disclaimer text, permission rows (14 test classes).
*   **Role Alignment Tests (Pass 11B-2)**: `tests/permissions/test_role_alignment.py` verifies NileGov Reporting Snapshot has at least one NileGov-prefixed role and no Guest access.
*   **Compliance check**: Full suite 668/668 passed.
