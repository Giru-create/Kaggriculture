"""
Market Trader for Kaggle Kaggriculture Competition
Handles market orders and price calculations.
"""

import math
from typing import Any, Dict, List, Optional


# Default market parameters for all products
DEFAULT_MARKET_PARAMS: Dict[str, Dict[str, Any]] = {
    "WHEAT": {
        "base": 25, "I0": 10000, "T": 400,
        "below_func": "sqrt", "below_target": 0.8,
        "above_func": "log", "above_target": 0.2,
    },
    "CARROT": {
        "base": 35, "I0": 10000, "T": 450,
        "below_func": "hinge", "below_target": 1.0,
        "above_func": "sqrt", "above_target": 0.7,
    },
    "TOMATO": {
        "base": 60, "I0": 10000, "T": 200,
        "below_func": "hinge", "below_target": 0.4,
        "above_func": "sqrt", "above_target": 0.6,
    },
    "STRAWBERRY": {
        "base": 120, "I0": 10000, "T": 100,
        "below_func": "sqrt", "below_target": 0.7,
        "above_func": "linear", "above_target": 1.6,
    },
    "MELON": {
        "base": 250, "I0": 10000, "T": 300,
        "below_func": "log", "below_target": 0.2,
        "above_func": "sq", "above_target": 3.6,
    },
    "EGG": {
        "base": 50, "I0": 10000, "T": 332,
        "below_func": "hinge", "below_target": 0.4,
        "above_func": "log", "above_target": 0.2,
    },
    "MILK": {
        "base": 160, "I0": 10000, "T": 122,
        "below_func": "sqrt", "below_target": 0.6,
        "above_func": "linear", "above_target": 1.6,
    },
    "WOOL": {
        "base": 200, "I0": 10000, "T": 105,
        "below_func": "log", "below_target": 0.2,
        "above_func": "sq", "above_target": 3.2,
    },
    "FERTILIZER": {
        "base": 100, "I0": 10000, "T": 200,
        "below_func": "linear", "below_target": 0.4,
        "above_func": "linear", "above_target": 0.4,
    },
}


class MarketTrader:
    """
    Handles market operations for the Kaggriculture agent.

    Manages buying/selling decisions and price calculations based on
    current inventory and market conditions.
    """

    def __init__(self) -> None:
        """Initialize the market trader (no state needed for now)."""
        pass

    def plan_market_orders(
        self,
        obs: Dict[str, Any],
        tracker: Any,
        money: float,
    ) -> List[List]:
        """
        Plan market orders based on current state.

        Determines what to buy and sell based on inventory levels,
        money available, and game progress.

        Args:
            obs: The current observation dictionary.
            tracker: The StateTracker instance for farm state.
            money: The player's current money.

        Returns:
            List of market orders, each being a list like ["SELL", "WHEAT", 10].
        """
        private = obs["private"]
        wheat_in_shed = private["shed"].get("WHEAT", 0)
        fertilizer_in_shed = private["shed"].get("FERTILIZER", 0)
        seeds = private["seeds"]
        day = obs["day"]

        orders: List[List] = []

        # Sell logic: sell excess wheat (keep 20 for animal feed)
        if wheat_in_shed > 50 and money < 500:
            sell_amount = wheat_in_shed - 20
            orders.append(["SELL", "WHEAT", sell_amount])

        # Sell logic: sell excess fertilizer (keep 5 for crops)
        if fertilizer_in_shed > 10 and money < 300:
            sell_amount = fertilizer_in_shed - 5
            orders.append(["SELL", "FERTILIZER", sell_amount])

        # Buy logic: buy wheat seeds if needed (early game)
        if seeds.get("WHEAT", 0) == 0 and money >= 10 and day < 10:
            orders.append(["BUY_SEED", "WHEAT", 5])

        # Buy logic: buy carrot seeds if needed (early game)
        if seeds.get("CARROT", 0) == 0 and money >= 20 and day < 10:
            orders.append(["BUY_SEED", "CARROT", 5])

        # Buy logic: buy a goose if we have enough money and no animals (early game)
        if money >= 1000 and len(tracker.animals) == 0 and day < 15:
            orders.append(["BUY_ANIMAL", "GOOSE", 1])

        return orders

    def calculate_price(
        self,
        product: str,
        inventory: int,
        market_params: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Calculate the current price for a product.

        Implements the Kaggriculture price function based on supply/demand.
        Price decreases when inventory is high (glut) and increases when
        inventory is low (scarcity).

        Args:
            product: The product name (e.g., "WHEAT", "CARROT").
            inventory: The current global inventory level.
            market_params: Optional custom market parameters. If None,
                          uses DEFAULT_MARKET_PARAMS.

        Returns:
            The calculated price in dollars (minimum $1, rounded to int).

        Examples:
            >>> trader = MarketTrader()
            >>> trader.calculate_price("WHEAT", 10000)
            25
            >>> trader.calculate_price("WHEAT", 5000)
            31
        """
        if market_params is None:
            market_params = DEFAULT_MARKET_PARAMS

        params = market_params.get(product)
        if params is None:
            return 1  # Default minimum price for unknown products

        base = params["base"]
        I0 = params["I0"]
        T = params["T"]
        below_func = params["below_func"]
        below_target = params["below_target"]
        above_func = params["above_func"]
        above_target = params["above_target"]

        # Determine if we're in scarcity (+1) or glut (-1)
        if inventory < I0:
            sign = 1
            func_name = below_func
            target = below_target
        else:
            sign = -1
            func_name = above_func
            target = above_target

        # Calculate the distance from equilibrium
        x = abs(inventory - I0)

        # Apply shape function and calculate amplitude
        f_T = self._apply_shape(func_name, T, T)
        if f_T == 0:
            return max(1, base)

        amp = target * base / f_T

        # Calculate final price
        f_x = self._apply_shape(func_name, x, T)
        price = base + sign * amp * f_x

        # Floor at $1 and round to nearest integer
        return max(1, round(price))

    def _apply_shape(self, func_name: str, x: float, T: float = 1.0) -> float:
        """
        Apply a shape function for price calculation.

        Args:
            func_name: The function name ("sqrt", "log", "linear", "hinge", "sq").
            x: The input value.
            T: The threshold parameter for hinge function.

        Returns:
            The result of applying the shape function.

        Raises:
            ValueError: If func_name is not recognized.
        """
        if func_name == "sqrt":
            return math.sqrt(x)
        elif func_name == "log":
            return math.log(1 + x)
        elif func_name == "linear":
            return x
        elif func_name == "hinge":
            # u + 8 * max(0, u-1)^2 where u = x/T
            u = x / T if T != 0 else x
            return u + 8 * max(0, u - 1) ** 2
        elif func_name == "sq":
            return x ** 2
        else:
            raise ValueError(f"Unknown shape function: {func_name}")
