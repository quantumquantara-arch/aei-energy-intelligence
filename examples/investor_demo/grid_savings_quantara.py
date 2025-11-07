# examples/investor_demo/grid_savings_quantara.py
# Quantara-style investor demo: κ-coherence + Veyn temporal operator
# Goal: show baseline vs AEI orchestration and the ~50% waste reduction

import numpy as np

# ---------------------------
# Quantara-style primitives
# ---------------------------

def veyn_operator(series: np.ndarray, lead_weight: float = 0.6) -> np.ndarray:
    """
    Veyn temporal operator (very lightweight version):
    Combines present signal with a forward-looking (lead) component.
    lead_weight in [0,1] tilts toward the future; (1-lead_weight) keeps the present.
    We roll by -1 to represent a one-step "peek" into the immediate future.
    """
    return lead_weight * np.roll(series, -1) + (1.0 - lead_weight) * series


def kappa_coherence(balance: np.ndarray) -> float:
    """
    κ (kappa) ~ alignment metric in [0,1]
    We convert deviation magnitude into a unit interval by normalizing
    against a soft scale (median absolute deviation + small epsilon) and
    then map to coherence via 1 / (1 + normalized_deviation).
    The mean over time is the κ score.
    """
    eps = 1e-6
    mad = np.median(np.abs(balance - np.median(balance))) + eps
    norm_dev = np.abs(balance) / (mad + 1.0)  # soft normalization, stable across scenarios
    k = np.mean(1.0 / (1.0 + norm_dev))
    return float(np.clip(k, 0.0, 1.0))


def tci_temporal_coherence(series: np.ndarray, alpha: float = 0.7) -> float:
    """
    Simple Temporal Coherence Index (TCI):
    1 - normalized volatility of the first difference (∆ series),
    smoothed by EMA for stability. Higher means smoother, more predictable.
    """
    diffs = np.diff(series, prepend=series[0])
    # EMA smoothing
    ema = 0.0
    for d in diffs:
        ema = alpha * d + (1 - alpha) * ema
    scale = np.mean(np.abs(diffs)) + 1e-6
    tci = 1.0 - min(abs(ema) / (scale + 1.0), 1.0)
    return float(np.clip(tci, 0.0, 1.0))


# ---------------------------
# Scenario generation
# ---------------------------

def make_scenario(hours: int = 24, seed: int = 42):
    """
    Toy microgrid:
    - Demand with diurnal structure + noise
    - Solar peaks mid-day, wind more even with gusts
    """
    rng = np.random.default_rng(seed)

    # Demand: base + diurnal + noise
    t = np.arange(hours)
    demand = 100 + 15*np.sin(2*np.pi*(t-6)/24) + rng.normal(0, 4, hours)

    # Solar: bell around midday
    solar = np.clip(60*np.exp(-0.5*((t-12)/4.5)**2) + rng.normal(0, 2, hours), 0, None)

    # Wind: moderate with random gusts
    wind = np.clip(35 + 5*np.sin(2*np.pi*(t)/8) + rng.normal(0, 6, hours), 0, None)

    return demand, solar, wind


# ---------------------------
# Baseline vs AEI orchestration
# ---------------------------

def baseline_controller(demand, solar, wind, storage_cap=20.0):
    """
    No forecasting, no coherence weighting: tries to absorb surplus or cover deficit
    within a bounded storage action. Residual absolute imbalance approximates 'waste'.
    """
    imbalance = solar + wind - demand
    # storage tries to buffer, but saturates
    storage_action = np.clip(imbalance, -storage_cap, storage_cap)
    residual = imbalance - storage_action  # what we couldn't handle
    waste = np.abs(residual).sum()
    kappa = kappa_coherence(residual)
    tci   = tci_temporal_coherence(residual)
    return residual, waste, kappa, tci


def aei_controller(demand, solar, wind, storage_cap=20.0, lead_weight=0.6, coherence_gain=0.7):
    """
    AEI with Veyn (time-symmetric peek) + coherence-weighted action.
    - Veyn produces a forward-aware demand forecast.
    - Coherence gain shrinks actions to favor smooth, stable flows (ethics + resilience).
    """
    demand_forecast = veyn_operator(demand, lead_weight=lead_weight)
    imbalance = (solar + wind) - demand_forecast

    # coherence-weighted action: avoid aggressive swings
    storage_action = np.clip(coherence_gain * imbalance, -storage_cap, storage_cap)
    residual = ((solar + wind) - demand) - storage_action  # true residual vs real demand
    waste = np.abs(residual).sum()
    kappa = kappa_coherence(residual)
    tci   = tci_temporal_coherence(residual)
    return residual, waste, kappa, tci


# ---------------------------
# Experiment runner
# ---------------------------

def run_experiment(hours=24, seed=42):
    demand, solar, wind = make_scenario(hours=hours, seed=seed)

    base_res, base_waste, base_k, base_tci = baseline_controller(demand, solar, wind)
    aei_res,  aei_waste,  aei_k,  aei_tci  = aei_controller(demand, solar, wind)

    savings_pct = (1.0 - aei_waste / (base_waste + 1e-9)) * 100.0

    report = {
        "hours": hours,
        "kappa_baseline": round(base_k, 3),
        "kappa_aei": round(aei_k, 3),
        "tci_baseline": round(base_tci, 3),
        "tci_aei": round(aei_tci, 3),
        "waste_baseline": round(float(base_waste), 2),
        "waste_aei": round(float(aei_waste), 2),
        "s
