from kaggle_environments import make

print("Running 5 games against random agent...")
wins = 0
losses = 0
ties = 0

for i in range(5):
    env = make("kaggriculture", configuration={"episodeSteps": 720})
    env.run(["main.py", "random"])
    
    final = env.steps[-1]
    p0_money = final[0].reward
    p1_money = final[1].reward
    
    if p0_money > p1_money:
        wins += 1
        result = "WIN"
    elif p0_money < p1_money:
        losses += 1
        result = "LOSS"
    else:
        ties += 1
        result = "TIE"
    
    print(f"Game {i+1}: {result} (${p0_money:.0f} vs ${p1_money:.0f})")

print(f"\nSummary: {wins}W - {losses}L - {ties}T")