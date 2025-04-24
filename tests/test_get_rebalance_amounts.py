import unittest
from unittest.mock import patch
from src.get_rebalance_amounts import get_rebalance_amounts


class TestGetRebalanceAmounts(unittest.TestCase):
    def test_basic_rebalance(self):
        """Test a simple rebalancing scenario with three assets."""
        holdings = [
            {"asset": "VTI", "account": "Taxable", "value": 6000},
            {"asset": "VXUS", "account": "Taxable", "value": 3000},
            {"asset": "BND", "account": "401k", "value": 1000},
        ]
        target_allocations = {
            "VTI": 0.5,  # 50% US stocks
            "VXUS": 0.3,  # 30% International stocks
            "BND": 0.2,  # 20% Bonds
        }

        result = get_rebalance_amounts(holdings, target_allocations)

        # Expected results
        # VTI: Current = 6000/10000 = 0.6, Target = 0.5, Absolute diff = 0.1, Relative diff = 0.2, Value = 1000
        # VXUS: Current = 3000/10000 = 0.3, Target = 0.3, Absolute diff = 0, Relative diff = 0, Value = 0
        # BND: Current = 1000/10000 = 0.1, Target = 0.2, Absolute diff = 0.1, Relative diff = 0.5, Value = 1000

        self.assertEqual(len(result), 3)

        vti_result = next(r for r in result if r["asset"] == "VTI")
        self.assertEqual(vti_result["absolute_difference"], 0.1)
        self.assertEqual(vti_result["relative_difference"], 0.2)
        self.assertEqual(vti_result["value"], 1000.0)

        vxus_result = next(r for r in result if r["asset"] == "VXUS")
        self.assertEqual(vxus_result["absolute_difference"], 0.0)
        self.assertEqual(vxus_result["relative_difference"], 0.0)
        self.assertEqual(vxus_result["value"], 0.0)

        bnd_result = next(r for r in result if r["asset"] == "BND")
        self.assertEqual(bnd_result["absolute_difference"], 0.1)
        self.assertEqual(bnd_result["relative_difference"], 0.5)
        self.assertEqual(bnd_result["value"], 1000.0)

    def test_multiple_accounts(self):
        """Test rebalancing with duplicate assets across multiple accounts."""
        holdings = [
            {"asset": "VTI", "account": "Taxable", "value": 5000},
            {"asset": "VTI", "account": "Roth IRA", "value": 5000},
            {"asset": "VXUS", "account": "Taxable", "value": 5000},
            {"asset": "BND", "account": "401k", "value": 5000},
        ]
        target_allocations = {
            "VTI": 0.6,  # 60% US stocks
            "VXUS": 0.2,  # 20% International stocks
            "BND": 0.2,  # 20% Bonds
        }

        result = get_rebalance_amounts(holdings, target_allocations)

        # Expected results
        # VTI: Current = 10000/20000 = 0.5, Target = 0.6, Absolute diff = 0.1, Relative diff = 0.167, Value = 2000
        # VXUS: Current = 5000/20000 = 0.25, Target = 0.2, Absolute diff = 0.05, Relative diff = 0.25, Value = 1000
        # BND: Current = 5000/20000 = 0.25, Target = 0.2, Absolute diff = 0.05, Relative diff = 0.25, Value = 1000

        self.assertEqual(len(result), 3)

        vti_result = next(r for r in result if r["asset"] == "VTI")
        self.assertEqual(vti_result["absolute_difference"], 0.1)
        self.assertAlmostEqual(vti_result["relative_difference"], 0.167, places=3)
        self.assertEqual(vti_result["value"], 2000.0)

        vxus_result = next(r for r in result if r["asset"] == "VXUS")
        self.assertEqual(vxus_result["absolute_difference"], 0.05)
        self.assertEqual(vxus_result["relative_difference"], 0.25)
        self.assertEqual(vxus_result["value"], 1000.0)

    def test_zero_value_holding(self):
        """Test rebalancing with a holding that has zero value."""
        holdings = [
            {"asset": "VTI", "account": "Taxable", "value": 10000},
            {"asset": "VXUS", "account": "Taxable", "value": 0},
            {"asset": "BND", "account": "401k", "value": 0},
        ]
        target_allocations = {"VTI": 0.5, "VXUS": 0.3, "BND": 0.2}

        result = get_rebalance_amounts(holdings, target_allocations)

        # Expected results
        # VTI: Current = 10000/10000 = 1.0, Target = 0.5, Absolute diff = 0.5, Relative diff = 1.0, Value = 5000
        # VXUS: Current = 0/10000 = 0, Target = 0.3, Absolute diff = 0.3, Relative diff = 1.0, Value = 3000
        # BND: Current = 0/10000 = 0, Target = 0.2, Absolute diff = 0.2, Relative diff = 1.0, Value = 2000

        self.assertEqual(len(result), 3)

        vti_result = next(r for r in result if r["asset"] == "VTI")
        self.assertEqual(vti_result["absolute_difference"], 0.5)
        self.assertEqual(vti_result["relative_difference"], 1.0)
        self.assertEqual(vti_result["value"], 5000.0)

        vxus_result = next(r for r in result if r["asset"] == "VXUS")
        self.assertEqual(vxus_result["absolute_difference"], 0.3)
        self.assertEqual(vxus_result["relative_difference"], 1.0)
        self.assertEqual(vxus_result["value"], 3000.0)

    def test_invalid_target_allocations(self):
        """Test that the function raises an error when target allocations don't sum to 1."""
        holdings = [{"asset": "VTI", "account": "Taxable", "value": 10000}]
        target_allocations = {"VTI": 0.9}  # Doesn't sum to 1

        with self.assertRaises(ValueError) as context:
            get_rebalance_amounts(holdings, target_allocations)

        self.assertTrue("Target allocations must sum to 1.0" in str(context.exception))

    def test_empty_holdings(self):
        """Test rebalancing with empty holdings list."""
        holdings = []
        target_allocations = {"VTI": 0.6, "VXUS": 0.2, "BND": 0.2}

        # This should not raise an error, but return an empty list
        # since total_value will be 0 and no calculations will be performed
        result = get_rebalance_amounts(holdings, target_allocations)
        self.assertEqual(result, [])

    def test_rounding(self):
        """Test that rounding works as expected."""
        holdings = [
            {"asset": "VTI", "account": "Taxable", "value": 10000},
            {"asset": "VXUS", "account": "Taxable", "value": 20000},
            {"asset": "BND", "account": "401k", "value": 30000},
        ]
        target_allocations = {
            "VTI": 0.333333,  # Should be rounded in output
            "VXUS": 0.333333,
            "BND": 0.333334,
        }

        result = get_rebalance_amounts(holdings, target_allocations)

        for item in result:
            # Check that rounding occurred to 3 decimal places
            self.assertLessEqual(
                len(str(item["absolute_difference"]).split(".")[-1]), 3
            )
            self.assertLessEqual(
                len(str(item["relative_difference"]).split(".")[-1]), 3
            )
            # Value should be rounded to 2 decimal places (cents)
            self.assertLessEqual(len(str(item["value"]).split(".")[-1]), 2)

    def test_case_sensitivity(self):
        """Test that assets with different case are treated as different assets."""
        holdings = [
            {"asset": "VTI", "account": "Taxable", "value": 5000},
            {"asset": "vti", "account": "Roth IRA", "value": 5000},
        ]
        target_allocations = {"VTI": 0.5, "vti": 0.5}

        result = get_rebalance_amounts(holdings, target_allocations)

        # Should have two separate results
        self.assertEqual(len(result), 2)
        self.assertTrue(any(r["asset"] == "VTI" for r in result))
        self.assertTrue(any(r["asset"] == "vti" for r in result))

    def test_missing_target_allocation(self):
        """Test scenario where a holding exists but has no target allocation."""
        holdings = [
            {"asset": "VTI", "account": "Taxable", "value": 5000},
            {"asset": "VXUS", "account": "Taxable", "value": 5000},
        ]
        target_allocations = {
            "VTI": 1.0,
            # VXUS is missing
        }

        # This should raise a KeyError because VXUS doesn't have a target allocation
        with self.assertRaises(KeyError):
            get_rebalance_amounts(holdings, target_allocations)

    @patch("builtins.round")
    def test_rounding_calls(self, mock_round):
        """Test that the round function is called with the correct arguments."""
        holdings = [
            {"asset": "VTI", "account": "Taxable", "value": 10000},
        ]
        target_allocations = {
            "VTI": 1.0,
        }

        # Reset mock to clear call history
        mock_round.reset_mock()

        get_rebalance_amounts(holdings, target_allocations)

        # Since current_allocation equals target_allocation,
        # absolute_difference and relative_difference are 0
        # So round is called 3 times (all with 0)
        expected_calls = [
            unittest.mock.call(0, 3),  # absolute_difference
            unittest.mock.call(0, 3),  # relative_difference
            unittest.mock.call(0, 2),  # value
        ]

        mock_round.assert_has_calls(expected_calls)


if __name__ == "__main__":
    unittest.main()
