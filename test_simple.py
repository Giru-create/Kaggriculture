from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 50})
env.run(["main.py", "pass"])
print("Done!")
final = env.steps[-1]
for i, s in enumerate(final):
    print(f"Player {i}: reward={s.reward}, status={s.status}")