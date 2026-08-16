"""Simple animal manager - disabled for now."""


class AnimalManager:
    """Animal management - returns PASS for now (will be enhanced later)."""

    def __init__(self):
        """Initialize the manager."""
        pass

    def plan_animal_actions(self, obs, tracker, farmer_pos, tile):
        """
        Return animal actions for this turn.

        Args:
            obs: Observation dictionary
            tracker: StateTracker instance
            farmer_pos: Farmer position [x, y]
            tile: Current tile dict

        Returns:
            List of actions (currently just PASS)
        """
        return ["PASS"]

    def should_buy_animal(self, obs, tracker, money):
        """
        Decide whether to buy an animal.

        Args:
            obs: Observation dictionary
            tracker: StateTracker instance
            money: Current money

        Returns:
            Tuple of (should_buy: bool, animal_type: str or None)
        """
        # Don't buy animals yet - focus on crops first
        return (False, None)
