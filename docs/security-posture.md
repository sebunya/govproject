# NileGov Stack Security & Branding Posture

This document outlines the **Role-Based Access Control (RBAC)** mappings, permission hierarchies, secure file validation policies, and product branding constraints for the **NileGov Stack**.

---

## Branding Foundation & Terminology

To prevent institutional confusion, NileGov Stack enforces a strict branding and language model.

### Branded Attributes
* **Product Branded Name:** NileGov Stack
* **Corporate Owner/Creator:** Digi-Verse Uganda Limited
* **Visual Presentation:** Gunicorn endpoints and interfaces must use customized NileGov CSS/HTML wrappers. Framework-level titles (Frappe/ERPNext) are restricted to developer configuration consoles and technical logs.

### Vocabulary Matrix
| Prohibited Term | Approved Branded Term | Rationale |
| :--- | :--- | :--- |
| NIRA Officer / Clerk | **Registry Liaison Officer** | Avoids claiming direct sovereign NIRA employment. |
| Live NIRA Connection | **Simulated Identity Check** | Honestly reflects mock/sandbox integrations. |
| ERP User / Desk User | **NileGov Operations Desk** | Highlights specialized domain workflows. |
| Ticket / Customer Issue | **Service Request / Case** | Aligns with standard public sector case management. |

---

## Role-Based Access Control (RBAC) Mappings

The following roles govern NileGov Stack workflows and will be provisioned via Frappe Custom Role Fixtures in Pass 2:

### 1. Citizen
* **Scope:** Individual applicants requesting public services (e.g. Lost ID replacement).
* **Permissions:**
  * Can create own request.
  * Can view own request.
  * Cannot view other citizens' requests (enforced via database row-level permissions).
  * Cannot access internal workspaces.

### 2. Service Desk Officer (Case Officer)
* **Scope:** Operational agency staff processing citizen requests.
* **Permissions:**
  * Can view assigned cases.
  * Can add case notes.
  * Can request more information (transitioning case to user-update status).
  * Can escalate (routing to supervisor for SLA breach or exception handling).
  * Cannot view all cases unless explicitly granted access.
  * Forbidden: Cannot access raw integration simulation logs, modify Service Types, or write to closed/escalated files.

### 3. Registry Liaison Officer
* **Scope:** Liaison desk reviewing NIRA registry simulation outputs.
* **Permissions:**
  * Can view verified requests.
  * Can trigger simulated identity checks.

### 4. Supervisor
* **Scope:** Case managers resolving processing breaches or escalations.
* **Permissions:**
  * Can view escalated cases.
  * Can view team workload.
  * Can review overdue cases.
  * Can reassign cases and override SLA thresholds.

### 5. MDA Leadership
* **Scope:** Executive monitors tracking agency response statistics.
* **Permissions:**
  * Dashboard and aggregate reporting only.
  * Read-only access (cannot edit case files, database details, or records).

### 6. MDA Administrator
* **Scope:** Local agency managers configuring service structures.
* **Permissions:**
  * Can configure service types, SLA rules, workflow metadata, and roles.

### 7. System Administrator
* **Scope:** Technical administration only.
* **Permissions:**
  * Technical administration only (monitoring infrastructure, logs, database health).
  * Forbidden: Cannot bypass audit hashes or modify case resolution flags directly without generating signed compliance events.

---

## Permissions Matrix (Planned for Pass 2)

| DocType / Entity | Citizen | Service Desk Officer | Supervisor | MDA Leadership | MDA Admin |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Citizen Profile** | Read (Own) | Read (Assigned) | Read | Read | Read/Write |
| **Service Request** | Read/Write (Own)| Read/Write (Assigned)| Read/Write | Read | Read/Write |
| **Consent Record** | Read (Own) | Read (Assigned) | Read | Read | Read |
| **Evidence Document**| Read/Write (Own)| Read (Assigned) | Read | Forbidden | Read |
| **Simulated Identity**| Read (Own) | Read (Assigned) | Read | Read | Read |
| **Case Note** | Read (Visible) | Read/Write (Assigned)| Read/Write | Read | Read |
| **SLA Rule / Event** | Forbidden | Read | Read/Write | Read | Read/Write |
| **Audit Event** | Forbidden | Read (Assigned) | Read | Read | Read |

---

## Technical Permission Implementation Warning (Pass 2)

> [!WARNING]
> **Row-Level Access Constraints:**
> Basic Frappe role permissions (DocPerms) alone are **not** sufficient to enforce NileGov's security posture. While DocPerms restrict general access by role, we must enforce that:
> 1. A **Citizen** cannot read or write another citizen's `Service Request` or `Evidence Document` record.
> 2. A **Service Desk Officer** can only view requests assigned to them (or in the active pool pending review).
>
> Therefore, in Pass 2, we must implement **row-level permissions** using:
> * Frappe User Permission filters (mapping citizens to their specific profiles).
> * Permission query conditions in hooks (`permission_query_conditions` in `hooks.py`).
> * Controller-level verification methods (`has_permission` hooks inside DocType controller classes).
