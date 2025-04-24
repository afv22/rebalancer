from collections import Counter


def get_rebalance_amounts(
    holdings: list[dict[str, str | float]],
    target_allocations: dict[str, float],
) -> list[dict[str, str | float]]:
    """
    Calculate rebalancing amounts for a portfolio to match target allocations.

    Parameters:
    holdings (list): List of dictionaries, each with keys 'asset' and 'value'
    target_allocations (dict): Dictionary mapping asset names to target percentage allocations
                              (decimal values that sum to 1.0)

    Returns:
    list: List of dictionaries containing rebalancing instructions
    """
    if sum(target_allocations.values()) != 1:
        raise ValueError("Target allocations must sum to 1.0")

    total_value = sum(holding["value"] for holding in holdings)

    asset_values = Counter()
    for holding in holdings:
        asset_values[holding["asset"]] += holding["value"]

    rebalance = []
    for asset, value in asset_values.items():
        current_allocation = value / total_value
        absolute_difference = abs(target_allocations[asset] - current_allocation)
        relative_difference = absolute_difference / target_allocations[asset]
        asset_rebalance = {
            "asset": asset,
            "absolute_difference": round(absolute_difference, 3),
            "relative_difference": round(relative_difference, 3),
            "value": round(absolute_difference * total_value, 2),
        }
        rebalance.append(asset_rebalance)

    return rebalance
