from kaggle_environments import make

def agent(obs):
    """
    Basic Kaggriculture agent - plants wheat, waters, harvests, and sells.
    """
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    
    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]
    
    market = []
    
    # Buy wheat seed on first turn if we have enough money
    step = obs.get("step", 0)
    if step == 0 and me["money"] >= 10:
        market.append(["BUY_SEED", "WHEAT", 1])
    
    # Sell any wheat in the shed
    wheat_in_shed = private["shed"].get("WHEAT", 0)
    if wheat_in_shed > 0:
        market.append(["SELL", "WHEAT", wheat_in_shed])
    
    # Farmer decision logic
    if tile is None and private["seeds"].get("WHEAT", 0) > 0:
        farmer_action = ["PLANT"]
    elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
        crop_age = obs["day"] - tile["planted_day"]
        if crop_age >= 4:
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