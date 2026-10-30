import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)

S_0 = 100
sigma = 2
T = 1
dt = 0.005
A = 140
k = 1.5
steps = int(T / dt)
paths = 10000

def simulate(delta, gamma = 0.0):
    """Simulate n_paths market makers. delta = half-spread,
    gamma = inventory skew"""
    S = np.full(paths, S_0, dtype = float)
    cash = np.zeros(paths)
    inv = np.zeros(paths)

    for _ in range(steps):
        bid_dist = np.maximum(delta + gamma * inv, 0)
        ask_dist = np.maximum(delta - gamma * inv, 0)

        p_bid = np.minimum(A * np.exp(-k * bid_dist) * dt, 1)
        p_ask = np.minimum(A * np.exp(-k * ask_dist) * dt, 1)

        bid_fill = rng.random(paths) < p_bid
        ask_fill = rng.random(paths) < p_ask

        cash -= bid_fill * (S - bid_dist)
        cash += ask_fill * (S + ask_dist)
        inv += bid_fill.astype(int) - ask_fill.astype(int)

        S += sigma * np.sqrt(dt) * rng.standard_normal(paths)

    return (cash + inv * S)

delta_star = 1 / k
pnl = simulate(delta_star)
theory = 2 * A * delta_star *np.exp(-k * delta_star) * T
print ("--- Baseline (no skew) ---")
print (f"Mean PnL: {pnl.mean():.2f}")
print (f"Theory: {theory:.2f}")
print (f"PnL std: {pnl.std():.2f}")

deltas = np.linspace(0.1, 2.0, 20)
mean_pnl = np.array([simulate(d).mean() for d in deltas])
theory_curve = 2 * A * deltas * np.exp(-k * deltas) * T

plt.figure()
plt.plot(deltas, mean_pnl, "o", label = "Simulation")
plt.plot(deltas, theory_curve, "-", label = "2Aδe^(-kδ)T")
plt.xlabel("Half-spread δ")
plt.ylabel("Mean PnL")
plt.legend()
plt.savefig("pnl_vs_spread.png", dpi = 150)

best = deltas[mean_pnl.argmax()]
print ("\n---- Spread sweep ---")
print (f"Best simulated δ: {best:.2f}  (theory 1/k = {1/k:.2f})")
print (f"Diference: {abs(best - 1/k) / (1/k) * 100:.1f}%")

print("\n--- Inventory Skew ---")
base_mean, base_std = pnl.mean(), pnl.std()
gammas = [0.0, 0.01, 0.02, 0.05, 0.10]
stds = []
means = []
for g in gammas:
    result = simulate(delta_star, gamma = g)
    means.append(result.mean())
    stds.append(result.std())
    std_cut = (1 - result.std() / base_std) * 100
    mean_cost = (1 - result.mean() / base_mean) * 100
    print(f"gamma = {g:<5} mean = {result.mean():7.2f} std = {result.std():6.2f}"
          f"std cut = {std_cut:5.1f}% mean cost = {mean_cost:5.1f}%")

plt.figure()
plt.plot(stds, means, "o-")
for g, x, y in zip(gammas, stds, means):
    plt.annotate(f"γ = {g}", (x, y), textcoords = "offset points",
                 xytext = (10, -16), ha = "left")
plt.margins(x = 0.15, y = 0.12)
plt.xlabel("PnL standard deviation")
plt.ylabel("Mean PnL")
plt.savefig("risk_return.png", dpi = 150)
plt.show()