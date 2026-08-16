from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 50}, debug=True)
env.run(["main.py", "pass"])

print("Final state:")
final = env.steps[-1]
for i, s in enumerate(final):
    print(f"Player {i}: reward={s.reward}, status={s.status}")

# Check if there were any errors
print("\nLast 5 steps:")
for step in env.steps[-5:]:
    print(step)