# Architecture Import Boundary Test
# Digi-Verse Uganda Limited

import os
import ast
import pytest


def get_domain_source_files():
    """Locates all Python source files in the domain layer."""
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    domain_dir = os.path.join(current_dir, "domain")
    
    domain_files = []
    for root, _, files in os.walk(domain_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                domain_files.append(os.path.join(root, file))
    return domain_files


@pytest.mark.parametrize("file_path", get_domain_source_files())
def test_no_framework_or_network_imports_in_domain(file_path):
    """Enforces that no file in the domain layer imports framework, db, or HTTP clients."""
    forbidden_modules = {
        "frappe", "requests", "mariadb", "redis", "pymysql", "mysql",
        "smtplib", "imaplib", "poplib", "urllib", "urllib3", "httpx", "aiohttp",
        "sqlite3", "psycopg2", "sqlalchemy", "peewee"
    }
    
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    for node in ast.walk(tree):
        # Handle direct imports: 'import frappe', 'import requests'
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]
                assert root_module not in forbidden_modules, (
                    f"Forbidden import '{alias.name}' detected in {file_path}. "
                    f"Domain layer must remain framework-agnostic."
                )
                
        # Handle from-imports: 'from frappe.model.document import Document'
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split(".")[0]
                assert root_module not in forbidden_modules, (
                    f"Forbidden import 'from {node.module}' detected in {file_path}. "
                    f"Domain layer must remain framework-agnostic."
                )


def test_domain_can_be_imported_without_frappe():
    """Verifies that key domain classes can be imported and initialized without errors."""
    from nilegov_stack.domain.value_objects import NIN
    from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus
    
    nin = NIN("CF999999999999")
    req = ServiceRequest(
        request_id="req_123",
        reference_no="NGS-NIRA-2026-9999",
        citizen_nin=nin,
        citizen_name="Demo Citizen A",
        phone_number="+256780000000",
        location="Ntinda, Kampala",
        description="Lost my ID."
    )
    
    assert req.request_id == "req_123"
    assert req.status == WorkflowStatus.SUBMITTED
    assert req.identity_status == "Requires Review"
