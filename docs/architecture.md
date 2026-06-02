# NileGov Stack System Architecture

This document defines the architectural blueprint and directory structure for the **NileGov Stack**, a sovereign service delivery and workflow accountability platform. 

The architecture is built on the principles of **Domain-Driven Design (DDD)**, **Clean Architecture**, and **Ports and Adapters (Hexagonal Architecture)**. It strictly isolates the core business logic from database systems, HTTP clients, and application frameworks (including the Frappe Framework).

---

## Architectural Layers

NileGov Stack is partitioned into four distinct layers. Dependencies flow one-way: **inward toward the Domain Layer**.

```text
       ┌────────────────────────────────────────────────────────┐
       │                       INTERFACES                       │
       │     (Frappe Doctype Controllers, Pages, Web APIs)      │
       └───────────────────────────┬────────────────────────────┘
                                   │ (Uses)
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                      APPLICATION                       │
       │    (Use Cases, e.g., SubmitRequest, AssignOfficer)     │
       └─────────────────────┬───────────┬──────────────────────┘
                             │           │ (Uses/Implements)
                    (Calls)  │           ▼
                             │     ┌────────────────────────────┐
                             │     │       INFRASTRUCTURE       │
                             │     │ (Repositores, Gateways,    │
                             │     │  SMTP, HTTP Adapters)      │
                             │     └─────────────┬──────────────┘
                             ▼                   │ (Implements)
       ┌─────────────────────────────────────────▼──────────────┐
       │                         DOMAIN                         │
       │   (Entities, Value Objects, Domain Events, Rules)      │
       └────────────────────────────────────────────────────────┘
```

### 1. Domain Layer (`domain/`)
The core domain model, representing the business entities, domain rules, events, and exceptions of Uganda's service request and accountability workflow.
* **Rules of Engagement:**
  * **No Frappe Framework imports.**
  * **No database driver or API imports** (e.g., no `frappe.db`).
  * **No HTTP, SMTP, or socket client imports.**
  * **Purely unit-testable** in standard Python without a database connection or running web server.
* **Core Concepts:** Entities (e.g., `ServiceRequest`), Value Objects (e.g., `NIN`), Domain Events (e.g., `RequestEscalated`), Exceptions.

### 2. Application Layer (`application/`)
Implements specific government use cases by coordinating domain objects and infrastructure ports.
* **Rules of Engagement:**
  * Orchestrates the execution of domain logic (e.g., loading an entity, calling a domain state change, saving it).
  * Accesses external systems (database, notifications, integrations) *only* through abstract interfaces (Ports/Fakes).
  * Exposes Use Cases as clean application services.
* **Core Concepts (Planned Use-Case Services for Pass 4):**
  * `SubmitLostNationalIDRequest` (Intake request creation)
  * `CaptureConsent` (Citizen legal signature validation)
  * `RunSimulatedIdentityCheck` (Mocks query verification triggers)
  * `AssignCase` (Case officer routing rules)
  * `StartOfficerReview` (Review status start and SLA setup)
  * `RequestMoreInformation` (Query triggers and pause actions)
  * `EscalateCase` (Automatics breach handling)
  * `SupervisorReview` (Manager manual overrides)
  * `CloseCase` (Resolution checks and archiving)
  * `TrackRequest` (Public status tracking checker)
  * `CalculateDashboardMetrics` (Leadership aggregate analytics compiles)
  * *Note: In Pass 1, these use-case services are established as structurally validated Python skeletons. Integration with database models and direct persistence repository operations will be completed in Pass 4.*

### 3. Infrastructure Layer (`infrastructure/`)
Contains concrete implementations of the abstract ports defined in the domain and application layers.
* **Rules of Engagement:**
  * Implements database repositories using Frappe DB APIs.
  * Connects to external systems (simulated SMS, SMTP, file systems).
  * Implements the simulated identity verification gateways.
* **Core Concepts:** Repositories, integrations, local storage, notification gateways.

### 4. Interfaces Layer (`interfaces/`)
The entry point into the system. Translates user actions, cron triggers, and web requests into application services.
* **Rules of Engagement:**
  * Houses Frappe DocType Controllers.
  * Custom desks, dashboards, and pages.
  * REST API handlers.
  * Controllers are kept thin; they parse inputs, call the appropriate application use case, and return results.
* **Core Concepts:** Doctype controller hooks, page routing, Frappe whitelist APIs.

---

## Bounded Contexts

NileGov Stack maintains strict boundaries between modules to manage complexity:
1. **Citizen Service Intake:** Manages citizen identity validation (NIN), portal access, request drafts, and submission.
2. **Case Management:** Manages officer queues, reviews, workflow transitions, and state changes.
3. **SLA and Escalation:** Monitors processing limits and automatically routes stalled requests to supervisors.
4. **Evidence Management:** Controls citizen attachments, documentation check status, and secure storage access.
5. **Integration Simulation:** Manages simulated mock endpoints for NIRA, URA, and UGHub.
6. **Notifications:** Handles multi-channel status messaging (simulated SMS, email).
7. **Audit and Compliance Support:** Tracks historical logs, changes, and verification hashes.
8. **Monitoring and Reporting:** Aggregates accountability performance indicators for leadership dashboards.

---

## ERP as a Shared Enterprise Services Layer

A key architectural rule is that **ERP is a shared services infrastructure**, not the product story itself.
* **User and Desk Presentation:** All user-facing portals, desk screens, dashboards, and document headings are styled and branded as **NileGov Service Experience** or **NileGov Case and Workflow Operations**.
* **Enterprise Back-End:** Frappe and ERPNext frameworks operate under the hood to handle database transactions, background workers, email queues, and basic user access control.
* **Decoupling Strategy:** By placing the domain and application directories at the top level of the custom app and enforcing ports and adapters, NileGov can be moved off the Frappe Framework onto a separate web framework (like FastAPI or Django) or to microservices without changing a single line of business logic.
