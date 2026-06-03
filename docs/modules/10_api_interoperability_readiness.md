# Module 10: API / Interoperability Readiness Foundation

## Purpose

The API / Interoperability Readiness Foundation prepares NileGov Stack for future integration with government systems, service registries, payment providers and inter-agency workflows without claiming live connectivity.

This module defines safe API payload contracts, response envelopes, error envelopes, correlation IDs, idempotency keys, simulated integration requests and integration-ready payload builders.

## Government use case

For a Lost National ID Replacement journey, NileGov may eventually need to exchange structured information with identity, payment, notification and MDA systems.

In this prototype, those exchanges are represented through safe simulated contracts only. No live government registry, NIRA endpoint, UGHub endpoint, URA endpoint, NITA-U infrastructure or production payment system is contacted.

## What has been implemented

The foundation includes:

- `IntegrationRequest`
- `IntegrationResponse`
- `APIError`
- `APIEnvelope`
- correlation ID generation
- idempotency key generation
- success response envelope
- error response envelope
- in-memory integration request repository
- simulated integration result recording
- safe payload builders for:
  - service requests
  - simulated identity verification
  - simulated payment verification
  - notification events
  - reporting snapshots

## API readiness principles

The module follows these principles:

1. **Simulation first**  
   All external integrations are represented as simulated or sandbox-ready contracts.

2. **Data minimisation**  
   Payload builders intentionally exclude raw National ID numbers, payment credentials, card data, mobile money PINs and private contact secrets.

3. **Traceability**  
   Correlation IDs and idempotency keys prepare the system for future audit-safe request tracing.

4. **No live claims**  
   The module does not claim live integration with UGHub, NIRA, URA, NITA-U, Pesapal live or any MDA system.

5. **Runtime separation**  
   Pure domain and application logic can be tested without a Frappe database runtime.

## Response envelope

Successful API-style responses use a standard envelope with:

- `success`
- `correlation_id`
- `data`
- `error`
- `timestamp`
- `disclaimer`

## Error envelope

Error responses use:

- `code`
- `message`
- `details`
- `retryable`
- `correlation_id`

This prepares NileGov for predictable error handling once public endpoints are activated.

## Correlation IDs

Correlation IDs support end-to-end tracing of simulated requests across service request workflows, payment checks, notifications and future MDA integrations.

## Idempotency keys

Idempotency keys prepare NileGov for safe retry handling. This is important for future payment verification, case submission and service update scenarios.

## Simulated interoperability boundaries

The accepted target systems are:

- Simulated NIRA
- Simulated UGHub
- Simulated Payment Provider
- Simulated Notification Gateway
- Simulated MDA System
- Internal NileGov

These names are intentional. They prevent the prototype from implying production connectivity.

## Payload contracts

### Service Request Payload

Includes:

- reference number
- service code
- service name
- citizen profile ID
- location
- status
- assigned queue
- SLA state
- payment status
- evidence summary
- creation timestamp
- disclaimer

### Simulated Identity Verification Payload

Includes:

- service request reference
- citizen profile ID
- consent reference
- verification purpose
- simulated identifier reference
- disclaimer

It does not include a real NIN.

### Simulated Payment Verification Payload

Includes:

- payment record ID
- service request reference
- amount
- currency
- payment purpose
- provider
- provider mode
- simulated transaction reference
- disclaimer

It does not include card numbers, PINs, mobile money credentials or bank credentials.

### Notification Event Payload

Includes:

- notification event ID
- service request reference
- recipient type
- channel
- message type
- delivery status
- disclaimer

It does not expose raw recipient contact secrets.

### Reporting Snapshot Payload

Includes:

- reporting snapshot ID
- reporting period
- total requests
- requests by status
- requests by service
- SLA summary
- payment summary
- notification summary
- workload summary
- disclaimer

## Integration logging

NileGov already includes a `NileGov Integration Simulation Log` DocType. The interoperability foundation can use this pattern during runtime activation to record:

- integration name
- simulation type
- target system
- status
- timestamp
- disclaimer

This pass does not add live logging to a production gateway.

## Security controls

The module supports:

- safe payload minimisation
- simulated target system allow-listing
- status allow-listing
- deterministic error envelopes
- explicit disclaimers
- no secret logging
- no raw credential exposure

## What remains pending

The following remain deferred to Hetzner or another working Linux/Frappe runtime:

- public HTTPS endpoint activation
- browser runtime validation
- Frappe whitelisted API endpoint validation
- UGHub onboarding
- NIRA onboarding
- URA onboarding
- payment callback/IPN runtime validation
- production integration logging
- screenshots and demo recording

## Formal onboarding required

Future live integration will require the relevant formal approvals, including but not limited to:

- MDA participation
- Data Sharing Agreements
- UGHub onboarding
- endpoint provisioning
- production security review
- privacy and consent validation
- payment-provider production approval

## Safe claims

It is safe to say:

- API readiness foundation implemented.
- REST-ready payload contracts implemented.
- Simulated interoperability contracts implemented.
- API envelope and error envelope implemented.
- Correlation ID and idempotency key support implemented.
- Safe payload builders implemented.
- Runtime validation remains pending.

## Claims to avoid

Do not claim:

- connected to UGHub
- connected to NIRA
- connected to URA
- connected to NITA-U
- live registry verification
- production API gateway
- official MDA integration
- real payment clearance
- live government reporting

## Validation

Latest implementation validation before documentation pass:

- `test_interoperability.py`: 14/14 passed.
- Full test suite: 323/323 passed.
- Python compile check passed.
- `.env` remained untracked.

## Required disclaimer

“Prototype interoperability simulation only. No live government system was contacted.”
