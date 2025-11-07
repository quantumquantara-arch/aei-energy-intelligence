import pandas as pd
from ..forecasting.veyn_operator import Veyn, moving_average_forecast
from ..optimization.battery_dispatch_lp import battery_dispatch
from ..coherence.kappa_score import kappa
from ..coherence.temporal_coherence import temporal_coherence_index

def plan(load_kw: pd.Series, pv_kw: pd.Series, price: pd.Series) -> dict:
    """
    End-to-end planning:
      1) Smooth load with Veyn temporal operator
      2) Produce a simple baseline forecast
      3) Optimise battery dispatch (LP)
      4) Compute κ and TCI for the interval
    Returns a JSON-friendly dict.
    """
    # 1) temporal smoothing (Veyn)
    veyn = Veyn(gamma=0.85)
    smooth_load = veyn.transform(load_kw)

    # 2) baseline forecast (same length as inputs for demo)
    fc = moving_average_forecast(smooth_load, horizon=len(smooth_load))
    fc.index = load_kw.index  # align for convenience

    # 3) optimisation
    dispatch = battery_dispatch(load_kw=smooth_load, pv_kw=pv_kw, price=price)

    # 4) coherence metrics (toy inputs for now)
    df = pd.DataFrame({
        "carbon_intensity_g_per_kwh": (40 + 100*(1 - (pv_kw/(pv_kw.max()+1e-9)))).fillna(120),
        "locality_km": 5,
        "social_weight": 0.7
    }, index=load_kw.index)
    k_series = df.apply(kappa, axis=1)
    tci = temporal_coherence_index(k_series, window=min(24, len(k_series)))

    return {
        "forecast_kw": [float(x) for x in fc.values],
        "dispatch": dispatch.to_dict(orient="list"),
        "kappa_mean": float(k_series.mean()),
        "tci": float(tci),
    }
