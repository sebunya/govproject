# Pytest Configuration
# Prototype simulation only. No live Government registry access.

import sys
from unittest.mock import MagicMock

# Inject mock frappe module globally for all unit and integration tests
if "frappe" not in sys.modules:
    sys.modules["frappe"] = MagicMock()
