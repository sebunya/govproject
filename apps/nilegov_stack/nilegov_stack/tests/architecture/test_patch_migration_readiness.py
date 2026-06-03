# Pass 11B-8C: Static Patch Migration Readiness Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external integration.
#

import importlib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
PATCHES_TXT_PATH = os.path.join(OUTER_PACKAGE, "patches.txt")


class TestPatchMigrationReadiness:
    def test_patches_txt_exists(self):
        assert os.path.isfile(PATCHES_TXT_PATH), f"patches.txt not found at: {PATCHES_TXT_PATH}"

    def test_patches_in_patches_txt_exist_and_have_execute(self):
        with open(PATCHES_TXT_PATH, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Verify patch file existence
            module_parts = line.split(".")
            # e.g., 'nilegov_stack.patches.seed_roles' -> patches/seed_roles.py
            filename = f"{module_parts[-1]}.py"
            file_path = os.path.join(OUTER_PACKAGE, "patches", filename)
            assert os.path.isfile(file_path), f"Patch module file {filename} does not exist at {file_path}"

            # Import the module to check execute function exists
            try:
                module = importlib.import_module(line)
                assert hasattr(module, "execute"), f"Patch module {line} is missing execute() function"
                assert callable(module.execute), f"execute in patch {line} is not callable"
            except ImportError as e:
                # Fallback check: parse file contents for def execute
                with open(file_path, "r", encoding="utf-8") as pf:
                    pcontent = pf.read()
                assert "def execute(" in pcontent, f"Patch {line} does not define execute() function"
