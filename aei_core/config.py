from dataclasses import dataclass

@dataclass
class BatteryConfig:
    capacity_kwh: float = 20.0
    max_charge_kw: float = 5.0
    max_discharge_kw: float = 5.0
    round_trip_eff: float = 0.9
    soc_min: float = 0.1
    soc_max: float = 0.9
