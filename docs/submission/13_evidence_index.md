# NileGov Stack Evidence Index

This document indexes the code deliverables, verification results, and operational assets ready in the **NileGov Stack** repository.

---

## 1. Automated Verification Checks

* **Pytest Suite Verification:** **299 passed in 0.44s (100% success rate)** via `.venv/bin/pytest`.
* **Python Compile Check:** **100% successful** via `compileall` (zero syntax/linter errors).
* **Language Compliance Check:** Proves that all strings avoid overclaiming live connections.

---

## 2. Key Code Deliverables

### Core Domain & Application Layer
- [service_request.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/service_request.py) *(Aggregate root coordinating workflows, updated to handle assignments, SLA calculations, and escalation transitions)*
- [citizen.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/citizen.py) *(CitizenProfile aggregate root implementing phone, location, email, preferred contact channel, status, optional NIN and safe demo check)*
- [consent.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/consent.py) *(ConsentRecord aggregate root managing statuses, purposes, and channels)*
- [evidence.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/evidence.py) *(EvidenceDocument aggregate root managing document types, upload channels, verification status, and officer notes)*
- [sla.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/sla.py) *(SLARule aggregate class and SLAState/EscalationState constants)*
- [escalation.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/escalation.py) *(EscalationRecord aggregate class)*
- [notification.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/notification.py) *(NotificationEvent aggregate root managing statuses, channels, recipients, message types, titles, body previews, and consent tracking checks)*
- [payment.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/payment.py) *(PaymentRecord aggregate root managing statuses, purposes, channels, verification statuses, receipt-readiness, and reconciliation)*
- [reporting_snapshot.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/reporting_snapshot.py) *(ReportingSnapshot domain aggregate root compiling pipeline metrics)*
- [value_objects.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/value_objects.py) *(PII validation)*
- [create_citizen_profile.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/create_citizen_profile.py) *(Create profile use case)*
- [update_citizen_contact.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/update_citizen_contact.py) *(Update profile contact use case)*
- [get_citizen_profile.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/get_citizen_profile.py) *(Retrieve profile use case)*
- [list_citizen_service_requests.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_citizen_service_requests.py) *(Retrieve linked requests use case)*
- [create_consent_record.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/create_consent_record.py) *(Create consent use case)*
- [withdraw_consent.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/withdraw_consent.py) *(Withdraw consent use case)*
- [check_active_consent.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/check_active_consent.py) *(Check active consent use case)*
- [list_citizen_consent_records.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_citizen_consent_records.py) *(Query consent by profile use case)*
- [list_request_consent_records.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_request_consent_records.py) *(Query consent by request use case)*
- [create_evidence_document.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/create_evidence_document.py) *(Create evidence document use case)*
- [verify_evidence_document.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/verify_evidence_document.py) *(Verify evidence document status and officer notes use case)*
- [list_service_request_evidence.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_service_request_evidence.py) *(List service request evidence use case)*
- [list_citizen_profile_evidence.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_citizen_profile_evidence.py) *(List citizen profile evidence use case)*
- [assign_officer.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/assign_officer.py) *(Assign officer use case)*
- [reassign_officer.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/reassign_officer.py) *(Reassign officer with reason use case)*
- [assign_department_team.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/assign_department_team.py) *(Assign department/team queue use case)*
- [mark_supervisor_review.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/mark_supervisor_review.py) *(Escalate to supervisor review use case)*
- [return_case_to_officer.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/return_case_to_officer.py) *(Return case to assigned officer use case)*
- [list_unassigned_requests.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_unassigned_requests.py) *(List unassigned requests use case)*
- [list_requests_by_officer.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_requests_by_officer.py) *(List requests by officer use case)*
- [list_requests_by_department.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_requests_by_department.py) *(List requests by department queue use case)*
- [list_supervisor_review_queue.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_supervisor_review_queue.py) *(List supervisor review queue use case)*
- [calculate_workload_metrics.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/calculate_workload_metrics.py) *(Calculate workloads and queue volumes use case)*
- [create_sla_rule.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/create_sla_rule.py) *(Create SLA rule use case)*
- [assign_sla_rule.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/assign_sla_rule.py) *(Assign SLA rule to case use case)*
- [evaluate_sla_state.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/evaluate_sla_state.py) *(Evaluate SLA state use case)*
- [escalate_case.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/escalate_case.py) *(Escalate case use case)*
- [resolve_escalation.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/resolve_escalation.py) *(Resolve escalation use case)*
- [list_at_risk_requests.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_at_risk_requests.py) *(List at risk requests use case)*
- [list_overdue_requests.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_overdue_requests.py) *(List overdue requests use case)*
- [list_escalated_requests.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_escalated_requests.py) *(List escalated requests use case)*
- [verify_payment.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/verify_payment.py) *(Payment use case, updated to evaluate active consent)*
- [close_case.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/close_case.py) *(Closure notes checks)*
- [create_notification_event.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/create_notification_event.py) *(Create notification use case checking active citizen consent)*
- [queue_notification_event.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/queue_notification_event.py) *(Queue notification use case)*
- [mark_notification_sent.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/mark_notification_sent.py) *(Mark notification sent use case)*
- [mark_notification_failed.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/mark_notification_failed.py) *(Mark notification failed use case)*
- [cancel_notification_event.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/cancel_notification_event.py) *(Cancel notification use case)*
- [list_notifications_by_service_request.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_notifications_by_service_request.py) *(List notifications by service request use case)*
- [list_notifications_by_citizen_profile.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_notifications_by_citizen_profile.py) *(List notifications by citizen profile use case)*
- [list_notifications_by_channel.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_notifications_by_channel.py) *(List notifications by channel use case)*
- [list_notifications_by_delivery_status.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_notifications_by_delivery_status.py) *(List notifications by delivery status use case)*
- [generate_message_preview.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/generate_message_preview.py) *(Generate preview for SMS, Email, and WhatsApp templates)*
- [send_simulated_notification.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/send_simulated_notification.py) *(Execute simulated notification delivery)*
- [create_payment_record.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/create_payment_record.py) *(Create payment record use case)*
- [submit_simulated_payment.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/submit_simulated_payment.py) *(Submit payment transaction reference use case)*
- [verify_simulated_payment_record.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/verify_simulated_payment_record.py) *(Verify payment record evaluating active consent use case)*
- [mark_payment_failed.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/mark_payment_failed.py) *(Mark payment failed use case)*
- [reverse_simulated_payment.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/reverse_simulated_payment.py) *(Reverse verified payment use case)*
- [cancel_payment_record.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/cancel_payment_record.py) *(Cancel pending payment record use case)*
- [mark_receipt_ready.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/mark_receipt_ready.py) *(Mark receipt status ready use case)*
- [mark_simulated_receipt_generated.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/mark_simulated_receipt_generated.py) *(Simulate receipt generation use case)*
- [list_payments_by_service_request.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_payments_by_service_request.py) *(List payments by service request use case)*
- [list_payments_by_citizen_profile.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_payments_by_citizen_profile.py) *(List payments by citizen profile use case)*
- [list_payments_by_payment_status.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_payments_by_payment_status.py) *(List payments by status use case)*
- [list_payments_by_reconciliation_status.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_payments_by_reconciliation_status.py) *(List payments by reconciliation status use case)*
- [calculate_payment_summary_metrics.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/calculate_payment_summary_metrics.py) *(Compute payments metrics use case)*
- [register_pesapal_ipn.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/register_pesapal_ipn.py) *(Register Pesapal IPN use case)*
- [initiate_pesapal_payment.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/initiate_pesapal_payment.py) *(Initiate Pesapal sandbox payment flow use case)*
- [refresh_pesapal_payment_status.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/refresh_pesapal_payment_status.py) *(Refresh Pesapal payment status and sync use case)*
- [pesapal_payload_parsers.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/pesapal_payload_parsers.py) *(Parses Pesapal callback and IPN payloads metadata)*
- [service_catalogue.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/domain/service_catalogue.py) *(ServiceCatalogueItem domain aggregate and enums)*
- [create_service_catalogue_item.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/create_service_catalogue_item.py) *(Create service catalogue item use case)*
- [update_service_catalogue_item.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/update_service_catalogue_item.py) *(Update service catalogue item attributes use case)*
- [list_services.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/list_services.py) *(List and filter service catalogue items use case)*
- [manage_service_status.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/manage_service_status.py) *(Transition item active status use case)*
- [retrieve_service_by_code.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/retrieve_service_by_code.py) *(Fetch item by short code use case)*
- [apply_catalogue_defaults.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/apply_catalogue_defaults.py) *(Sync defaults to service request and payment aggregates, check evidence requirements use case)*
- [generate_reporting_snapshot.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/generate_reporting_snapshot.py) *(GenerateReportingSnapshot application service to compile performance metrics)*


