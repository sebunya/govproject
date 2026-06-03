# Pesapal API 3.0 Sandbox Adapter Foundation

## Module Purpose
The Pesapal API 3.0 Sandbox Adapter Foundation provides a secure, environment-configured adapter preparing the NileGov Stack for integration with the Pesapal API 3.0 payment gateway. It allows the platform to initiate payments and track transaction status in sandbox mode, completely decoupled from live payment processors.

## Why Pesapal Was Selected
Pesapal API 3.0 is a leading East African payment gateway widely used in Uganda, Kenya, and Tanzania. It supports multiple key payment channels (Mobile Money via MTN & Airtel, Credit/Debit cards, bank transfers) under a unified REST interface, making it an excellent bridge for local MDA (Ministries, Departments, and Agencies) revenue collections without requiring separate direct integrations with individual telecommunication networks or financial institutions.

## API 3.0 Flow
The integration follows the standard Pesapal API 3.0 workflow:
1. **Authentication**: Call `POST /api/Auth/RequestToken` using `consumer_key` and `consumer_secret` to obtain a short-lived (5-minute) bearer token.
2. **IPN Registration**: Call `POST /api/URLSetup/RegisterIPN` to register the public callback URL and obtain an `ipn_id`.
3. **Submit Order**: Call `POST /api/Transactions/SubmitOrderRequest` with the payment details, merchant reference, and `ipn_id`. The response returns an `order_tracking_id` and a `redirect_url` for the citizen's browser.
4. **Verification Loop**: Upon payment completion, Pesapal calls the public callback/IPN. The application extracts the metadata, then runs `GET /api/Transactions/GetTransactionStatus` to securely verify the final state.

## Sandbox vs Live Mode
* **Sandbox Mode**: (Default) Communicates with `https://cybqa.pesapal.com/pesapalv3`. Does not charge real money or require verified merchant credentials.
* **Live Mode**: Communicates with `https://pay.pesapal.com/v3`. Disabled by default. It requires BOTH `PESAPAL_MODE=live` and `PESAPAL_LIVE_ENABLED=true` to prevent accidental production activations.

## Environment Variables
The adapter is configured using the following environment variables:
```env
PESAPAL_MODE=sandbox
PESAPAL_CONSUMER_KEY=<set in uncommitted .env or server environment>
PESAPAL_CONSUMER_SECRET=<set in uncommitted .env or server environment>
PESAPAL_SANDBOX_BASE_URL=https://cybqa.pesapal.com/pesapalv3
PESAPAL_LIVE_BASE_URL=https://pay.pesapal.com/v3
PESAPAL_CALLBACK_URL=https://nile-gov-demo.com/api/payments/pesapal/callback
PESAPAL_CANCELLATION_URL=https://nile-gov-demo.com/api/payments/pesapal/cancel
PESAPAL_IPN_URL=https://nile-gov-demo.com/api/payments/pesapal/ipn
PESAPAL_IPN_NOTIFICATION_TYPE=POST
PESAPAL_LIVE_ENABLED=false
```

## Token Flow
Authentication tokens are requested programmatically prior to any transactional calls. The short-lived bearer token is cached per execution session and is never logged to avoid security exposures.

## IPN Registration
The public IPN endpoint is registered with Pesapal using the `RegisterPesapalIPN` use case. The returned `ipn_id` is required when submitting payment orders so that Pesapal knows where to send asynchronous status updates.

## Submit Order Flow
1. An unpaid `PaymentRecord` is loaded.
2. An order is submitted via `InitiatePesapalPayment` containing the amount, currency (UGX), payment purpose description, billing address, and registered `ipn_id`.
3. The adapter receives the `order_tracking_id` and `redirect_url`.
4. The payment status changes to `Submitted`, and the citizen is redirected to complete the payment.

## Callback / IPN Handling Boundary
As a security measure, the callback or IPN payload receipt is **never** used as a direct proof of payment. It only triggers a backend status query. Callback and IPN payload parsing helpers (`parse_pesapal_callback_payload` and `parse_pesapal_ipn_payload`) extract metadata and update payment record timestamps without altering the payment status.

## Why GetTransactionStatus is Mandatory
The callback/IPN request could potentially be spoofed or altered. To ensure integrity, the final state verification is exclusively determined by querying `GET /api/Transactions/GetTransactionStatus?orderTrackingId=...` directly from NileGov backend servers to Pesapal's secure endpoints. Only a `COMPLETED` response from this endpoint can transition a payment record to `Verified`.

## Payment Status Mapping
Pesapal transaction status codes are mapped to NileGov states:
* **Code 1 (COMPLETED)**: Maps to payment status `Verified`, verification status `Simulated Verified`, receipt status `Receipt Ready`, and reconciliation status `Pending Reconciliation`.
* **Code 2 (FAILED)**: Maps to payment status `Failed`, verification status `Simulated Failed`, and stores the failure reason description.
* **Code 3 (REVERSED)**: Maps to payment status `Reversed`, verification status `Requires Review`, and reconciliation status `Requires Review`.
* **Code 0 (INVALID)**: Maps to payment status `Failed`, verification status `Requires Review`, and stores the description.

## Security Controls
* **No Live Payments**: In development/sandbox environments, no money changes hands.
* **Explicit Live Switch**: Blocked by default to prevent accidental production deployments.
* **Masked Payment Accounts**: Real card, bank, or mobile money numbers are never stored in plain text. Only the masked payment account reference supplied by Pesapal is optionally recorded.
* **No Secrets Committed**: Credentials are kept in `.env` files.
* **No Mocking Network Calls in Production**: All tests utilize standard mocks.

## What is Implemented
* Pure python `PesapalApiClient` and `PesapalConfig` definitions.
* Extensively updated `PaymentRecord` domain model and DocType schemas with 14 provider-specific fields.
* Application use cases: `RegisterPesapalIPN`, `InitiatePesapalPayment`, `RefreshPesapalPaymentStatus`, and payload parsers.
* Standardized test suite executing multiple verification checks.

## What Remains Pending for Hetzner
* Deployed container host setup.
* Public SSL/HTTPS configuration for receiving real IPNs.
* Interactive Desk button triggers to initiate the actual redirect loop.
* Live merchant account verification.

## Safe Claims
* Pesapal API 3.0 sandbox adapter foundation implemented.
* Live mode disabled by default.
* No live payment processed.
* No real network calls in tests.
* Payment status verification prepared through Pesapal `GetTransactionStatus`.

## Claims to Avoid
* Do not claim live connection to URA, MTN MoMo, Airtel Money, Visa, Mastercard, or banks.
* Do not claim active production status.
