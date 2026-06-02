# NileGov Stack Evaluator Walkthrough Notes

Dear Ministry Evaluator,

This document explains the NileGov Stack prototype design and guides you through what each system component demonstrates.

---

## 1. Why the National ID Replacement Service was Selected

Replacing a lost or damaged National Identification Card is a high-volume service that:
1. Interacts directly with citizen PII.
2. Involves cross-agency verification (requiring lookup against the NIRA registry).
3. Requires tracking citizen consent for data access.
4. Requires verifying compliance fee payments (matching tax collection logs).
5. Must be processed under strict timelines (SLA rules) to ensure public accountability.

If NileGov Stack can successfully manage this complex workflow, it demonstrates the platform's suitability for digitizing almost any other Ministry service (such as permit requests, license renewals, and registration applications).

---

## 2. What Each Workflow Step Demonstrates

The prototype seeds 9 requests, allowing you to examine how NileGov Stack coordinates different processing stages:

* **Submitted (`req_pass3_001`):** Demonstrates intake capture. The system generates a unique reference ID and computes the SLA resolution deadline.
* **Under Review (`req_pass3_002`):** Shows the officer-side view. The case is assigned, and status logging tracks when the evaluation started.
* **Information Required (`req_pass3_003`):** Demonstrates workflow flexibility. If details are missing, the officer can return the request, which suspends SLA response calculations.
* **Payment Pending (`req_pass3_004`):** Shows fee-compliance queues. The citizen's identity has been matched, and the request is awaiting payment verification.
* **Payment Verified (`req_pass3_005`):** Confirms that payment verification callbacks have succeeded.
* **Approved & Ready for Collection (`req_pass3_006` & `req_pass3_007`):** Demonstrates final validation and shipping stages. The new card is printed and ready for pickup at the Ntinda collection liaison office.
* **Closed (`req_pass3_008`):** Displays case closure. The card has been handed over, and the officer has added mandatory evaluation and resolution notes.
* **Overdue (`req_pass3_009`):** Demonstrates SLA monitoring. This case has breached processing limits and is visually highlighted to supervisors.

---

## 3. Why Simulated Integrations are Used

In compliance with the **Absolute Honesty Rule**, there are no live connections to the sovereign NIRA registry, URA tax portals, or mobile money systems in this prototype. Doing so would require formal Data Sharing Agreements (DSAs) and network setups.

Instead, we use pluggable **Simulated Gateways**:
* **Simulated NIRA Verification:** Verifies NIN input formats against mock profiles and logs the transaction.
* **Simulated Payment Verification:** Confirms payment status for test fee numbers.

Both systems generate transaction logs clearly marked with simulation warnings, showing how the logic is structured for a future production connection.

---

## 4. Production Integration Roadmap

Moving from this prototype to a live deployment in a Ministry site involves:
1. **Infrastructure Migration:** Run the native Docker Compose stack on the Ministry's private cloud or national data center servers.
2. **Data Sharing Agreements:** Sign formal DSAs with NIRA and payment providers.
3. **Plugging Live APIs:** Replace the simulated Python gateways with live HTTP clients targeting the NIRA registry and national service buses (e.g. UGHub REST interfaces). The domain logic remains untouched, preserving the system's core stability.
