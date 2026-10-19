"""Run the demo: KPIs, reuse-cycle sweep, ranking, explanations, charts."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from boothkpi import evaluate_all, explain, load_inputs, rank_options, sweep_reuse_cycles
from boothkpi.plots import plot_gwp_breakdown, plot_reuse_sweep

RESULTS = ROOT / "results"


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    inputs = load_inputs()

    kpis = evaluate_all(inputs)
    ranking = rank_options(kpis)
    sweep = sweep_reuse_cycles(inputs)

    kpis.to_csv(RESULTS / "kpis.csv", index=False)
    ranking.to_csv(RESULTS / "ranking.csv", index=False)
    sweep.to_csv(RESULTS / "reuse_sweep.csv", index=False)
    plot_gwp_breakdown(kpis, RESULTS / "gwp_breakdown.png")
    plot_reuse_sweep(sweep, RESULTS / "reuse_sweep.png")

    pd.set_option("display.width", 140, "display.float_format", "{:.2f}".format)
    cols = ["option_id", "reuse_cycles", "gwp_per_use", "cost_per_use",
            "recycled_content", "recovery_rate", "circularity_index", "score", "rank"]
    print("\nRanking (illustrative data):\n")
    print(ranking[cols].to_string(index=False))
    print("\nRule-based recommendations:")
    for _, row in ranking.iterrows():
        print(f"\n[{row['option_id']}]")
        for note in explain(row):
            print(f"  - {note}")
    # Methodological sensitivity: how does the EoL credit choice change the picture?
    net = evaluate_all(inputs, credit_method="net_scrap").set_index("option_id")["gwp_per_use"]
    cut = evaluate_all(inputs, credit_method="cut_off").set_index("option_id")["gwp_per_use"]
    method_check = pd.DataFrame({"net_scrap": net, "cut_off": cut})
    method_check.to_csv(RESULTS / "credit_method_sensitivity.csv")
    print("\nGWP per use (kg CO2e) under two EoL credit methods:\n")
    print(method_check.to_string())

    print(f"\nResults written to {RESULTS}")


if __name__ == "__main__":
    main()
