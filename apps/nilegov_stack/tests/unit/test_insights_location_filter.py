import unittest
from unittest.mock import patch, MagicMock

# Import the module that contains get_command_centre_filters
# Assuming it is in apps/nilegov_stack/nilegov_stack/interfaces/frappe/api/insights.py
from nilegov_stack.interfaces.frappe.api.insights import _get_location_options

class TestInsightsLocationFilter(unittest.TestCase):

    @patch("nilegov_stack.interfaces.frappe.api.insights.frappe.db.exists")
    @patch("nilegov_stack.interfaces.frappe.api.insights.frappe.get_all")
    def test_missing_district_doctype_returns_empty_list(self, mock_get_all, mock_exists):
        # Simulate that "NileGov District" DocType is missing
        mock_exists.return_value = False

        locations = _get_location_options()

        self.assertEqual(locations, [])
        mock_get_all.assert_not_called()

    @patch("nilegov_stack.interfaces.frappe.api.insights.frappe.db.exists")
    @patch("nilegov_stack.interfaces.frappe.api.insights.frappe.get_all")
    def test_active_districts_fetched_correctly(self, mock_get_all, mock_exists):
        # Simulate that "NileGov District" DocType exists
        mock_exists.return_value = True

        # Mock the frappe.get_all return value
        mock_get_all.return_value = ["Kampala", "Wakiso"]

        locations = _get_location_options()

        # Verify the list of locations matches what we expect
        self.assertEqual(locations, ["Kampala", "Wakiso"])

        # Verify the get_all call matches our contract requirements exactly
        mock_get_all.assert_called_once_with(
            "NileGov District",
            filters={"disabled": 0},
            pluck="district_name",
            order_by="district_name asc"
        )

    @patch("nilegov_stack.interfaces.frappe.api.insights.frappe.db.exists")
    @patch("nilegov_stack.interfaces.frappe.api.insights.frappe.get_all")
    def test_get_all_exception_returns_empty_list(self, mock_get_all, mock_exists):
        # Simulate that "NileGov District" DocType exists
        mock_exists.return_value = True

        # Simulate frappe.get_all raising an Exception
        mock_get_all.side_effect = Exception("DB error")

        locations = _get_location_options()

        # Verify it gracefully returns an empty list
        self.assertEqual(locations, [])