### Infrastructure Layer (Persistence & Gateways)
- [frappe_service_request_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_service_request_repository.py) *(Maps service request SLA and escalation domain state changes to the database)*
- [frappe_citizen_profile_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_citizen_profile_repository.py) *(Maps profile domain state changes to the Frappe framework)*
- [citizen_profile_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/citizen_profile_repository.py) *(InMemory repository for profile testing)*
- [frappe_consent_record_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_consent_record_repository.py) *(Maps consent record domain state changes to the Frappe framework)*
- [consent_record_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/consent_record_repository.py) *(InMemory repository for consent testing)*
- [frappe_evidence_document_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_evidence_document_repository.py) *(Maps evidence document domain state changes to the Frappe framework)*
- [evidence_document_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/evidence_document_repository.py) *(InMemory repository for evidence document testing)*
- [sla_rule_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/sla_rule_repository.py) *(InMemory repository for SLA rule testing)*
- [frappe_sla_rule_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_sla_rule_repository.py) *(Maps SLA rules domain state changes to the database)*
- [frappe_notification_event_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_notification_event_repository.py) *(Maps notification domain state changes to the database)*
- [notification_event_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/notification_event_repository.py) *(InMemory repository for notification testing)*
- [frappe_payment_record_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_payment_record_repository.py) *(Maps payment record domain state changes to the database)*
- [payment_record_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/payment_record_repository.py) *(InMemory repository for payment testing)*
- [simulated_identity_gateway.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/integrations/simulated_identity_gateway.py) *(Sandbox check)*
- [simulated_payment_gateway.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/integrations/simulated_payment_gateway.py) *(Sandbox check updated for PaymentRecord verification)*
- [pesapal_api_client.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/integrations/pesapal_api_client.py) *(Pesapal API 3.0 Sandbox/Live integration client)*
- [simulated_notification_gateway.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/notifications/simulated_notification_gateway.py) *(Logs simulated notifications for email, SMS, and WhatsApp)*
- [frappe_service_catalogue_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_service_catalogue_repository.py) *(Maps service catalogue item domain state changes to the database)*
- [service_catalogue_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/service_catalogue_repository.py) *(InMemory repository for service catalogue testing)*
- [reporting_snapshot_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/reporting_snapshot_repository.py) *(InMemory repository for ReportingSnapshot testing)*
- [frappe_reporting_snapshot_repository.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/infrastructure/repositories/frappe_reporting_snapshot_repository.py) *(Maps ReportingSnapshot domain state changes to the database)*


