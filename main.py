"""Kaggle Kaggriculture Agent - v7 Fixed"""

from kaggle_environments import make
from state_tracker import StateTracker
from route_planner import find_nearest_target, generate_movement_actions
from market_trader import MarketTrader
from animal_manager import AnimalManager

# Global instances
tracker = StateTracker()
trader = MarketTrader()
animal_mgr = AnimalManager()


def agent(obs):
    """
    Main agent function.

    Args:
        obs: Observation dictionary

    Returns:
        Dictionary with farmer, hands, and market actions
    """
    try:
        # Update state tracker
        tracker.update(obs)

        player = obs["player"]
        me = obs["farms"][player]
        private = obs["private"]
        day = obs["day"]

        fx, fy = me["farmer"]
        tile = me["tiles"][fy][fx]

        # Get market orders
        market = trader.plan_market_orders(obs, tracker, me["money"])

        # Farmer decision logic
        if tile is None and private["seeds"].get("WHEAT", 0) > 0:
            # Plant on empty tile if we have seeds
            farmer_action = ["PLANT"]
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
            crop_age = day - tile["planted_day"]
            if crop_age >= 4:
                # Harvest mature wheat
                farmer_action = ["HARVEST"]
            elif not tile["watered_today"]:
                # Water if not watered today
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

    except Exception as e:
        # Never crash
        print(f"Agent error: {e}")
        return {
            "farmer": ["PASS"],
            "hands": [],
            "market": []
        }


if __name__ == "__main__":
    # Test locally
    env = make("kaggriculture", configuration={"episodeSteps": 100}, debug=True)
    env.run(["main.py", "random"])
    print("Game completed!")
    print([(i, s.reward) for i, s in enumerate(env.steps[-1])])
