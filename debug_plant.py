from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 50}, debug=True)
env.run(["main.py", "pass"])

# Check what happened
print("Step 0-10 actions:")
for i, step in enumerate(env.steps[:10]):
    if i % 2 == 0:  # Player 0's turn
        action = step[0]["action"]
        obs = step[0]["observation"]
        private = obs["private"]
        print(f"Step {i}: {action}")
        print(f"  Seeds: {private['seeds']}")
        print(f"  Money: {obs['farms'][obs['player']]['money']}")