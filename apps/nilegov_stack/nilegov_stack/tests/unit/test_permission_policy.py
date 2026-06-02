from nilegov_stack.application.permission_policy import (
    NILEGOV_ROLES,
    PROTECTED_DOCTYPES,
    can_modify_protected_log,
    can_read_protected_log,
    can_review_evidence,
    can_review_payment,
    is_nilegov_role,
    is_protected_doctype,
    is_sensitive_doctype,
    role_implies_live_government_access,
)


def test_required_roles_are_defined():
    expected = {
        "NileGov Citizen Officer",
        "NileGov Records Officer",
        "NileGov Payments Officer",
        "NileGov SLA Supervisor",
        "NileGov M&E Viewer",
        "NileGov MDA Admin",
        "NileGov System Auditor",
        "NileGov System Manager",
    }

    assert expected.issubset(NILEGOV_ROLES)


def test_audit_and_integration_logs_are_protected():
    assert "NileGov Audit Event" in PROTECTED_DOCTYPES
    assert "NileGov Integration Simulation Log" in PROTECTED_DOCTYPES
    assert is_protected_doctype("NileGov Audit Event")
    assert is_protected_doctype("NileGov Integration Simulation Log")


def test_ordinary_roles_cannot_modify_protected_logs():
    assert can_modify_protected_log("NileGov Citizen Officer", "NileGov Audit Event") is False
    assert can_modify_protected_log("NileGov Records Officer", "NileGov Integration Simulation Log") is False
    assert can_modify_protected_log("NileGov Payments Officer", "NileGov Audit Event") is False
    assert can_modify_protected_log("NileGov System Auditor", "NileGov Audit Event") is False


def test_auditor_can_read_but_not_modify_protected_logs():
    assert can_read_protected_log("NileGov System Auditor", "NileGov Audit Event") is True
    assert can_modify_protected_log("NileGov System Auditor", "NileGov Audit Event") is False


def test_payment_and_evidence_duties_are_separated():
    assert can_review_payment("NileGov Payments Officer") is True
    assert can_review_payment("NileGov Records Officer") is False

    assert can_review_evidence("NileGov Records Officer") is True
    assert can_review_evidence("NileGov Payments Officer") is False


def test_sensitive_doctypes_are_identified():
    assert is_sensitive_doctype("NileGov Citizen Profile")
    assert is_sensitive_doctype("NileGov Evidence Document")
    assert is_sensitive_doctype("NileGov Payment Record")
    assert is_sensitive_doctype("NileGov Service Request")


def test_roles_do_not_imply_live_government_access():
    for role in NILEGOV_ROLES:
        assert is_nilegov_role(role)
        assert role_implies_live_government_access(role) is False
