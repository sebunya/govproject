# Module: Payments Foundation & Simulated Government Fee Workflow

## Purpose

The **Payments Foundation & Simulated Government Fee Workflow** module manages simulated government fee tracking, receipt-readiness, and payment verification within the NileGov Stack. It provides a trace log representing mock payment collection, receipt generation, and transaction reconciliation. 

To maintain strict security and sandbox isolation, the module does not connect to live banks, mobile money providers, card networks, or tax systems. It is a simulation layer designed to verify workflow integration and consent rules during evaluator dry-runs.

---

## Government Use Case

The primary use case is fee tracking during the **Lost National ID Replacement** service:

1. **Payment Pending:** When a citizen's identity is verified, the case moves to `Payment Pending`. A draft payment record is initialized for the replacement fee (UGX 15,000 or UGX 50,000 depending on service constraints).
2. **Citizen Pays:** The citizen submits a simulated payment. A transaction reference is assigned (e.g. `SIM-PAY-NIRA-2026-0004`), and the payment record status moves to `Submitted`.
3. **Simulated Verification:** The officer clicks **Trigger Simulated Payment Verification** in the Desk interface. The system runs a privacy consent check. If consent is active, the simulated payment gateway verifies the transaction, setting the payment status to `Verified` and the service request workflow to `Payment Verified`.
4. **Receipt Generation:** Once verified, a simulated receipt reference (e.g. `SIM-RECEIPT-2026-0006`) is issued, and status transitions to `Simulated Receipt Generated`.
5. **Reconciliation:** Background logs trace transaction reconciliation status (`Reconciled`, `Mismatch`) to ensure auditing compliance.

---

## Simulated Payment Principles

1. **No Financial Movement:** The module does not process real money, collect bank account details, credit card numbers, or mobile money credentials.
2. **Mandatory Disclaimer:** Every record preserves the disclaimer: *"Prototype simulation only. No live payment was processed."*
3. **Soft Consent Verification:** If a citizen withdraws or does not grant consent for `Simulated Payment Verification`, the gateway check returns `Requires Review` or `Pending Verification` instead of verified. The primary workflow is not hard-blocked, allowing administrative override.
4. **Decoupled Reconciliation:** Audit reconciliation states run alongside payment statuses to prepare the codebase for future bank statement matching integrations.

---

## Allowed Vocabularies

### Payment Purposes
* `National ID Replacement Fee`: Replacement fee for a lost card.
* `Service Processing Fee`: Standard administrative service charge.
* `Document Replacement Fee`: Administrative charge for secondary documents.
* `Other Government Service Fee`: Miscellaneous fee category.
* `Not Applicable`: Default for free government services.

### Payment Channels
* `Simulated Mobile Money`: Mock cellular wallet payments (MTN/Airtel).
* `Simulated Card`: Mock credit or debit card checkouts (Visa/Mastercard).
* `Simulated Bank`: Mock direct bank transfer clearing.
* `Simulated Cash Office`: Cash paid directly at a government center desk.
* `Not Applicable`: Case where no channel is used.

### Payment Statuses
* `Not Required`: Default for services with zero fees.
* `Pending`: Opened draft record awaiting submission of payment details.
* `Submitted`: Payment reference has been entered and is awaiting gateway confirmation.
* `Verified`: Verification confirmed and matched by the simulated gateway.
* `Failed`: Transaction declined or cancelled by mock provider.
* `Reversed`: Charge reversed or refunded.
* `Cancelled`: Recalled before clearing.

### Verification Statuses
* `Not Checked`: Initial state for draft or unpaid entries.
* `Pending Verification`: Queued for gateway confirmation.
* `Simulated Verified`: Successfully verified by simulated check.
* `Simulated Failed`: Failed validation checks.
* `Requires Review`: Consent withdrawn/expired, or transaction matching mismatch.
* `Not Applicable`: Verification not required.

### Receipt Statuses
* `Not Required`: Free services.
* `Receipt Pending`: Verification complete; receipt not yet generated.
* `Receipt Ready`: Layout formatted and receipt-ready.
* `Simulated Receipt Generated`: Mock receipt reference generated and saved.
* `Cancelled`: Record cancelled.

### Reconciliation Statuses
* `Not Required`: Zero fee services.
* `Pending Reconciliation`: Logged payment awaiting bank statement match.
* `Reconciled`: Matched and closed.
* `Mismatch`: Discrepancy in amount or reference.
* `Requires Review`: Flagged for accountant review.

---

## Entity Schema & Fields

