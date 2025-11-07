# grid_savings_simulation.py
import numpy as np

def simulate_grid_efficiency(hours=24, random_seed=42):
    np.random.seed(random_seed)
    demand = np.random.uniform(80, 120, hours)
    solar = np.random.uniform(30, 60, hours)
    wind = np.random.uniform(20, 50, hours)

    # Baseline grid: no predictive balancing
    baseline_storage = np.clip(solar + wind - demand, -20, 20)
    baseline_loss = np.abs(baseline_storage).sum()

    # AEI: coherence-weighted orchestration
    forecast = (0.6 * np.roll(demand, -1)) + (0.4 * demand)
    aei_storage = np.clip((solar + wind - forecast) * 0.7, -20, 20)
    aei_loss = np.abs(aei_storage).sum()

    savings = (1 - aei_loss / baseline_loss) * 100
    return baseline_loss, aei_loss, savings

if __name__ == "__main__":
    base, aei, savings = simulate_grid_efficiency()
    print(f"Baseline Energy Waste: {base:.2f}")
    print(f"AEI-Optimized Energy Waste: {aei:.2f}")
    print(f"Estimated Grid Savings: {savings:.1f}%")
