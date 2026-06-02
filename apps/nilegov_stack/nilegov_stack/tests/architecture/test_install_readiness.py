# Pass 11B-8B: Static Architecture Tests for Installation Hook Readiness
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external integration.
#

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
INSTALL_MODULE_PATH = os.path.join(OUTER_PACKAGE, "install.py")
HOOKS_FILE_PATH = os.path.join(OUTER_PACKAGE, "hooks.py")


class TestInstallHookArchitecture:
    def test_install_module_exists(self):
        assert os.path.isfile(INSTALL_MODULE_PATH), f"install.py not found at: {INSTALL_MODULE_PATH}"

    def test_after_install_function_exists(self):
        with open(INSTALL_MODULE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def after_install(" in content, "after_install() function definition is missing"

    def test_hooks_registers_correct_install_path(self):
        with open(HOOKS_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # Verify unregistered/commented out pattern does not match
        pattern = r'^after_install\s*=\s*["\']nilegov_stack\.install\.after_install["\']'
        assert re.search(pattern, content, re.MULTILINE), "hooks.py does not register after_install correctly"

    def test_install_module_contains_no_secrets_or_env(self):
        with open(INSTALL_MODULE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert ".env" not in content
        assert "secret" not in content.lower()
        assert "password" not in content.lower()
        assert "token" not in content.lower()

    def test_install_module_excludes_live_claims(self):
        with open(INSTALL_MODULE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "nira_live_connection" not in content
        assert "production_payment" not in content.lower()
        assert "http://" not in content
        assert "https://" not in content

    def test_install_module_does_not_create_demo_users_or_data(self):
        with open(INSTALL_MODULE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "demo_user" not in content.lower()
        assert "Demo Citizen" not in content
        assert "CF9000" not in content
        assert "NIN" not in content
        assert "+256" not in content

    def test_canonical_roles_referenced(self):
        with open(INSTALL_MODULE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "NileGov Citizen Officer" in content
        assert "NileGov Records Officer" in content
        assert "NileGov Payments Officer" in content
        assert "NileGov SLA Supervisor" in content
        assert "NileGov M&E Viewer" in content
        assert "NileGov MDA Admin" in content
        assert "NileGov System Auditor" in content
        assert "NileGov System Manager" in content
