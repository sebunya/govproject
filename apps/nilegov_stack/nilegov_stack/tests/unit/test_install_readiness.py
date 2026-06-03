# Pass 11B-8B: Unit Tests for Installation Hook Readiness
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external integration.
#

import pytest
from nilegov_stack.install import get_canonical_roles, get_install_readiness_summary


def test_get_canonical_roles():
    roles = get_canonical_roles()
    assert isinstance(roles, list)
    assert len(roles) == 8
    assert "NileGov Citizen Officer" in roles
    assert "NileGov System Manager" in roles


def test_get_install_readiness_summary():
    summary = get_install_readiness_summary()
    assert isinstance(summary, dict)
    assert summary["status"] == "Ready"
    assert summary["pesapal_mode"] == "sandbox"
    assert summary["live_registry_connection"] == "disabled"
    assert summary["external_notifications"] == "disabled"
    assert "manual_setup_required" in summary

    # Ensure no secrets or API keys reside in the summary payload
    for k, v in summary.items():
        assert "secret" not in str(v).lower()
        assert "token" not in str(v).lower()
        assert "password" not in str(v).lower()
