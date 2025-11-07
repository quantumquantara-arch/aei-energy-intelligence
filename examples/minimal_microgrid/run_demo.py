import pandas as pd
from aei_core.orchestration.policy_engine import plan

def main():
    df = pd.read_csv("examples/minimal_microgrid/demo_data.csv")
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.set_index("ts")

    result = plan(
        load_kw=df["load_kw"],
        pv_kw=df["pv_kw"],
        price=df["price_usd_per_kwh"],
    )

    print("\n--- AEI Demo ---")
    print("kappa_mean:", round(result["kappa_mean"], 3))
    print("TCI:", round(result["tci"], 3))
    print("First 5 forecast pts:", [round(x,2) for x in result["forecast_kw"][:5]])
    print("First 5 SOC:", [round(x,2) for x in result["dispatch"]["soc_kwh"][:5]])
    print("----------------\n")

if __name__ == "__main__":
    main()
