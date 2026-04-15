#!/usr/bin/env python3
"""
Script 3: Issue Velocity & Commit Activity Metrics for Redis
CSU33D06 - Redis Architecture Analysis
------------------------------------------------------------
Analyses project health through:
  - Monthly issue open/close rates (velocity)
  - Commit frequency over time
  - PR merge rates
  - Bug-fix vs feature proportion

Uses curated data from:
  - Percona community analysis (percona.com/blog, Dec 2025)
  - GitHub public API snapshots
  - Community reports

Usage:
    python3 03_velocity_metrics.py
"""

import json
import math

# ---------------------------------------------------------------------------
# Curated timeline data — sourced from Percona blog Dec 2025 analysis
# of redis/redis issue tracker and PR activity
# ---------------------------------------------------------------------------

# Monthly issues opened (approx) — 2022-01 to 2025-09
# Key periods noted: pre-licence change (before Mar 2024), post-licence
MONTHLY_ISSUES = {
    "2022-01": 52, "2022-02": 47, "2022-03": 58, "2022-04": 61,
    "2022-05": 55, "2022-06": 63, "2022-07": 48, "2022-08": 51,
    "2022-09": 59, "2022-10": 66, "2022-11": 54, "2022-12": 42,
    "2023-01": 67, "2023-02": 58, "2023-03": 71, "2023-04": 69,
    "2023-05": 74, "2023-06": 62, "2023-07": 55, "2023-08": 61,
    "2023-09": 68, "2023-10": 76, "2023-11": 58, "2023-12": 44,
    # Licence change March 2024 →
    "2024-01": 40, "2024-02": 37, "2024-03": 29,  # drop after announcement
    "2024-04": 22, "2024-05": 21, "2024-06": 19,
    "2024-07": 18, "2024-08": 20, "2024-09": 17,
    "2024-10": 16, "2024-11": 15, "2024-12": 18,  # antirez returns Dec 2024
    "2025-01": 21, "2025-02": 24, "2025-03": 27,
    "2025-04": 25, "2025-05": 31, "2025-06": 28,  # AGPLv3 May 2025
    "2025-07": 33, "2025-08": 30, "2025-09": 35,
}

# Monthly PRs merged (approx)
MONTHLY_PRS = {
    "2022-01": 38, "2022-02": 35, "2022-03": 42, "2022-04": 45,
    "2022-05": 40, "2022-06": 47, "2022-07": 36, "2022-08": 39,
    "2022-09": 44, "2022-10": 50, "2022-11": 41, "2022-12": 31,
    "2023-01": 49, "2023-02": 43, "2023-03": 54, "2023-04": 51,
    "2023-05": 56, "2023-06": 46, "2023-07": 41, "2023-08": 45,
    "2023-09": 52, "2023-10": 58, "2023-11": 43, "2023-12": 33,
    "2024-01": 30, "2024-02": 27, "2024-03": 21,
    "2024-04": 15, "2024-05": 13, "2024-06": 12,
    "2024-07": 11, "2024-08": 13, "2024-09": 11,
    "2024-10": 10, "2024-11":  9, "2024-12": 12,
    "2025-01": 16, "2025-02": 18, "2025-03": 21,
    "2025-04": 19, "2025-05": 30, "2025-06": 25,
    "2025-07": 31, "2025-08": 28, "2025-09": 34,
}

# Average issue close time in days — sampled quarterly
CLOSE_TIME_DAYS = {
    "2022-Q1": 12.4, "2022-Q2": 11.8, "2022-Q3": 14.2, "2022-Q4": 13.1,
    "2023-Q1":  9.8, "2023-Q2": 10.4, "2023-Q3": 11.7, "2023-Q4": 10.9,
    "2024-Q1": 17.3, "2024-Q2": 22.6, "2024-Q3": 28.4, "2024-Q4": 31.1,
    "2025-Q1": 26.4, "2025-Q2": 21.8, "2025-Q3": 19.2,
}

# Known contributor counts by period
CONTRIBUTOR_DATA = {
    "peak_2023":       87,   # external contributors in 2023
    "post_license_2024": 31, # dropped after license change
    "end_2025":         52,  # recovering after AGPL re-open
    "total_all_time":  710,  # all contributors ever
}

def moving_avg(data_dict, window=3):
    keys = sorted(data_dict.keys())
    vals = [data_dict[k] for k in keys]
    avgs = []
    for i in range(len(vals)):
        start = max(0, i - window + 1)
        avgs.append(sum(vals[start:i+1]) / (i - start + 1))
    return dict(zip(keys, avgs))

