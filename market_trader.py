"""Simple market trader - fixed version for Kaggle Kaggriculture."""


class MarketTrader:
    """Basic market logic - buy seeds early, sell excess wheat."""

    def __init__(self):
        """Initialize the trader."""
        pass

    def plan_market_orders(self, obs, tracker, money):
        """
        Return market orders for this turn.

        Args:
            obs: Observation dictionary
            tracker: StateTracker instance
            money: Current money

        Returns:
            List of market orders
        """
        orders = []
        private = obs["private"]
        day = obs["day"]
        step = obs.get("step", 0)

        # Buy wheat seeds on first turn only (step 0)
        if step == 0 and money >= 10:
            orders.append(["BUY_SEED", "WHEAT", 5])

        # Sell excess wheat (keep 10 for animal feed later)
        wheat_in_shed = private["shed"].get("WHEAT", 0)
        if wheat_in_shed > 20:
            orders.append(["SELL", "WHEAT", wheat_in_shed - 10])

        return orders
