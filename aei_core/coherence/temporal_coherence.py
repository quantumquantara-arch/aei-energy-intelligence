import numpy as np
import pandas as pd

def temporal_coherence_index(kappa_series: pd.Series, window: int = 24) -> float:
    """
    Temporal Coherence Index (TCI)

    Intuition:
      - Reward consistently high κ over time.
      - Penalize volatility (spiky / greenwashing behavior).

    Formula (bounded 0..1):
      TCI_t = mean(κ) * (1 - normalized_variance)
      where normalized_variance = var(κ) / var_max for a [0,1] signal (=0.25)

    Args:
      kappa_series: pd.Series of κ in [0,1] over time (one value per interval).
      window: rolling window length (e.g., 24 for hourly → 1 day).

    Returns:
      float TCI in [0,1] computed at the end of the series.
    """
    if kappa_series is None or len(kappa_series) == 0:
        return 0.0

    k = kappa_series.clip(0, 1).astype(float)
    # rolling mean and variance (population variance)
    mu = k.rolling(window, min_periods=1).mean()
    var = k.rolling(window, min_periods=1).var(ddof=0).fillna(0.0)

    # maximum variance for a bounded [0,1] process is 0.25
    norm_var = (var / 0.25).clip(0, 1)

    tci_series = mu * (1.0 - norm_var)
    return float(tci_series.iloc[-1])

def temporal_band(series: pd.Series, window: int = 24, z: float = 2.0) -> pd.DataFrame:
    """
    Helper: returns a smooth band (mean ± z*std) to visualize temporal stability.
    """
    s = series.astype(float)
    m = s.rolling(window, min_periods=1).mean()
    sd = s.rolling(window, min_periods=1).std(ddof=0).fillna(0.0)
    return pd.DataFrame({"mean": m, "low": m - z*sd, "high": m + z*sd})
