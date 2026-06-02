# Service Catalogue & SLA Settings Integration Foundation

This module acts as the central configuration layer, linking government service types to default SLA rules, required document types, fee settings, payment provider configurations, and workflow template rules.

---

## 1. Domain Architecture & Models

The Service Catalogue domain models are defined in `domain/service_catalogue.py`.

### 1.1 ServiceCatalogueItem (Domain Aggregate)
Represents a configured government service template:
*   **service_catalogue_id**: Unique ID (e.g. `SVC-LOST-NID`).
*   **service_name**: Human-readable name.
*   **service_code**: Short code mapping to transactional service types (e.g., `LOST_NATIONAL_ID`).
*   **responsible_mda_placeholder**: The government agency in charge.
*   **service_category**: One of the standard categories (e.g. `Identity Services`, `Citizen Complaints`).
*   **required_documents**: List of required supporting document types.
*   **fee_required**: Boolean stating if a payment is required.
*   **default_fee_amount**: Default fee in currency.
*   **default_currency**: Default currency (e.g. `UGX`).
*   **default_payment_provider**: simulated or Pesapal Sandbox Ready.
*   **default_sla_rule**: Associated SLA rule ID.
*   **workflow_template**: Standard workflow template option.
*   **active_status**: `Active`, `Inactive`, `Demo Only`, or `Retired`.
*   **public_visibility**: `Demo Visible`, `Citizen Hidden`, or `Public Visible`.
*   **disclaimer**: Hardcoded simulation disclaimer.

---

## 2. DocType Schema & Controller

The `NileGov Service Catalogue` DocType provides the database schema for catalogue persistence:
*   **required_documents**: Serialized as a comma-separated string (`Small Text`) in the database, mapped back to a clean list in Python domain objects.
*   **fee_required**: Mapped to boolean values.
*   **active_status** & **workflow_template** & **default_payment_provider**: Selective enums for strict data validation on insertion/update.

### Controller Validations
The controller `nilegov_service_catalogue.py` checks:
*   Name and Code presence.
*   Non-negative fee amounts.
*   Allowed select options.
*   Presence of the disclaimer text: `"Prototype service catalogue only. Not connected to a live government service registry."`.

---

## 3. Repositories & Application Use Cases

### 3.1 Repositories
*   **ServiceCatalogueRepository**: Abstract port definition.
*   **InMemoryServiceCatalogueRepository**: Registry simulation for offline unit testing.
*   **FrappeServiceCatalogueRepository**: Map-and-serialize layer mapping database records to `ServiceCatalogueItem` domain aggregates.

### 3.2 Use Cases
*   **CreateServiceCatalogueItem**: Persists new templates.
*   **UpdateServiceCatalogueItem**: Allows partial update validation of attributes.
*   **ListServices**: Supports querying active, demo, or category items.
*   **ManageServiceStatus**: Transition items between `Active`, `Inactive`, and `Demo Only` status.
*   **RetrieveServiceByCode**: Direct code lookup.
*   **ApplyCatalogueDefaults**: Connects catalogue configuration to incoming request transactions:
    *   Fills `assigned_department` and `queue_name` defaults on `ServiceRequest`.
    *   Fills payment provider, amount, and purpose on `PaymentRecord`.
    *   Validates evidence checklist completeness against submitted document types.

---

## 4. Seeding Demo Records

The patch `patches/seed_demo_records.py` is updated to seed three default templates:
1.  **SVC-LOST-NID** (Active): Configured with `LOST_NATIONAL_ID` code, 50,000 UGX fee, `Simulated` provider, and `Police Letter Placeholder`, `Affidavit Placeholder`, and `Supporting ID Placeholder` as required documents.
2.  **SVC-CITIZEN-COMPLAINT** (Demo Only): Configured for complaining about public services.
3.  **SVC-PERMIT-APPLICATION** (Inactive): Requires EIA and Land documents with a fee of 250,000 UGX.

---

## 5. Verification & Quality Gate

*   **Unit Tests**: `tests/unit/test_service_catalogue.py` asserts all validations, defaults mapping, repository operations, and use cases.
*   **Regression check**: Checked against the complete 289-test test suite.
