from kaggle_environments import make
from state_tracker import StateTracker


# Global state tracker instance to persist across turns
tracker = StateTracker()

def agent(obs):
    """
    Kaggriculture agent using StateTracker for informed decisions.
    """
    # Update state tracker with latest observation
    tracker.update(obs)

    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]

    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]
    farmer_pos = (fx, fy)

    market = []

    # Buy wheat seed on first turn if we have enough money
    step = obs.get("step", 0)
    if step == 0 and me["money"] >= 10:
        market.append(["BUY_SEED", "WHEAT", 1])

    # Sell any wheat in the shed
    wheat_in_shed = private["shed"].get("WHEAT", 0)
    if wheat_in_shed > 0:
        market.append(["SELL", "WHEAT", wheat_in_shed])

    # Query state tracker for farm status
    crops_needing_water = tracker.get_crops_needing_water(day)
    crops_ready_to_harvest = tracker.get_crops_ready_to_harvest(day)

    # Farmer decision logic
    if tile is None and private["seeds"].get("WHEAT", 0) > 0:
        # Empty tile with seeds available: plant
        farmer_action = ["PLANT"]
    elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
        crop_age = day - tile["planted_day"]

        # Check if this crop is ready to harvest (uses state tracker data)
        if farmer_pos in crops_ready_to_harvest:
            farmer_action = ["HARVEST"]
        # Check if this crop needs watering (uses state tracker data)
        elif farmer_pos in crops_needing_water:
            farmer_action = ["WATER"]
        # Fallback: use direct tile inspection
        elif crop_age >= 4:
            farmer_action = ["HARVEST"]
        elif not tile["watered_today"]:
            farmer_action = ["WATER"]
        else:
            farmer_action = ["PASS"]
    else:
        farmer_action = ["PASS"]

    return {
        "farmer": farmer_action,
        "hands": [],
        "market": market
    }


if __name__ == "__main__":
    # Test the agent locally (shorter game for quick testing)
    env = make("kaggriculture", configuration={"episodeSteps": 100}, debug=True)
    env.run(["main.py", "random"])
    print("Game completed!")
    print([(i, s.reward) for i, s in enumerate(env.steps[-1])])