### Frappe Integration Layer
- [nilegov_citizen_profile.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_citizen_profile/nilegov_citizen_profile.json) *(Citizen Profile DocType schema)*
- [nilegov_citizen_profile.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_citizen_profile/nilegov_citizen_profile.py) *(Citizen Profile controller validations)*
- [nilegov_consent_record.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_consent_record/nilegov_consent_record.json) *(Consent Record DocType schema)*
- [nilegov_consent_record.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_consent_record/nilegov_consent_record.py) *(Consent Record controller validations)*
- [nilegov_evidence_document.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_evidence_document/nilegov_evidence_document.json) *(Evidence Document DocType schema updated for document verification)*
- [nilegov_evidence_document.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_evidence_document/nilegov_evidence_document.py) *(Evidence Document controller validations)*
- [nilegov_sla_rule.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_sla_rule/nilegov_sla_rule.json) *(SLA Rule DocType schema)*
- [nilegov_escalation_record.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_escalation_record/nilegov_escalation_record.json) *(Escalation Record DocType schema)*
- [nilegov_citizen_notification.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_citizen_notification/nilegov_citizen_notification.json) *(Citizen Notification DocType schema)*
- [nilegov_citizen_notification.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_citizen_notification/nilegov_citizen_notification.py) *(Citizen Notification controller validations)*
- [nilegov_payment_record.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_payment_record/nilegov_payment_record.json) *(Payment Record DocType schema)*
- [nilegov_payment_record.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_payment_record/nilegov_payment_record.py) *(Payment Record controller validations)*
- [nilegov_service_catalogue.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_service_catalogue/nilegov_service_catalogue.json) *(Service Catalogue DocType schema)*
- [nilegov_service_catalogue.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_service_catalogue/nilegov_service_catalogue.py) *(Service Catalogue controller validations)*