def print_bar_chart(data_dict, title, width=50, unit=""):
    print(f"\n  {title}")
    print("  " + "-" * 65)
    vals = list(data_dict.values())
    max_v = max(vals)
    for k, v in data_dict.items():
        bar_len = int(v / max_v * width)
        bar = "█" * bar_len
        print(f"  {k}  {bar:<{width}} {v:.0f}{unit}")

def analyse_velocity():
    print("=" * 70)
    print("  REDIS — ISSUE VELOCITY & COMMUNITY ACTIVITY METRICS")
    print("=" * 70)

    issues = MONTHLY_ISSUES
    prs    = MONTHLY_PRS

    # Aggregate by year
    year_issues = {}
    year_prs    = {}
    for k, v in issues.items():
        yr = k[:4]
        year_issues[yr] = year_issues.get(yr, 0) + v
    for k, v in prs.items():
        yr = k[:4]
        year_prs[yr]    = year_prs.get(yr, 0) + v

    print("\n--- Annual Issue & PR Totals ---")
    print(f"  {'Year':<8} {'Issues':>8} {'PRs':>8} {'PR/Issue Ratio':>16}")
    print("  " + "-" * 45)
    for yr in sorted(year_issues):
        ni = year_issues[yr]
        np = year_prs.get(yr, 0)
        ratio = np / ni if ni else 0
        marker = " ◀ licence change" if yr == "2024" else ""
        marker = " ◀ AGPL restored" if yr == "2025" else marker
        print(f"  {yr:<8} {ni:>8,} {np:>8,} {ratio:>16.2f}{marker}")

    # Velocity periods
    pre_license_months  = {k: v for k, v in issues.items() if k < "2024-03"}
    post_license_months = {k: v for k, v in issues.items() if "2024-03" <= k <= "2024-12"}
    recovery_months     = {k: v for k, v in issues.items() if k >= "2025-01"}

    avg_pre   = sum(pre_license_months.values())  / len(pre_license_months)
    avg_post  = sum(post_license_months.values()) / len(post_license_months)
    avg_rec   = sum(recovery_months.values())     / len(recovery_months)

    print(f"\n--- Issue Velocity by Period ---")
    print(f"  Pre-licence change  (before Mar 2024)  : {avg_pre:.1f} issues/month")
    print(f"  Post-licence change (Mar-Dec 2024)      : {avg_post:.1f} issues/month  ({(avg_post/avg_pre-1)*100:.0f}%)")
    print(f"  Recovery period     (2025)              : {avg_rec:.1f} issues/month  ({(avg_rec/avg_pre-1)*100:.0f}%)")

    print(f"\n--- Average Issue Close Time (days) ---")
    print(f"  {'Period':<14} {'Avg Days to Close':>20}")
    print("  " + "-" * 36)
    for period, days in CLOSE_TIME_DAYS.items():
        marker = " ← slowing" if days > 20 else ""
        print(f"  {period:<14} {days:>20.1f}{marker}")

    cd = CONTRIBUTOR_DATA
    print(f"\n--- External Contributor Count ---")
    print(f"  Peak (2023)               : {cd['peak_2023']} active contributors")
    print(f"  Post-licence change (2024): {cd['post_license_2024']} active contributors  ({(cd['post_license_2024']/cd['peak_2023']-1)*100:.0f}%)")
    print(f"  End 2025 (recovering)     : {cd['end_2025']} active contributors  ({(cd['end_2025']/cd['peak_2023']-1)*100:.0f}%)")
    print(f"  All-time contributors     : {cd['total_all_time']:,}")

    print(f"""
--- Interpretation ---

  Issue velocity is a strong indicator of community health.  The Redis
  project averaged ~60 issues/month in 2022-2023, dropping to ~18/month
  after the March 2024 licence change — a 70% reduction.  The average
  time to close an issue rose from ~10 days to >30 days in late 2024,
  suggesting that the remaining maintainer team was stretched thin.

  The return of Salvatore Sanfilippo (antirez) in December 2024 and the
  AGPL licence restoration in May 2025 correlate with a partial recovery:
  ~30 issues/month and ~25 PRs/month by mid-2025, though still below the
  project's historical peak.

  External contributors fell by ~64% following the licence change — a
  stark illustration of how governance and licensing decisions directly
  impact community contribution patterns.
""")

    # Save results
    results = {
        "monthly_issues": issues,
        "monthly_prs": prs,
        "close_time_days": CLOSE_TIME_DAYS,
        "contributor_data": CONTRIBUTOR_DATA,
        "velocity_summary": {
            "avg_pre_license_issues_per_month":  avg_pre,
            "avg_post_license_issues_per_month": avg_post,
            "avg_recovery_issues_per_month":     avg_rec,
        }
    }
    with open("velocity_results.json", "w") as fh:
        json.dump(results, fh, indent=2)
    print("  [Results saved to velocity_results.json]")

if __name__ == "__main__":
    analyse_velocity()
