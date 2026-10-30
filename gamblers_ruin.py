import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)

p = 0.49
start = 10
target = 20
trials = 1000000

money = np.full(trials, start)
active = np.ones(trials, dtype=bool)

while active.any():
    n_active = active.sum()
    steps = np.where(rng.random(n_active) < p, 1, -1)
    money[active] += steps
    active = (money > 0) & (money < target)

ruined = (money == 0).mean()
print(f"Estimated ruin probability: {ruined:.4f}")

q = 1 - p
r = q / p
i = np.arange(0, target + 1)
exact = (r**i - r**target) / (1 - r**target)

print(f"Exact ruin probability:     {exact[start]:.4f}")
print(f"Difference:                 {abs(ruined - exact[start]):.4f}")

def simulate(n):
    money = np.full(n, start)
    active = np.ones(n, dtype=bool)
    while active.any():
        n_active = active.sum()
        steps = np.where(rng.random(n_active) < p, 1, -1)
        money[active] += steps
        active = (money > 0) & (money < target)
    return (money == 0).mean()

N_values = 10 ** np.arange(2, 7)
errors = []
for n in N_values:
    estimates = [simulate(n) for _ in range(20)]
    errors.append(np.mean(np.abs(np.array(estimates) - exact[start])))

plt.loglog(N_values, errors, "o-", label = "Simulation error")
plt.loglog(N_values, 0.5 / np.sqrt(N_values), "--", label = "1/√N reference")
plt.xlabel("Number of trials N")
plt.ylabel("Mean absolute error")
plt.legend()
plt.savefig("error_vs_N.png", dpi=150)
plt.show()