- [nilegov_service_request.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_service_request/nilegov_service_request.json) *(Service Request DocType schema, updated for SLA and escalations)*
- [nilegov_service_request.js](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_service_request/nilegov_service_request.js) *(Desk action handlers)*
- [nilegov_case_operations.json](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/nilegov_stack/workspace/nilegov_case_operations/nilegov_case_operations.json) *(Desk Operations Workspace)*
- [seed_service_types_and_sla_rules.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/patches/seed_service_types_and_sla_rules.py) *(SLA rule seeding patch)*
- [seed_demo_records.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/patches/seed_demo_records.py) *(Seeding patch registered in patches.txt, updated for SLA states and escalations)*
- [docker-compose.yml](file:///Users/robertsebunya/Documents/Nile_Gov/deployment/docker-compose.yml) *(Deployment setup mapping local source code)*

---

## 3. Operational Testing Status

* **Static Schema Verification:** Checked. All 15 schema definitions contain the required disclaimers.
* **Gunicorn / MariaDB Execution:** Stalled. Live runtime validation is pending deployment on a working container host.
* **Wording Audit:** Verified. No live integration claims are made in documentation or code.

## API / Interoperability Readiness Evidence

| Evidence Item | Location | Notes |
|---|---|---|
| Interoperability domain model | `apps/nilegov_stack/nilegov_stack/domain/interoperability.py` | Defines integration request, response, API envelope and API error structures |
| API envelope helpers | `apps/nilegov_stack/nilegov_stack/application/build_api_envelope.py` | Builds success and error response envelopes |
| Correlation/idempotency helpers | `apps/nilegov_stack/nilegov_stack/application/generate_integration_keys.py` | Generates trace and retry-safety keys |
| Integration request use case | `apps/nilegov_stack/nilegov_stack/application/create_integration_request.py` | Creates simulated interoperability requests |
| Integration result use cases | `apps/nilegov_stack/nilegov_stack/application/record_integration_result.py` | Records simulated success and failure outcomes |
| Integration list use case | `apps/nilegov_stack/nilegov_stack/application/list_integration_requests.py` | Lists requests by target system, status and service request |
| Safe payload builders | `apps/nilegov_stack/nilegov_stack/application/build_interoperability_payloads.py` | Builds minimised service, identity, payment, notification and reporting payloads |
| In-memory repository | `apps/nilegov_stack/nilegov_stack/infrastructure/repositories/integration_request_repository.py` | Supports testable simulated integration workflows |
| Unit tests | `apps/nilegov_stack/nilegov_stack/tests/unit/test_interoperability.py` | Validates domain model, envelopes, payload safety and repository behaviour |
| Module documentation | `docs/modules/10_api_interoperability_readiness.md` | Explains purpose, boundaries, safe claims and runtime limitations |

## Roles, Permissions and User Profiles Evidence

| Evidence Item | Location | Notes |
|---|---|---|
| Role and permission documentation | `docs/modules/11_roles_permissions_foundation.md` | Defines NileGov role model and access assumptions |
| Permission policy helper | `apps/nilegov_stack/nilegov_stack/application/permission_policy.py` | Provides testable permission assumptions |
| Permission policy tests | `apps/nilegov_stack/nilegov_stack/tests/unit/test_permission_policy.py` | Confirms protected logs, role separation and no live access claims |

---

## Pass 11B-3 Additions (Workspace Navigation, Search Fields)

### Workspace
- `workspace/nilegov_case_operations/nilegov_case_operations.json` updated with 8 labelled sections (A–H), 20 shortcuts, and 24 links covering all 16 NileGov DocTypes.

### DocType Search/List Enhancements (all 16 DocTypes)
| DocType | search_fields | in_list_view count | sort_field |
|---|---|---|---|
| NileGov Service Request | service_request_id, citizen_full_name, service_type, assigned_officer, internal_status | 6 | submitted_at DESC |
| NileGov Citizen Profile | citizen_profile_id, full_name, phone, nin | 5 | full_name ASC |
| NileGov Evidence Document | evidence_document_id, service_request, document_type, verification_status | 5 | uploaded_at DESC |
| NileGov Payment Record | payment_record_id, service_request, payment_purpose, payment_status, provider_merchant_reference | 5 | verification_timestamp DESC |
| NileGov Case Note | service_request, note_type, created_by_user | 4 | created_at DESC |
| NileGov Citizen Notification | notification_event_id, service_request, channel, delivery_status | 5 | scheduled_at DESC |
| NileGov SLA Event | service_request, event_type, status | 5 | due_at ASC |
| NileGov Escalation Record | service_request, escalated_by, escalated_to, status | 5 | escalated_at DESC |
| NileGov Service Catalogue | service_code, service_name, service_category | 5 | service_name ASC |
| NileGov Reporting Snapshot | snapshot_name, source_dataset, generated_by | 5 | generated_at DESC |
| NileGov Integration Simulation Log | service_request, integration_name, simulation_type, status | 5 | simulated_at DESC |
| NileGov Audit Event | service_request, event_type, actor, actor_role | 6 | event_time DESC |
| NileGov SLA Rule | sla_rule_id, service_type | 5 | sla_rule_id ASC |
| NileGov Service Type | service_code, service_name | 5 | service_name ASC |
| NileGov Consent Record | consent_record_id, citizen_profile, service_request, consent_status | 5 | consent_given_at DESC |
| NileGov Simulated Identity Verification | service_request, simulation_status, verification_source | 4 | simulated_at DESC |

### Tests Added
- `tests/unit/test_workspace_navigation.py` — 155 tests, 17 classes covering workspace links, shortcuts, no broken DocType names, no live labels, roles, section labels, search_fields, title_field, sort_field, list_view count, standard filters, JSON integrity, and spot-checks.

### Test Suite After Pass 11B-7B
- **1354 / 1354 passed** (includes Pass 11B-6B print formats, Pass 11B-6C notifications, Pass 11B-6D assignment rules, and Pass 11B-7B web forms static architecture tests)
- Python compile: CLEAN
- `.env`: untracked

### Pass 11B-5B Additions (Reporting Workspace Shortcuts and Evidence Update)
- Added new section `I. Reports and Dashboards` to NileGov Case Operations Workspace links with 1 dashboard and 9 report shortcut links.
- Created [test_workspace_reporting_links.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/unit/test_workspace_reporting_links.py) verifying workspace links existence, dashboard and report definitions matching, and sandbox/prototype label disclaimers.

### Pass 11B-6B Additions (Print Format Definitions)
- Created 7 standard Print Format JSON files under `print_format/` for acknowledgements, replacement case summaries, simulated payment receipts, evidence reviews, SLA escalation memos, case closure certificates, and M&E briefs.
- Registered print formats in `hooks.py` fixtures.
- Created [test_print_format_definitions.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/architecture/test_print_format_definitions.py) to statically assert all definition schemas, HTML content, and mandatory simulation/sandbox disclaimers.

### Pass 11B-6C Additions (Simulated Notification Templates)
- Created 8 standard Notification JSON files under `notification/` for officers assigned, incomplete evidence, pending review payments, SLA risk/overdue alerts, escalation assignments, case closures, and status updates.
- Registered notifications in `hooks.py` fixtures.
- Created [test_notification_definitions.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/architecture/test_notification_definitions.py) to statically assert definitions, trigger conditions, recipient roles, and mandatory simulation disclaimers.

### Pass 11B-6D Additions (Assignment Rules and ToDo Readiness)
- Created 7 standard Assignment Rule JSON files under `assignment_rule/` for submitted queues, evidence reviews, payment reviews, SLA risks, SLA breaches, SLA escalations, and case closure reviews.
- Registered assignment rules in `hooks.py` fixtures.
- Created [test_assignment_rule_definitions.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/architecture/test_assignment_rule_definitions.py) to statically assert all definition schemas, priority rules, target roles, and conditions.

### Pass 11B-7B Additions (Citizen Web Form Metadata Scaffold)
- Created 3 standard Web Form JSON files under `web_form/` for intake, supplementary evidence documents, and citizen consent records.
- Configured all Web Forms as unpublished (`published=0`) and login-required (`login_required=1`).
- Registered Web Forms in `hooks.py` fixtures.
- Created [test_web_form_definitions.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/architecture/test_web_form_definitions.py) to statically verify field safety, disclaimers, and security parameters.

### Pass 11B-7C Additions (REST API Envelope Endpoint Scaffolding)
- Created [public_readiness.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/interfaces/frappe/api/public_readiness.py) implementing 6 read-only whitelisted API endpoints.
- Exported API endpoints in [__init__.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/interfaces/frappe/api/__init__.py).
- Created [test_public_api_scaffold.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/architecture/test_public_api_scaffold.py) statically asserting that the endpoints are whitelisted, free of secrets, forbidden fields, or emails, and enforce disclaimers.
- Created [test_public_api_scaffold_outputs.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/unit/test_public_api_scaffold_outputs.py) validating API envelopes, schemas, optional NIN formatting, and response structure.
- **1376 / 1376 passed** in total test suite.

### Pass 11B-7D Additions (Citizen Status Lookup and Redaction Layer)
- Created [redaction.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/application/redaction.py) containing masking functions (`mask_nin`, `mask_phone`, `mask_email`) and status data redaction helpers.
- Added `get_redacted_case_status_preview` to [public_readiness.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/interfaces/frappe/api/public_readiness.py) whitelisting a secure read-only case status lookup by reference.
- Exported the new API endpoint in [__init__.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/interfaces/frappe/api/__init__.py).
- Created [test_redaction.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/unit/test_redaction.py) to independently unit-test all masking and redaction behaviors.
- Updated unit and architecture tests in `test_public_api_scaffold.py` and `test_public_api_scaffold_outputs.py` to cover safety constraints and the lookup endpoints.
- **1388 / 1388 passed** in total test suite.

### Pass 11B-8B Additions (Safe Install Hook and Setup Readiness)
- Created [install.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/install.py) implementing the safe, conservative `after_install` setup validation hook.
- Registered the install hook in [hooks.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/hooks.py).
- Created [test_install_readiness.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/architecture/test_install_readiness.py) to statically assert hook registration, role validation, and lack of live/secret claims.
- Created [test_install_readiness.py](file:///Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack/nilegov_stack/tests/unit/test_install_readiness.py) unit testing `get_canonical_roles()` and `get_install_readiness_summary()`.





