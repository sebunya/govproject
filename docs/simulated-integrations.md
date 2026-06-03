# NileGov Stack Simulated Integrations

This document outlines the design and payloads of mock integration gateways used to simulate external Government registries.

---

## Simulation Disclaimer

> [!WARNING]
> **Prototype Simulation Boundary:**
> “Prototype simulation only. No live Government registry access.”
> All external system endpoints are fully mocked inside the `infrastructure/integrations/` sub-package. Production integrations would require formal onboarding, security audits, whitelisting, and Data Sharing Agreements with NIRA, URA, and the Ministry of ICT & National Guidance (UGHub).

---

## Simulated Gateways

### 1. National Identification & Registration Authority (NIRA)
* **Objective:** Simulates checking the National Identification Number (NIN) validity.
* **Interface Port:** `IdentityVerificationGateway`
* **Trigger:** Capturing citizen consent automatically requests validation.
* **Simulation Behavior:**
  * If the NIN matches specific test profiles (e.g. `CF900000000000` or `CM800000000000`), returns a success response.
  * If a random NIN is entered, parses the character format. If format matches 14 alphanumeric characters, returns a success simulation with a generated mock name. If format is invalid, returns a fail result.
* **Mock Response Payload:**
  ```json
  {
    "success": true,
    "transaction_id": "SIM-NIRA-2026-99283",
    "nin": "CF900000000000",
    "first_name": "Robert",
    "last_name": "Sebunya",
    "dob": "1990-05-12",
    "gender": "Male",
    "message": "NIRA Simulated Identity Verified"
  }
  ```

### 2. Uganda Revenue Authority (URA)
* **Objective:** Simulates validation of tax compliance status (TIN) for specific service requests requiring tax confirmation.
* **Simulation Behavior:**
  * Checks if the TIN format is 10 digits.
  * Returns compliance flags based on mock lists.
* **Mock Response Payload:**
  ```json
  {
    "success": true,
    "transaction_id": "SIM-URA-2026-10293",
    "tin": "1002938475",
    "taxpayer_name": "Digi-Verse Uganda Limited",
    "compliance_status": "Compliant",
    "message": "TIN verification simulation successful"
  }
  ```

### 3. UGHub (Uganda Government Integration Service Bus)
* **Objective:** Simulates publishing status change events to the central integration bus for inter-agency synchronization.
* **Trigger:** Major state transitions (e.g. `Assigned to Officer`, `Closed`) publish outbound message formats.
* **Simulation Behavior:**
  * Logs the outbound JSON to `NileGov Integration Simulation Log` in the database.
* **Mock Request Payload:**
  ```json
  {
    "event_type": "nilegov.service_request.status_changed",
    "timestamp": "2026-06-01T22:48:00Z",
    "payload": {
      "reference_no": "NLG-REF-10029",
      "status": "Assigned to Officer",
      "agency": "Ministry of Internal Affairs"
    }
  }
  ```

---

## Integration Logging Schema

All simulated external API requests write logs to the database using `Integration Simulation Log` DocType:
* `name` (ID): Unique sequence transaction (`SIM-LOG-XXXXXX`).
* `timestamp` (Datetime): Execution time.
* `service_request` (Link): Associated case.
* `gateway_name` (Data): Target identifier (`NIRA`, `URA`, `UGHub`).
* `request_payload` (Code): Output parameters sent.
* `response_payload` (Code): Mock input parameters received.
* `success` (Check): Success boolean flag.
