# ADR 001: Frappe-First Consolidation Strategy

## Status
Approved

## Context
The NileGov project was developed across two distinct codebases:
1. **System A (`govproject-claude-peaceful-dijkstra-TMPp2`):** A React/Vite frontend coupled with an Express/SQLite backend prototype. It includes visual flows, microcopy, checklist guides, and mock integration payloads.
2. **System B (`govproject-main`):** A custom Frappe application structured with Clean Architecture boundaries (Domain, Application, Infrastructure, and Interfaces layers). It includes 16 custom DocTypes, fixtures, workspace layouts, query reports, dashboards, print formats, and a comprehensive test suite of 1,410 tests.

Running a dual-backend architecture (Express/SQLite alongside Frappe) introduces unnecessary complexity, increases hosting resources on Hetzner, duplicates business logic, and splits the data source of truth.

---

## Decision
We will consolidate all operations into the Frappe-native custom app (System B) as the sole runtime and backend.

### Implementation Boundaries
1. **Database Source of Truth:** SQLite is deprecated. MariaDB (or PostgreSQL) managed natively by Frappe Bench is the sole database engine.
2. **Archived Backend:** The Node/Express API service is deprecated. Its operational endpoints will be fully mapped to whitelisted, role-restricted Frappe REST APIs.
3. **Frontend Visual Alignment:** System A's React/Vite client is archived. Its Uganda-themed styling cues, stepper intake wizard flow, and live SLA timers will be ported to custom Frappe Pages, Web Forms, and Desk client scripts.
4. **Clean Architecture Isolation:** The domain and application logic inside `nilegov_stack` will remain independent of the Frappe framework, preserving the ability to port NileGov core code to other Python frameworks in the future.
5. **Privacy & Payment Safeguards:** All identity (NIRA) and tax (URA) checking interfaces will remain in simulated/sandbox mode, enforcing the Data Protection and Privacy Act 2019 and avoiding live credentials in the prototype.

---

## Consequences
* **Single Source of Truth:** Centralized database storage, workflow rules, SLA triggers, and audit logs.
* **Operational Simplicity:** A single, lightweight bench folder setup on Hetzner with standard MariaDB backups and restoration scripts.
* **Privacy & Security:** Native access control via the Frappe Role Permission Manager, guaranteeing strict segregation of duties (e.g., separating Payments Officer and Records Officer).
* **UI Effort:** Visual enhancements (steppers, dashboards, and timers) must be rewritten as custom CSS/HTML layouts and vanilla JS client scripts within the Frappe framework, rather than utilizing React components.
