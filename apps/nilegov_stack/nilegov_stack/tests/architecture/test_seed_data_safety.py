# Pass 11B-8C: Static Seed Data Safety Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external integration.
#

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
PATCHES_DIR = os.path.join(OUTER_PACKAGE, "patches")


class TestSeedDataSafety:
    def test_seed_scripts_do_not_contain_secrets(self):
        for root, _, files in os.walk(PATCHES_DIR):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                    assert ".env" not in content, f"Secret reference (.env) found in patch {file}"
                    assert "secret" not in content.lower(), f"Secret reference (secret keyword) found in patch {file}"
                    assert "password" not in content.lower(), f"Password reference found in patch {file}"
                    assert "token" not in content.lower(), f"Token reference found in patch {file}"

    def test_seed_scripts_do_not_contain_live_urls(self):
        for root, _, files in os.walk(PATCHES_DIR):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                    assert "http://" not in content, f"Insecure URL found in patch {file}"
                    assert "https://" not in content, f"Secure URL found in patch {file}"

    def test_seed_scripts_use_fictional_personal_data(self):
        for root, _, files in os.walk(PATCHES_DIR):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Avoid real-looking personal email domains
                    assert "@gmail.com" not in content
                    assert "@yahoo.com" not in content
                    assert "@outlook.com" not in content

                    # Ensure phone numbers are fake mock sequences
                    assert "+256700123" not in content
                    assert "+25677123" not in content

    def test_seed_scripts_do_not_claim_live_government_integration(self):
        for root, _, files in os.walk(PATCHES_DIR):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                    assert "nira_live_connection" not in content
                    assert "ughub_live_gateway" not in content
                    assert "production_payment" not in content.lower()
