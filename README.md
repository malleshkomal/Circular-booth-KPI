# Circular Booth KPI Demo

A small, self-contained example of **KPI-based circular product evaluation**: it links material, product, usage and end-of-life data to sustainability and circularity indicators, simulates reuse scenarios, and ranks design options with transparent, explainable logic.

It uses an exhibition booth as the example product.

> **Important:** This is an independent personal demo. It is **not** part of, affiliated with,  **All data in `data/` are illustrative placeholders**, not measured or database values. Do not cite the numbers. For real studies, replace them with ecoinvent / EPD / primary data.

## What it shows

| Toolkit idea (public description) | Where it appears here |
|---|---|
| KPI framework linking indicators with product, material and life-cycle data | `data/*.csv` joined in `model.py`; KPIs: GWP per use, cost per use, recycled content, EoL recovery rate, circularity index |
| Simulation of environmental and economic scenarios | `sweep_reuse_cycles()` (reuse cycles) and the EoL credit-method comparison |
| AI-supported decision logic | `decision.py`: weighted multi-criteria ranking and rule-based explanations. No LLM is used |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_demo.py      # prints ranking and recommendations, writes results/
pytest                  # 8 tests
```

## Example output (illustrative data)

| Option | Reuse cycles | GWP per use (kg CO₂e) | Cost per use (€) | Circularity index | Rank |
|---|---|---|---|---|---|
| reusable_recycled | 5 | 78 | 104 | 0.67 | 1 |
| reusable | 5 | 106 | 95 | 0.51 | 2 |
| linear | 1 | 857 | 451 | 0.05 | 3 |

![GWP breakdown](results/gwp_breakdown.png)
![Reuse sweep](results/reuse_sweep.png)

## How the model works

For each design option and component (mass *m*, recycled share *r*), with *n* = reuse cycles:

- Embodied GWP = m · [(1 − r) · EF_virgin + r · EF_recycled]
- Production per use = embodied / n; refurbishment per use = embodied · refurb_share · (n − 1) / n
- End of life per use = Σ m · (process EF − credit_share · avoided EF) / n
- Recycled content and recovery rate are mass-weighted
- Circularity index = (recycled content + recovery rate + (1 − 1/n)) / 3. This is a **simplified, equally weighted illustrative index. It is not the Ellen MacArthur Material Circularity Indicator**

**Ranking** is a weighted sum (default GWP 0.4, cost 0.3, circularity 0.3) of min-max normalised criteria. Weights are normalised, so only their ratios matter.

**Guardrail by design:** every number in an explanation comes from the deterministic model. If an LLM is added later, it may only phrase these results. It must not supply emission factors or other data.

## A methodological choice you should know about

Counting both a low-burden recycled input *and* a full recycling credit at end of life claims the same benefit twice (an early version of this demo produced negative GWP for a booth because of it). Two methods are therefore implemented:

- `net_scrap` (default): credit only for recovery **beyond** the recycled input share
- `cut_off`: no end-of-life credit

The ranking is the same under both, but the size of the benefit differs a lot (reusable booth: 106 vs 191 kg CO₂e per use). `run_demo.py` prints both. Results should always be reported with the method named.

## Limitations

- Illustrative data; no uncertainty analysis; GWP only (no other impact categories)
- No transport, use-phase energy, storage, or biogenic carbon; no price premium for recycled material
- The reuse sweep overrides reuse cycles for all options. "linear" at n > 1 is hypothetical and has no refurbishment
- Rule-based explanations, not a learned model

## Possible next steps

- Replace placeholders with Brightway/ecoinvent-based factors and run Monte Carlo uncertainty
- Add more impact categories and a relational schema (SQL) for product, material and end-of-life data
- Add a guarded LLM layer that explains results without being allowed to generate data
- Encode more R-strategies (repair, remanufacture) as separate end-of-life routes

## Project structure

```
data/        booth_bom.csv, materials.csv, eol_routes.csv, design_options.csv
src/boothkpi model.py (KPIs), decision.py (ranking, explanations), plots.py
tests/       pytest checks (including a guard against double counting)
results/     generated CSVs and charts
run_demo.py  entry point
```
