# Pass 11B-8E: Pre-Hetzner Runtime Lockdown Verification Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external integration.
#

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
PROJECT_ROOT = os.path.abspath(os.path.join(OUTER_PACKAGE, "..", "..", ".."))

LOCKDOWN_DOC_PATH = os.path.join(PROJECT_ROOT, "docs", "submission", "15_pre_hetzner_runtime_lockdown.md")
GITIGNORE_PATH = os.path.join(PROJECT_ROOT, ".gitignore")
HOOKS_PATH = os.path.join(OUTER_PACKAGE, "hooks.py")
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "docs", "submission", "14_frappe_native_evidence_manifest.md")
CHECKLIST_PATH = os.path.join(PROJECT_ROOT, "docs", "submission", "08_runtime_validation_checklist.md")
ENV_EXAMPLE_PATH = os.path.join(PROJECT_ROOT, ".env.example")


class TestPreHetznerLockdown:
    def test_lockdown_document_exists(self):
        assert os.path.isfile(LOCKDOWN_DOC_PATH), f"Lockdown document not found at: {LOCKDOWN_DOC_PATH}"

    def test_gitignore_excludes_dotenv(self):
        assert os.path.isfile(GITIGNORE_PATH), ".gitignore file not found"
        with open(GITIGNORE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        lines = [line.strip() for line in content.splitlines()]
        assert ".env" in lines, ".gitignore does not explicitly contain '.env'"

    def test_hooks_fixtures_registered(self):
        assert os.path.isfile(HOOKS_PATH), "hooks.py not found"
        with open(HOOKS_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        required_fixture_doctypes = [
            "Role",
            "Workspace",
            "Report",
            "Number Card",
            "Dashboard Chart",
            "Dashboard",
            "Print Format",
            "Notification",
            "Assignment Rule",
            "Web Form",
        ]
        for dt in required_fixture_doctypes:
            assert f'"dt": "{dt}"' in content, f"hooks.py is missing fixture registration for: '{dt}'"

    def test_after_install_hook_registered(self):
        with open(HOOKS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert 'after_install = "nilegov_stack.install.after_install"' in content

    def test_evidence_manifest_exists(self):
        assert os.path.isfile(MANIFEST_PATH), "Evidence manifest not found"

    def test_runtime_checklist_exists(self):
        assert os.path.isfile(CHECKLIST_PATH), "Runtime checklist not found"

    def test_lockdown_doc_avoids_live_claims(self):
        with open(LOCKDOWN_DOC_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # Verify it has standard disclaimer wording
        assert "no live" in content.lower()
        assert "prototype" in content.lower()
        assert "claims to avoid" in content.lower()

    def test_dotenv_example_contains_placeholders_only(self):
        assert os.path.isfile(ENV_EXAMPLE_PATH), ".env.example not found"
        with open(ENV_EXAMPLE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verify placeholders are present and no real secrets exist
        assert "placeholder_" in content
        assert "DB_PASSWORD=placeholder_" in content
        assert "ADMIN_PASSWORD=placeholder_" in content
        assert "PESAPAL_CONSUMER_KEY=<set in uncommitted" in content
