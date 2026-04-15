# Redis Architecture Analysis — CSU33D06
## Reproducing the Analysis

This directory contains all scripts and data needed to reproduce the analysis
presented in `redis_architecture_report.pdf`.

### Requirements

```bash
pip install reportlab matplotlib pypdf --break-system-packages
```

Python 3.8+ is required. No external API keys or internet access needed —
all data is curated from published sources (see Section 8 of the report).

### Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| `01_loc_metrics.py`   | Lines of code, file counts, COCOMO estimate | `loc_results.json` |
| `02_complexity_metrics.py` | Cyclomatic complexity & Maintainability Index | `complexity_results.json` |
| `03_velocity_metrics.py` | Issue velocity, PR rates, contributor counts | `velocity_results.json` |
| `04_coupling_metrics.py` | Martin's instability metrics (A, I, D) | `coupling_results.json` |
| `05_generate_charts.py` | Generates all 4 figures (PNG) | `fig1_*.png` – `fig4_*.png` |
| `build_report.py` | Assembles the final 10-page PDF | `redis_architecture_report.pdf` |

### Run order

```bash
python3 01_loc_metrics.py
python3 02_complexity_metrics.py
python3 03_velocity_metrics.py
python3 04_coupling_metrics.py
python3 05_generate_charts.py   # must run before build_report.py
python3 build_report.py
```

Or run all at once:

```bash
for f in 01 02 03 04 05; do python3 ${f}_*.py; done
python3 build_report.py
```

### Data Sources

All metrics are derived from:
- **scc** output on redis/redis (March 2025 snapshot)
- **Percona Blog** community analysis (December 2025)
- **deepwiki.com/redis/redis** architecture documentation
- **pauladamsmith.com** Redis internals series
- **GitHub public API** snapshots of issue/PR data

Scripts include inline citations and can be extended to use a live
`git clone https://github.com/redis/redis` if desired.

### Optional: live analysis with scc

If you have `scc` installed and a local Redis clone:

```bash
scc /path/to/redis/src
```

The output can replace the `CURATED_DATA` dict in `01_loc_metrics.py`.
