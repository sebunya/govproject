# Controller for NileGov Service Request
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.model.document import Document

class NileGovServiceRequest(Document):
    def validate(self):
        # Basic validation
        if not self.service_type:
            frappe.throw("Service Type is required.")
        if not self.citizen_profile:
            frappe.throw("Citizen Profile is required.")
        if not self.citizen_full_name:
            frappe.throw("Citizen Full Name is required.")
        if not self.nin:
            frappe.throw("NIN is required.")
        if not self.location:
            frappe.throw("Location is required.")
        if not self.phone and not self.email:
            frappe.throw("Either phone or email must be provided.")
        if not self.internal_status:
            frappe.throw("Internal Status is required.")
        if not self.citizen_visible_status:
            frappe.throw("Citizen Visible Status is required.")
            
        # Closure validation: closure requires decision or closure_notes
        if self.internal_status == "Closed" or self.citizen_visible_status == "Closed":
            if not self.closure_notes:
                frappe.throw("Closure notes are mandatory for closing a request.")
            if self.decision == "None" or not self.decision:
                frappe.throw("Decision must be specified for closing a request.")


@frappe.whitelist()
def run_simulated_identity_check(request_id):
    """Triggers simulated identity check on the document."""
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.infrastructure.integrations.simulated_identity_gateway import SimulatedIdentityVerificationGateway
    from nilegov_stack.application.run_simulated_identity_check import RunSimulatedIdentityCheck
    
    repo = FrappeServiceRequestRepository()
    gateway = SimulatedIdentityVerificationGateway()
    use_case = RunSimulatedIdentityCheck(repo, gateway)
    
    result = use_case.execute(request_id, actor=frappe.session.user)
    return result


@frappe.whitelist()
def verify_payment(request_id):
    """Triggers simulated payment check on the document."""
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.infrastructure.integrations.simulated_payment_gateway import SimulatedPaymentVerificationGateway
    from nilegov_stack.application.verify_payment import VerifyPayment
    
    repo = FrappeServiceRequestRepository()
    gateway = SimulatedPaymentVerificationGateway()
    use_case = VerifyPayment(repo, gateway)
    
    result = use_case.execute(request_id, actor=frappe.session.user)
    return result


@frappe.whitelist()
def assign_officer(request_id, officer_id):
    """Assigns the service request to an officer."""
    import time
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.application.assign_officer import AssignOfficer
    
    repo = FrappeServiceRequestRepository()
    use_case = AssignOfficer(repo)
    use_case.execute(request_id, officer_id, timestamp=time.time())
    return True


@frappe.whitelist()
def reassign_officer(request_id, new_officer_id, reason):
    """Reassigns the service request to another officer with a reason."""
    import time
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.application.reassign_officer import ReassignOfficer
    
    repo = FrappeServiceRequestRepository()
    use_case = ReassignOfficer(repo)
    use_case.execute(request_id, new_officer_id, reason, timestamp=time.time())
    return True


@frappe.whitelist()
def assign_department_team(request_id, department, team=None):
    """Assigns the service request to a department/team queue."""
    import time
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.application.assign_department_team import AssignDepartmentTeam
    
    repo = FrappeServiceRequestRepository()
    use_case = AssignDepartmentTeam(repo)
    use_case.execute(request_id, department, team, timestamp=time.time())
    return True


@frappe.whitelist()
def mark_supervisor_review(request_id, supervisor_id):
    """Escalates/routes the case to supervisor review."""
    import time
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.application.mark_supervisor_review import MarkSupervisorReview
    
    repo = FrappeServiceRequestRepository()
    use_case = MarkSupervisorReview(repo)
    use_case.execute(request_id, supervisor_id, timestamp=time.time())
    return True


@frappe.whitelist()
def return_case_to_officer(request_id):
    """Returns the case from supervisor review back to the assigned officer."""
    import time
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.application.return_case_to_officer import ReturnCaseToOfficer
    
    repo = FrappeServiceRequestRepository()
    use_case = ReturnCaseToOfficer(repo)
    use_case.execute(request_id, timestamp=time.time())
    return True


@frappe.whitelist()
def evaluate_sla_state(request_id):
    """Evaluates the SLA state of a service request."""
    import time
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.infrastructure.repositories.frappe_sla_rule_repository import FrappeSLARuleRepository
    from nilegov_stack.application.evaluate_sla_state import EvaluateSLAState
    
    req_repo = FrappeServiceRequestRepository()
    rule_repo = FrappeSLARuleRepository()
    use_case = EvaluateSLAState(req_repo, rule_repo)
    use_case.execute(request_id, current_time=time.time())
    return True


@frappe.whitelist()
def escalate_case(request_id, supervisor_id, reason):
    """Escalates a service request case to a supervisor."""
    import time
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.application.escalate_case import EscalateCase
    
    repo = FrappeServiceRequestRepository()
    use_case = EscalateCase(repo)
    use_case.execute(request_id, supervisor_id, reason, timestamp=time.time())
    return True


@frappe.whitelist()
def resolve_escalation(request_id):
    """Resolves an escalation on a service request."""
    import time
    from nilegov_stack.infrastructure.repositories.frappe_service_request_repository import FrappeServiceRequestRepository
    from nilegov_stack.application.resolve_escalation import ResolveEscalation
    
    repo = FrappeServiceRequestRepository()
    use_case = ResolveEscalation(repo)
    use_case.execute(request_id, timestamp=time.time())
    return True

