# Pass 8A-9A: API / Interoperability Readiness Audit and Plan

## Objective

Prepare NileGov Stack for future API and interoperability readiness without claiming live integration with UGHub, NIRA, URA, NITA-U, Pesapal live, or any government registry.

This pass is audit and planning only.

## Current verified state

- Citizen Profile Foundation implemented.
- Consent Records Foundation implemented.
- Evidence & Document Foundation implemented.
- Officer Assignment & Department Queues implemented.
- SLA Rules & Escalation Foundation implemented.
- Notification Events & Simulated Communication Foundation implemented.
- Payments Foundation implemented.
- Pesapal API 3.0 Sandbox Adapter Foundation implemented.
- Service Catalogue & SLA Settings Integration implemented.
- M&E / Reporting Foundation implemented.
- Latest verified test count: 299/299 passing.
- Python compile check passed.
- `.env` is local, ignored and untracked.
- Runtime validation remains deferred to Hetzner.
- Public demo domain prepared: nile-gov-demo.com.

## Absolute honesty rule

There are no live MDA deployments.
There is no live UGHub integration.
There is no live NIRA integration.
There is no live URA integration.
There is no live government registry access.
There is no live payment-provider production integration.

All interoperability work remains prototype-level, simulated or integration-ready only.

## Audit targets

Inspect:

- existing API folders under interfaces/frappe/api;
- existing Frappe whitelisted endpoints;
- existing simulated identity verification gateways;
- existing simulated payment gateway;
- existing Pesapal sandbox adapter;
- existing notification gateway;
- existing reporting snapshot model;
- existing service catalogue model;
- existing audit event and integration simulation log models;
- existing payload validation helpers;
- existing unit tests;
- existing submission documentation.

## Proposed implementation for Pass 8A-9B

Create pure domain/application layer support for:

- IntegrationRequest
- IntegrationResponse
- APIError
- APIEnvelope
- correlation ID generation
- idempotency key generation
- success envelope builder
- error envelope builder
- integration request repository
- safe interoperability payload builders

Payload builders should cover:

- service request payload;
- simulated identity verification payload;
- simulated payment verification payload;
- notification event payload;
- reporting snapshot payload.

## Proposed implementation for Pass 8A-9C

Create and update documentation:

- docs/modules/10_api_interoperability_readiness.md
- docs/submission/07_claims_matrix.md
- docs/submission/13_evidence_index.md
- docs/submission/08_runtime_validation_checklist.md
- walkthrough.md
- task.md

## Files not to touch

- .env
- Pesapal live settings
- runtime deployment files unless documentation-only
- working service request workflow unless a defect is found
- Docker/Hetzner runtime configuration

## Validation

Run after implementation:

.venv/bin/pytest
python3 -m compileall apps/nilegov_stack/nilegov_stack
git status --short
git ls-files .env

Expected:

- all tests pass;
- compile passes;
- `.env` remains untracked;
- no live integration claims introduced;
- no secrets logged.
