import pandas as pd
from src.classes.holding import Holding
from src.utils import is_prod

TARGET_ALLOCATIONS = {"VOO": 0.55, "VXUS": 0.30, "GLDM": 0.05, "VGIT": 0.10}
SANDBOX_TARGET_ALLOCATIONS = {"U S Dollar": 0.30, "NHX105509": 0.05, "CAMYX": 0.65}


def get_rebalance_amounts(holdings: list[Holding]) -> pd.DataFrame:
    """
    Calculate rebalancing amounts for a portfolio to match target allocations.

    Parameters:
    holdings (list): List of dictionaries, each with keys 'symbol', 'type', 'price', and 'value'
    is_prod (bool): Whether to run with production data. Determines which assets are tracked.

    Returns:
    Dataframe: df containing rebalancing instructions
    """
    target_allocations = TARGET_ALLOCATIONS if is_prod() else SANDBOX_TARGET_ALLOCATIONS

    if sum(target_allocations.values()) != 1:
        raise ValueError("Target allocations must sum to 1.0")

    total_value = sum(holding.value for holding in holdings)

    rows = []
    for holding in holdings:
        current_allocation = holding.value / total_value

        if holding.symbol in target_allocations:
            target_allocation = target_allocations[holding.symbol]
            absolute_difference = target_allocation - current_allocation
            relative_difference = absolute_difference / target_allocation
        else:
            target_allocation = 0
            absolute_difference = -current_allocation
            relative_difference = 1

        rebalance_value = absolute_difference * total_value

        row_data = {
            "symbol": holding.symbol,
            "current_value": holding.value,
            "target_allocation": target_allocation,
            "current_allocation": current_allocation,
            "absolute_difference": absolute_difference,
            "relative_difference": relative_difference,
            "rebalance_value": rebalance_value,
            "rebalance_quantity": (
                rebalance_value // holding.price if holding.price else 0
            ),
        }
        rows.append(row_data)

    return pd.DataFrame(rows)
