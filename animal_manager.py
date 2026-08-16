"""
Animal Manager for Kaggle Kaggriculture Competition
Handles animal care and structure building decisions.
"""

from typing import Any, Dict, List, Optional, Tuple


class AnimalManager:
    """
    Manages animal-related actions for the Kaggriculture agent.

    Handles feeding, collecting products, building structures,
    and deciding when to buy new animals.
    """

    def __init__(self) -> None:
        """Initialize the animal manager (no state needed)."""
        pass

    def plan_animal_actions(
        self,
        obs: Dict[str, Any],
        tracker: Any,
        farmer_pos: List[int],
        tile: Any,
    ) -> List[str]:
        """
        Plan actions when farmer is at a position.

        Handles actions for animal tiles (COOP/PASTURE) and determines
        if new animal structures should be built on empty tiles.

        Args:
            obs: The current observation dictionary.
            tracker: The StateTracker instance for farm state.
            farmer_pos: The farmer's position as [x, y].
            tile: The tile at the farmer's current position.

        Returns:
            List of action strings for the farmer.
        """
        actions: List[str] = []
        pos_tuple = (farmer_pos[0], farmer_pos[1])

        # Handle animal tiles (COOP or PASTURE)
        if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE"):
            animal_data = tracker.animals.get(pos_tuple)

            if animal_data is not None:
                # Priority 1: Feed hungry animals (prevent escape)
                if animal_data["consecutive_unfed"] >= 1:
                    actions.append("FEED")

                # Priority 2: Collect animal products (eggs/milk/wool)
                elif animal_data["yield_units"] > 0:
                    actions.append("HARVEST")

                # Priority 3: Collect fertilizer if available
                elif animal_data["fertilizer_available"]:
                    actions.append("COLLECT_FERTILIZER")

                # No action needed
                else:
                    actions.append("PASS")

        # Handle empty tiles - check if we should build animal structure
        elif tile is None:
            private = obs["private"]
            shed = private.get("shed", {})

            # Check if we have a goose and no coop
            if shed.get("GOOSE", 0) > 0:
                has_coop_with_goose = any(
                    data.get("animal") == "GOOSE"
                    for data in tracker.animals.values()
                )
                if not has_coop_with_goose:
                    actions.append("BUILD_COOP")

            # Check if we have a cow or sheep and no pasture
            if shed.get("COW", 0) > 0 or shed.get("SHEEP", 0) > 0:
                has_pasture_with_animal = any(
                    data.get("animal") in ("COW", "SHEEP")
                    for data in tracker.animals.values()
                )
                if not has_pasture_with_animal:
                    actions.append("BUILD_PASTURE")

        # Default: pass if no action determined
        if not actions:
            actions.append("PASS")

        return actions

    def should_buy_animal(
        self,
        obs: Dict[str, Any],
        tracker: Any,
        money: float,
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if we should buy a new animal.

        Makes purchasing decisions based on money, day, and current
        animal count.

        Args:
            obs: The current observation dictionary.
            tracker: The StateTracker instance for farm state.
            money: The player's current money.

        Returns:
            Tuple of (should_buy: bool, animal_type: str or None).

        Examples:
            >>> manager = AnimalManager()
            >>> manager.should_buy_animal(obs, tracker, 500)
            (True, "GOOSE")
        """
        day = obs["day"]
        animal_count = len(tracker.animals)

        # Priority 1: Buy goose (cheapest, good early income)
        if money >= 300 and day < 20 and animal_count < 3:
            return (True, "GOOSE")

        # Priority 2: Buy cow (good milk production)
        if money >= 400 and day < 15 and animal_count < 2:
            return (True, "COW")

        # Priority 3: Buy sheep (wool production)
        if money >= 500 and day < 15 and animal_count < 2:
            return (True, "SHEEP")

        return (False, None)
