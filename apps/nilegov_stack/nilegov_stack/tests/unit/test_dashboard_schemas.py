import os
import json
import pytest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
DASHBOARD_ROOT = os.path.join(PACKAGE_ROOT, "nilegov_stack", "nilegov_stack", "dashboard")

def test_dashboard_json_has_no_raw_dicts_in_scalar_fields():
    """All Dashboard JSON files must be recursively scanned. Child-table rows must not contain raw dict values in scalar fields."""
    if not os.path.isdir(DASHBOARD_ROOT):
        return

    for folder in os.listdir(DASHBOARD_ROOT):
        folder_path = os.path.join(DASHBOARD_ROOT, folder)
        if not os.path.isdir(folder_path):
            continue

        json_path = os.path.join(folder_path, f"{folder}.json")
        if not os.path.isfile(json_path):
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # check root fields
        for key, value in data.items():
            if key not in ("cards", "charts") and isinstance(value, dict):
                pytest.fail(f"Field '{key}' in dashboard {folder} contains a raw dict. Must be serialized string.")

        # check child table fields
        for child_type in ("cards", "charts"):
            for idx, child in enumerate(data.get(child_type, [])):
                for key, value in child.items():
                    if isinstance(value, dict):
                        pytest.fail(f"Child table '{child_type}' row {idx} field '{key}' in dashboard {folder} contains a raw dict.")
