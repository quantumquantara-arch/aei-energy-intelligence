import pandas as pd
import pulp
from ..config import BatteryConfig

def battery_dispatch(
    load_kw: pd.Series,
    pv_kw: pd.Series,
    price: pd.Series,
    cfg: BatteryConfig = BatteryConfig(),
    dt_hours: float = 1.0,
) -> pd.DataFrame:
    """
    Minimize energy cost given load, PV generation and prices.
    Variables:
      ch_t  : charge power (kW)
      dis_t : discharge power (kW)
      soc_t : state of charge (kWh)

    Grid import (+) / export (-) each step:
      grid_t = load_t - pv_t + ch_t - dis_t

    SoC dynamics (η split between charge/discharge):
      soc_t = soc_{t-1} + (ηc*ch_t - dis_t/ηd) * dt

    Returns a DataFrame with charge/discharge/soc/grid profiles.
    """
    assert len(load_kw) == len(pv_kw) == len(price), "series must align"
    T = len(load_kw)

    prob = pulp.LpProblem("battery_dispatch", sense=pulp.LpMinimize)

    ch  = [pulp.LpVariable(f"ch_{t}",  lowBound=0, upBound=cfg.max_charge_kw)    for t in range(T)]
    dis = [pulp.LpVariable(f"dis_{t}", lowBound=0, upBound=cfg.max_discharge_kw) for t in range(T)]
    soc = [pulp.LpVariable(
            f"soc_{t}",
            lowBound=cfg.soc_min * cfg.capacity_kwh,
            upBound=cfg.soc_max * cfg.capacity_kwh
          ) for t in range(T)]

    # objective: minimize cost of grid energy
    grid = [load_kw.iloc[t] - pv_kw.iloc[t] + ch[t] - dis[t] for t in range(T)]
    prob += pulp.lpSum(price.iloc[t] * grid[t] * dt_hours for t in range(T))

    # SoC dynamics with split efficiencies
    eta_c = cfg.round_trip_eff ** 0.5
    eta_d = cfg.round_trip_eff ** 0.5
    for t in range(T):
        if t == 0:
            prob += soc[t] == (cfg.capacity_kwh * 0.50) + (eta_c * ch[t] - dis[t] / eta_d) * dt_hours
        else:
            prob += soc[t] == soc[t-1] + (eta_c * ch[t] - dis[t] / eta_d) * dt_hours

    # (Optional) prevent simultaneous full charge & discharge abuse by a simple cap
    for t in range(T):
        prob += ch[t] * dis[t] == 0  # MILP-free mutual exclusion (relaxed by solver tolerance)

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    dispatch = pd.DataFrame(
        {
            "charge_kw":     [v.value() for v in ch],
            "discharge_kw":  [v.value() for v in dis],
            "soc_kwh":       [v.value() for v in soc],
            "grid_kw":       [float(grid[t].value()) if hasattr(grid[t], "value") else float(grid[t])
                               for t in range(T)],
        },
        index=load_kw.index,
    )
    return dispatch
