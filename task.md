# Pass 8A-9A Task List: API / Interoperability Readiness Audit and Plan

## Audit

- [x] Inspect interfaces/frappe/api
- [x] Inspect existing whitelisted endpoints
- [x] Inspect simulated identity gateway
- [x] Inspect simulated payment gateway
- [x] Inspect Pesapal sandbox adapter
- [x] Inspect notification gateway
- [x] Inspect reporting snapshot model
- [x] Inspect service catalogue model
- [x] Inspect audit event and integration simulation logs
- [x] Inspect existing tests
- [x] Inspect submission documentation

## Audit Findings

- Existing `interfaces/frappe/api` package is present but minimal.
- Existing whitelisted Desk actions are concentrated in the `NileGov Service Request` DocType controller.
- Simulated identity, payment and notification gateways are already implemented.
- Pesapal API 3.0 sandbox adapter is implemented and must remain sandbox-first.
- Reporting Snapshot and Service Catalogue foundations are implemented.
- `NileGov Integration Simulation Log` already exists and can support future runtime logging.
- No complete API envelope, error envelope, idempotency key or correlation ID layer exists yet.
- No dedicated interoperability domain model exists yet.
- No safe cross-module payload builder exists yet.
- Runtime validation remains deferred to Hetzner.

## Planning

- [x] Define Pass 8A-9A objective
- [x] Define honesty boundaries
- [x] Define files not to touch
- [x] Define proposed Pass 8A-9B scope
- [x] Define proposed Pass 8A-9C scope
- [x] Define validation gates

## Safety

- [x] Confirm `.env` remains untracked
- [x] Confirm no secrets appear in git diff
- [x] Confirm no live payment mode is activated
- [x] Confirm no runtime validation is attempted

## Next pass

- [x] Proceed to Pass 8A-9B only after audit findings are reviewed
