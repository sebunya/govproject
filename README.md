# NileGov Stack

NileGov Stack is a Uganda-built service delivery and case-management workflow accountability platform designed for Government Ministries, Departments, and Agencies (MDAs). It provides a structured framework to receive, assign, track, resolve, and audit citizen service requests.

---

## Technical Auditing Disclaimer

> [!IMPORTANT]
> **Prototype Deployment & Integration Notice:**
> 1. **Mocks & Simulations Only:** All external government database integrations (NIRA registry lookup, URA tax validations, UGHub message publishing) in this repository are **simulated models only**. There is no live Government network connection. Actual production interfaces require formal data sharing agreements, security reviews, and institutional onboarding.
> 2. **Single-Node VPS Hosting:** The Hetzner deployment package included in this repository is an early-stage deployment draft intended for prototype demonstrations. Sovereign production systems for public agencies must run on approved hosting infrastructures with full security auditing, high availability clustering, and failover disaster recovery policies.

---

## End-to-End Workflow Demonstration

NileGov Stack models the following service request lifecycle:
1. **Citizen Request:** Citizen submits an application draft (e.g. Lost National ID replacement) with attachments.
2. **Consent Capture:** Citizen signs a legal data-sharing authorization check.
3. **Simulated Registry Check:** System invokes a mock NIRA gateway lookup.
4. **Queue Allocation:** System assigns the verified request to the least-busy Case Officer.
5. **Desk Review:** Case Officer starts the desk evaluation, triggering an SLA countdown timer.
6. **Supervisor Review / Escalation:** Overdue cases automatically escalate to the supervisor dashboard.
7. **Resolution Audit Trail:** State transitions are committed to a secure, append-only compliance log.
8. **Dashboard Monitoring:** Management monitors throughput and SLA compliance on a read-only statistics dashboard.

---

## Directory Structure

```text
Nile_Gov/
  ├── apps/                  # Custom Frappe App code
  │   └── nilegov_stack/
  │       └── nilegov_stack/
  │           ├── domain/    # Decoupled Pure Python entities & rules
  │           ├── application/# Use-case services & abstract ports
  │           ├── infrastructure/# DB repositories, notification & mock adapters
  │           ├── interfaces/ # Frappe controller overrides, API pages
  │           └── tests/      # 5-tier testing suite
  ├── docs/                  # Architecture, specifications, and disclaimers
  ├── deployment/            # Single-node Hetzner Compose configs & setup scripts
  ├── pytest.ini             # Pytest paths configuration
  ├── implementation_plan.md # Release blueprint tracking
  ├── task.md                # Task verification checklist
  └── walkthrough.md         # Pass verification walkthrough logs
```

---

## Running the Verification Suite

Unit tests, use case validations, and automated static architecture fitness checks are run using `pytest` inside the local virtual environment:

```bash
# Create local virtual environment and install pytest
python3 -m venv .venv
source .venv/bin/activate
pip install pytest

# Run all test suites
pytest
```
*Tests can be executed in isolation on any machine without needing a running database or Frappe Bench environment.*
