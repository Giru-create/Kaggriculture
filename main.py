"""
Kaggle Kaggriculture Agent
A farming simulation agent that plants, waters, harvests, and trades.
"""

from kaggle_environments import make
from state_tracker import StateTracker
from route_planner import find_nearest_target, generate_movement_actions
from market_trader import MarketTrader
from animal_manager import AnimalManager


# Global instances to persist across turns
tracker = StateTracker()
trader = MarketTrader()
animal_mgr = AnimalManager()


def should_buy_land(me, money):
    """
    Decide whether to buy land expansion.

    Args:
        me: The player's farm data.
        money: Current money.

    Returns:
        True if should buy next quadrant, False otherwise.
    """
    quadrants = len(me.get("unlocked_quadrants", []))

    # Cost progression: $1k, $2k, $4k
    if quadrants == 1:
        cost = 1000
    elif quadrants == 2:
        cost = 2000
    elif quadrants == 3:
        cost = 4000
    else:
        return False  # Already have all 4 quadrants

    # Buy if we have 2x the cost (to be safe) and it's early-mid game
    if money >= cost * 2 and quadrants < 3:
        return True

    return False


def agent(obs):
    """
    Main agent function that decides actions for each turn.

    Integrates StateTracker for farm awareness, RoutePlanner for movement,
    and MarketTrader for economic decisions.

    Args:
        obs: Observation dictionary containing game state.

    Returns:
        Dictionary with "farmer", "hands", and "market" action lists.
    """
    try:
        # Update state tracker with latest observation
        tracker.update(obs)

        player = obs["player"]
        me = obs["farms"][player]
        private = obs["private"]
        day = obs["day"]

        fx, fy = me["farmer"]
        tile = me["tiles"][fy][fx]
        farmer_pos = (fx, fy)

        # Get market orders from trader
        market = trader.plan_market_orders(obs, tracker, me["money"])

        # Land expansion logic
        if should_buy_land(me, me["money"]):
            market.append(["BUY_LAND"])

        # Buy animals if needed
        should_buy, animal_type = animal_mgr.should_buy_animal(obs, tracker, me["money"])
        if should_buy and animal_type:
            market.append(["BUY_ANIMAL", animal_type, 1])

        # Query state tracker for farm status
        unwatered_crops = tracker.get_crops_needing_water(day)
        ready_crops = tracker.get_crops_ready_to_harvest(day)

        # Farmer decision logic
        # Check if standing on animal tile
        is_animal_tile = (
            isinstance(tile, dict)
            and tile.get("kind") in ["COOP", "PASTURE"]
            and tile.get("animal")
        )

        if is_animal_tile:
            # Use animal manager for animal tiles
            animal_actions = animal_mgr.plan_animal_actions(obs, tracker, [fx, fy], tile)
            farmer_action = animal_actions if animal_actions else ["PASS"]

        # Priority 1: Harvest ready crops at current position
        elif farmer_pos in ready_crops:
            farmer_action = ["HARVEST"]

        # Priority 2: Water crops at current position if needed
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
            if not tile.get("watered_today", False):
                farmer_action = ["WATER"]
            else:
                farmer_action = ["PASS"]

        # Priority 3: Plant seeds on empty tile
        elif tile is None and private["seeds"].get("WHEAT", 0) > 0:
            farmer_action = ["PLANT"]

        # Priority 4: Move toward nearest unwatered crop
        elif unwatered_crops:
            target = find_nearest_target([fx, fy], unwatered_crops)
            if target and (target[0] != fx or target[1] != fy):
                moves = generate_movement_actions([fx, fy], list(target))
                farmer_action = [moves[0]] if moves else ["PASS"]
            else:
                farmer_action = ["PASS"]

        # Default: pass
        else:
            farmer_action = ["PASS"]

        return {
            "farmer": farmer_action,
            "hands": [],
            "market": market
        }

    except Exception as e:
        # Never crash - return pass actions on any error
        print(f"Agent error: {e}")
        return {
            "farmer": ["PASS"],
            "hands": [],
            "market": []
        }


if __name__ == "__main__":
    # Test the agent locally (shorter game for quick testing)
    env = make("kaggriculture", configuration={"episodeSteps": 100}, debug=True)
    env.run(["main.py", "random"])
    print("Game completed!")
    print([(i, s.reward) for i, s in enumerate(env.steps[-1])])
