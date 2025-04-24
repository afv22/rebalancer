from src.get_rebalance_amounts import get_rebalance_amounts

def main():
    # Fetch holdings
    holdings = []

    # Process allocations
    target_allocations = {}
    rebalance_amounts = get_rebalance_amounts(holdings, target_allocations)

    # Check if any asset is outside the allowed window
    for asset in rebalance_amounts:
        if asset['absolute_difference'] >= 0.05:
            break
        if asset['relative_difference'] >= 0.25:
            break
    else:
        return

    # Alert me or automatically rebalance
    pass

    
if __name__ == "__main__":
    main()
