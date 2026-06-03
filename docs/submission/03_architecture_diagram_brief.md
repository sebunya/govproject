# NileGov Stack Architecture Diagram Brief

This document provides a block-by-block structural description of the NileGov Stack system architecture. It serves as a visual guide and layout instruction brief for a graphic designer or systems architect to convert into a visual vector diagram.

---

## 1. Diagram Layout and Layering

The diagram should be structured in **four horizontal layers** (Top to Bottom), demonstrating the user interactions, the logic separation, the database structure, and the integration/deployment layer.

```text
+-----------------------------------------------------------------------------------+
| 1. USER INTERACTION LAYER (Citizen Portal, Officer Desk, Supervisor views)        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 2. FRAPPE FRAMEWORK LAYER (Gunicorn, REST API routing, Client Script Handlers)    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 3. DECOUPLED LOGIC LAYER (Pure Python domain aggregates, repositories, gateways)  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 4. PERSISTENCE & DEPLOYMENT LAYER (MariaDB, Docker containers, private cloud)     |
+-----------------------------------------------------------------------------------+
```

---

## 2. Block Component Details

### Layer 1: User Interaction Layer
* **Block 1A: Citizen Profile Node**
  - *Description:* Web browser interface. Citizens register profiles, submit replacement requests, and upload evidence.
  - *Icon Idea:* Laptop/mobile phone icon with a citizen silhouette.
* **Block 1B: Service Desk Officer Node**
  - *Description:* Frappe Desk view. Officers review intake registers, examine SLA metrics, and trigger verifications.
  - *Icon Idea:* Desktop monitor with a clipboard.
* **Block 1C: Supervisor Node**
  - *Description:* Desk Escalation panel. Supervises overdue SLA cases and processes escalated service requests.
  - *Icon Idea:* Silhouette of a team leader with a shield.

### Layer 2: Frappe Framework Layer
* **Block 2A: Desk UI Workspace Controller**
  - *Description:* Custom JSON config dashboard rendering filtered queues.
* **Block 2B: REST API Router**
  - *Description:* Handles client-side Javascript form button triggers mapping to backend controller methods.
* **Block 2C: Row-Level Permissions Engine**
  - *Description:* Restricts data visibility by mapping Python query conditions.

### Layer 3: Decoupled Logic Layer
* **Block 3A: Pure Domain Model (The Core)**
  - *Description:* Pure-Python state machine checking status transitions, value object constraints (e.g., NIN validations), and publishing domain events.
  - *Visual style:* Centered, highlighted boundary with an "Inner Core - Pure Logic Only" border.
* **Block 3B: Frappe Repository Adapter**
  - *Description:* Coordinates domain saves and queries with Frappe database methods.
* **Block 3C: Simulated Integration Gateways**
  - *Description:* Pluggable mock gateways (Simulated NIRA Verification, Simulated Payment Verification) logging transaction payloads with simulation disclaimers.

### Layer 4: Persistence & Deployment Layer
* **Block 4A: MariaDB Database**
  - *Description:* Relational storage housing custom tables.
  - *Icon:* Cylinder database stack.
* **Block 4B: Docker Compose Stack**
  - *Description:* Container orchestration nodes (backend Gunicorn, Redis queue, database, background worker).
* **Block 4C: Private Cloud / On-Premise Layer**
  - *Description:* Safe, sovereign deployment target (Ministry or National Data Center).

---

## 3. Directional Connection Arrows (Data Flow)

1. **Intake Flow:** *Citizen Node* → sends HTTP POST request → *REST API Router* → calls repository adapter → inserts record in *MariaDB*.
2. **Review Flow:** *Officer Node* → accesses *Desk Workspace* → triggers custom JS action → queries *Simulated NIRA Verification Gateway* → updates status to `Payment Pending` in *Domain Model*.
3. **Audit Logging Flow:** State change events in *Domain Model* → trigger repository mapping → insert immutable logs into *MariaDB* audit table.
4. **Future Integration Points:** Draw dashed connection lines from *Simulated Gateways* to external clouds labelled: *"Future Integration Target (e.g. UGHub registry bus, live payment gateway)"*.
