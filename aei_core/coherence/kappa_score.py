import pandas as pd

def kappa(row: pd.Series) -> float:
    """
    Computes a κ-score (0–1) based on:
      - carbon intensity (lower = better)
      - locality distance (closer = better)
      - social responsibility weight
    """
    ci = float(row.get("carbon_intensity_g_per_kwh", 400))
    locality = float(row.get("locality_km", 500))
    social = float(row.get("social_weight", 0.5))

    ci_score = max(0.0, min(1.0, 1 - ci / 600))        # 0 at 600 g/kWh, 1 near 0
    loc_score = max(0.0, min(1.0, 1 - locality / 500)) # 0 at 500 km, 1 local
    k = 0.5 * ci_score + 0.3 * loc_score + 0.2 * social
    return float(k)
