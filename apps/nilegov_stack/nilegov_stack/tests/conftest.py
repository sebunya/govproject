# Pytest Configuration
# Prototype simulation only. No live Government registry access.

import sys
from unittest.mock import MagicMock

# Inject mock frappe module globally for all unit and integration tests
if "frappe" not in sys.modules:
    mock_frappe = MagicMock()
    def mock_whitelist(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator
    mock_frappe.whitelist = mock_whitelist
    sys.modules["frappe"] = mock_frappe