### NileGov Payment Record DocType
| Fieldname | Fieldtype | Label | Required? | Description / Valid Values |
| :--- | :--- | :--- | :--- | :--- |
| `payment_record_id` | Data | Payment Record ID | Yes | Unique ID (autoname: `field:payment_record_id`). |
| `service_request` | Link | Service Request | Yes | Links to `NileGov Service Request`. |
| `citizen_profile` | Link | Citizen Profile | No | Links to `NileGov Citizen Profile`. |
| `consent_record` | Link | Consent Record | No | Links to `NileGov Consent Record`. |
| `amount` | Currency | Amount | Yes | The payment amount. |
| `currency` | Data | Currency | Yes | Default: `UGX`. |
| `payment_purpose` | Select | Payment Purpose | Yes | National ID Replacement Fee, Service Processing Fee, Document Replacement Fee, Other Government Service Fee, Not Applicable. |
| `payment_channel` | Select | Payment Channel | Yes | Simulated Mobile Money, Simulated Card, Simulated Bank, Simulated Cash Office, Not Applicable. |
| `payment_status` | Select | Payment Status | Yes | Not Required, Pending, Submitted, Verified, Failed, Reversed, Cancelled. |
| `simulated_transaction_reference` | Data | Simulated Transaction Reference | No | Transaction reference code. |
| `verification_status` | Select | Verification Status | Yes | Not Checked, Pending Verification, Simulated Verified, Simulated Failed, Requires Review, Not Applicable. |
| `verification_timestamp` | Datetime | Verification Timestamp | No | Verification timestamp. |
| `verified_by` | Data | Verified By | No | Officer username. |
| `receipt_status` | Select | Receipt Status | Yes | Not Required, Receipt Pending, Receipt Ready, Simulated Receipt Generated, Cancelled. |
| `receipt_reference` | Data | Receipt Reference | No | Receipt number placeholder. |
| `reconciliation_status` | Select | Reconciliation Status | Yes | Not Required, Pending Reconciliation, Reconciled, Mismatch, Requires Review. |
| `failure_reason` | Small Text | Failure Reason | No | Logs declination details or consent warnings. |
| `triggered_by_event` | Data | Triggered By Event | No | Trigger source. |
| `disclaimer` | Small Text | Disclaimer | Yes | Hardcoded safety warning: *"Prototype simulation only. No live payment was processed."* |

---

## Consent-Aware Behaviour

The module implements privacy checking against the citizen profile's active consent records:
* **Active Consent Found:** When the officer validates a submitted payment, the system locates a `"Simulated Payment Verification"` consent record with `Granted` status. If valid, the gateway transitions the payment to `Verified` and the workflow status to `Payment Verified`.
* **Missing/Withdrawn/Expired Consent:** If the consent record is missing, withdrawn, or expired, the verification transitions to `Requires Review` and notes the warning. The case remains in `Payment Pending`, ensuring that citizen data access permissions are respected without crashing the primary processing thread.

---

## Testing Summary

Verified by 8 dedicated unit and integration tests (suite total: 249 passing tests):
* **Domain Validation:** Asserts negative amount rejection, correct enums (purpose, channel, statuses), and mandatory disclaimer checks.
* **State Transitions:** Validates workflow actions (`submit()`, `verify()`, `fail()`, `reverse()`, `cancel()`, `reconcile()`).
* **Consent Checks:** Checks that granted consent clears verification, while missing/withdrawn/expired consent triggers `Requires Review`.
* **Queries & Metrics:** Verifies listing queries by request, profile, payment status, and reconciliation status, and tests summary aggregates.
* **Gateway Testing:** Ensures deterministic results for special keys (`FAIL` and `REVIEW` in references) without making network calls.

---

## Deployment & Validation Status

* **Status:** Fully implemented at domain, application, infrastructure, seed, and unit test level.
* **Local Run Verification:** All 249 pytest unit tests pass cleanly on python 3.14.5.
* **Production Validation:** Defer bench site migration validation until deploying to a Linux host where Frappe framework commands (`bench`) are available.

---

## Claims Registry

### Safe Claims
* Simulated payment tracking and fee collection status updates.
* Consent-aware verification checks.
* Receipt generation simulation and reconciliation state tracking.
* Full immutable audit event logs.

### Claims to Avoid
* Direct connection to Uganda Revenue Authority (URA), UGHub, MTN MoMo, Airtel Money, Visa, or bank clearings.
* Real financial transactions or legal invoice/receipt issuance.
