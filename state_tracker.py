"""
State Tracker for Kaggle Kaggriculture Competition
Tracks crops, animals, and farm state across turns.
"""

from typing import Dict, List, Optional, Tuple, Any


# Time to max yield for each crop type (in days)
CROP_MATURITY: Dict[str, int] = {
    "WHEAT": 4,
    "CARROT": 5,
    "MELON": 6,
}

# Ongoing crops that produce yield each day after maturity
ONGOING_CROPS: set = {"TOMATO", "STRAWBERRY"}


class StateTracker:
    """
    Tracks farm state across multiple turns.

    Maintains dictionaries of planted crops and animals, providing
    helper methods to query which need attention (watering, feeding,
    harvesting, etc.).
    """

    def __init__(self) -> None:
        """Initialize the state tracker with empty crop and animal dictionaries."""
        self.crops: Dict[Tuple[int, int], Dict[str, Any]] = {}
        self.animals: Dict[Tuple[int, int], Dict[str, Any]] = {}
        self.last_obs: Optional[Dict[str, Any]] = None

    def update(self, obs: Dict[str, Any]) -> None:
        """
        Update tracked state from a new observation.

        Scans all tiles on the player's farm and records crop and animal
        information. Removes entries for positions that no longer have
        crops or animals.

        Args:
            obs: The observation dictionary from the environment.
        """
        self.last_obs = obs
        player = obs["player"]
        me = obs["farms"][player]
        day = obs["day"]

        # Track which positions still have crops/animals
        current_crop_positions: set = set()
        current_animal_positions: set = set()

        # Scan all tiles
        tiles = me["tiles"]
        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):
                if tile is None:
                    continue

                if not isinstance(tile, dict):
                    continue

                position = (x, y)

                if tile.get("kind") == "PLANT":
                    # Track this crop
                    current_crop_positions.add(position)
                    self.crops[position] = {
                        "crop": tile["crop"],
                        "planted_day": tile["planted_day"],
                        "watered_today": tile["watered_today"],
                        "consecutive_unwatered": tile.get("consecutive_unwatered", 0),
                        "yield_units": tile.get("yield_units", 0),
                        "fertilized_until_day": tile.get("fertilized_until_day", -1),
                    }

                elif tile.get("kind") in ("COOP", "PASTURE") and "animal" in tile:
                    # Track this animal
                    current_animal_positions.add(position)
                    self.animals[position] = {
                        "animal": tile["animal"],
                        "yield_units": tile.get("yield_units", 0),
                        "fed_today": tile.get("fed_today", False),
                        "consecutive_unfed": tile.get("consecutive_unfed", 0),
                        "fertilizer_available": tile.get("fertilizer_available", False),
                    }

        # Remove entries for positions that no longer have crops/animals
        self.crops = {
            pos: data for pos, data in self.crops.items()
            if pos in current_crop_positions
        }
        self.animals = {
            pos: data for pos, data in self.animals.items()
            if pos in current_animal_positions
        }

    def get_crops_needing_water(self, day: int) -> List[Tuple[int, int]]:
        """
        Get crops that need watering, sorted by urgency.

        Returns positions where watered_today is False, sorted by
        consecutive_unwatered (highest first) to prioritize crops
        closest to dying.

        Args:
            day: The current game day.

        Returns:
            List of (x, y) tuples for crops needing water.
        """
        needing_water = [
            (pos, data) for pos, data in self.crops.items()
            if not data["watered_today"]
        ]

        # Sort by consecutive_unwatered (highest first = most urgent)
        needing_water.sort(key=lambda item: item[1]["consecutive_unwatered"], reverse=True)

        return [pos for pos, _ in needing_water]

    def get_crops_ready_to_harvest(self, day: int) -> List[Tuple[int, int]]:
        """
        Get crops that are ready to be harvested.

        For one-time crops (WHEAT, CARROT, MELON): ready when crop_age >= time_to_max_yield.
        For ongoing crops (TOMATO, STRAWBERRY): ready when yield_units > 0.

        Args:
            day: The current game day.

        Returns:
            List of (x, y) tuples for crops ready to harvest.
        """
        ready = []

        for pos, data in self.crops.items():
            crop_type = data["crop"]
            crop_age = day - data["planted_day"]

            if crop_type in CROP_MATURITY:
                # One-time crop: ready when mature
                if crop_age >= CROP_MATURITY[crop_type]:
                    ready.append(pos)

            elif crop_type in ONGOING_CROPS:
                # Ongoing crop: ready when there's yield to collect
                if data["yield_units"] > 0:
                    ready.append(pos)

        return ready

    def get_animals_needing_feed(self) -> List[Tuple[int, int]]:
        """
        Get animals that need to be fed.

        Returns positions where consecutive_unfed >= 1, indicating
        the animal missed at least one day of feeding.

        Returns:
            List of (x, y) tuples for animals needing feed.
        """
        return [
            pos for pos, data in self.animals.items()
            if data["consecutive_unfed"] >= 1
        ]

    def get_animals_ready_to_collect(self) -> List[Tuple[int, int]]:
        """
        Get animals that have products ready to collect.

        Returns positions where yield_units > 0.

        Returns:
            List of (x, y) tuples for animals ready to collect.
        """
        return [
            pos for pos, data in self.animals.items()
            if data["yield_units"] > 0
        ]

    def get_fertilizer_available(self) -> List[Tuple[int, int]]:
        """
        Get animal positions that can produce fertilizer.

        Returns positions where fertilizer_available is True.

        Returns:
            List of (x, y) tuples with available fertilizer.
        """
        return [
            pos for pos, data in self.animals.items()
            if data["fertilizer_available"]
        ]
