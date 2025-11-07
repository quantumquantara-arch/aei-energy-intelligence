import numpy as np
import pandas as pd

class Veyn:
    """
    Temporal-coherence operator.
    - Exponential memory (gamma) smooths noise.
    - Simple continuity guard reduces shock from sudden jumps/gaps.
    - Keeps a small state so the next call starts where the last ended.
    """
    def __init__(self, gamma: float = 0.85, gap_penalty: float = 0.2):
        if not (0.0 < gamma < 1.0):
            raise ValueError("gamma must be in (0,1)")
        self.gamma = gamma
        self.gap_penalty = gap_penalty
        self.state: float | None = None

    def transform(self, series: pd.Series) -> pd.Series:
        s = series.astype(float).to_numpy()
        y = np.zeros_like(s, dtype=float)
        state = s[0] if self.state is None else self.state

        # exponential memory
        for i, v in enumerate(s):
            state = self.gamma * state + (1 - self.gamma) * v
            y[i] = state

        # continuity guard: dampen rare large steps
        if len(y) > 2:
            dy = np.abs(np.diff(y, prepend=y[0]))
            thresh = np.nanstd(y) * 3 + 1e-9
            mask = dy > thresh
            if mask.any():
                y[mask] = (1 - self.gap_penalty) * y[mask] + self.gap_penalty * s[mask]

        self.state = float(y[-1])
        return pd.Series(y, index=series.index, name="veyn")

def moving_average_forecast(series: pd.Series, horizon: int = 24, window: int = 6) -> pd.Series:
    """
    Very small baseline forecast for the demo.
    Takes the rolling mean as the level and projects it forward.
    """
    level = float(series.rolling(window, min_periods=1).mean().iloc[-1])
    return pd.Series([level] * horizon, name="forecast")
