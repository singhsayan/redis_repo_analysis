#!/usr/bin/env python3
"""
Script 5: Generate Analysis Charts for Redis Report
CSU33D06 - Redis Architecture Analysis
-------------------------------------------
Produces all charts referenced in the PDF report:
  fig1_loc_breakdown.png          — stacked bar: LOC by language
  fig2_cc_distribution.png        — bar: cyclomatic complexity buckets
  fig3_issue_velocity.png         — line: monthly issues over time
  fig4_instability_scatter.png    — scatter: A vs I (main sequence)

Usage:
    python3 05_generate_charts.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json, os

OUT_DIR = "."

COLORS = {
    "blue":   "#2563EB",
    "red":    "#DC2626",
    "green":  "#16A34A",
    "orange": "#EA580C",
    "purple": "#7C3AED",
    "grey":   "#6B7280",
    "light":  "#DBEAFE",
    "dark":   "#1E3A5F",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titlesize": 11,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.dpi": 150,
})

# ── Figure 1: LOC breakdown ──────────────────────────────────────────────────
def fig1_loc():
    langs   = ["C", "C Header", "TCL", "JSON", "Python", "Shell", "Other"]
    code    = [190252, 31881, 54962, 25388, 3610, 1044, 12000]
    comments= [45998, 11302, 4651, 0, 498, 343, 1800]
    blanks  = [31103, 5648, 7330, 4, 694, 239, 1200]

    x = np.arange(len(langs))
    w = 0.6

    fig, ax = plt.subplots(figsize=(8, 4))
    b1 = ax.bar(x, code,     w, label="Code",     color=COLORS["blue"])
    b2 = ax.bar(x, comments, w, bottom=code, label="Comments", color=COLORS["green"])
    b3 = ax.bar(x, blanks,   w,
                bottom=[c+m for c,m in zip(code, comments)],
                label="Blank", color=COLORS["grey"], alpha=0.5)

    ax.set_xticks(x); ax.set_xticklabels(langs, rotation=30, ha="right")
    ax.set_ylabel("Lines")
    ax.set_title("Redis Codebase: Lines by Language and Type")
    ax.legend(loc="upper right", fontsize=8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig1_loc_breakdown.png"))
    plt.close(fig)
    print("  Saved fig1_loc_breakdown.png")

# ── Figure 2: CC distribution ────────────────────────────────────────────────
def fig2_cc():
    categories = ["Low\n(CC 1-10)", "Medium\n(CC 11-20)",
                  "High\n(CC 21-50)", "Very High\n(CC > 50)"]
    counts = [8, 6, 7, 4]   # from script 2 results
    colors = [COLORS["green"], COLORS["blue"], COLORS["orange"], COLORS["red"]]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(categories, counts, color=colors, edgecolor="white", linewidth=1.5)
    for bar, n in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(n), ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_ylabel("Number of Functions Sampled")
    ax.set_title("Cyclomatic Complexity Distribution (n=25 sampled functions)")
    ax.set_ylim(0, max(counts) + 2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    threshold_note = "McCabe threshold\n(CC ≤ 10)"
    ax.axhline(y=0, color="black", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig2_cc_distribution.png"))
    plt.close(fig)
    print("  Saved fig2_cc_distribution.png")

# ── Figure 3: Issue velocity over time ──────────────────────────────────────
def fig3_velocity():
    MONTHLY_ISSUES = {
        "2022-01": 52, "2022-04": 61, "2022-07": 48, "2022-10": 66,
        "2023-01": 67, "2023-04": 69, "2023-07": 55, "2023-10": 76,
        "2024-01": 40, "2024-03": 29, "2024-06": 19, "2024-09": 17,
        "2024-12": 18, "2025-03": 27, "2025-06": 28, "2025-09": 35,
    }
    MONTHLY_PRS = {
        "2022-01": 38, "2022-04": 45, "2022-07": 36, "2022-10": 50,
        "2023-01": 49, "2023-04": 51, "2023-07": 41, "2023-10": 58,
        "2024-01": 30, "2024-03": 21, "2024-06": 12, "2024-09": 11,
        "2024-12": 12, "2025-03": 21, "2025-06": 25, "2025-09": 34,
    }

    labels = sorted(MONTHLY_ISSUES.keys())
    issues = [MONTHLY_ISSUES[l] for l in labels]
    prs    = [MONTHLY_PRS.get(l, 0) for l in labels]

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(x, issues, "o-", color=COLORS["blue"],   label="Issues opened", linewidth=2)
    ax.plot(x, prs,    "s--", color=COLORS["orange"], label="PRs merged",    linewidth=2)

    # Annotate key events
    # Find index of 2024-03
    idx_lc = labels.index("2024-03")
    idx_ar = labels.index("2025-06") if "2025-06" in labels else None
    idx_ai = labels.index("2024-12") if "2024-12" in labels else None

    ax.axvline(x=idx_lc, color=COLORS["red"], linestyle="--", alpha=0.7, linewidth=1.5)
    ax.text(idx_lc + 0.2, max(issues)*0.95, "Licence\nChange\nMar 2024",
            fontsize=7, color=COLORS["red"], va="top")

    if idx_ai:
        ax.axvline(x=idx_ai, color=COLORS["purple"], linestyle=":", alpha=0.7, linewidth=1.5)
        ax.text(idx_ai + 0.2, max(issues)*0.6, "antirez\nreturns\nDec 2024",
                fontsize=7, color=COLORS["purple"], va="top")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("Count")
    ax.set_title("Redis GitHub Activity: Issues Opened & PRs Merged (2022–2025)")
    ax.legend(loc="upper right", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig3_issue_velocity.png"))
    plt.close(fig)
    print("  Saved fig3_issue_velocity.png")

# ── Figure 4: Instability scatter (A vs I) ───────────────────────────────────
def fig4_instability():
    modules_data = [
        ("server.c",      0.05, 0.90),
        ("networking.c",  0.10, 0.69),
        ("ae.c",          0.60, 0.17),
        ("dict.c",        0.70, 0.07),
        ("sds.c",         0.75, 0.06),
        ("listpack.c",    0.65, 0.10),
        ("rdb.c",         0.15, 0.77),
        ("aof.c",         0.12, 0.79),
        ("cluster.c",     0.08, 0.88),
        ("replication.c", 0.10, 0.80),
        ("config.c",      0.15, 0.67),
        ("acl.c",         0.15, 0.55),
        ("scripting.c",   0.12, 0.80),
        ("bio.c",         0.50, 0.29),
        ("zmalloc.c",     0.80, 0.05),
        ("t_zset.c",      0.20, 0.75),
    ]

    names = [m[0] for m in modules_data]
    A     = [m[1] for m in modules_data]
    I     = [m[2] for m in modules_data]
    D     = [abs(a + i - 1) for a, i in zip(A, I)]

    fig, ax = plt.subplots(figsize=(7, 6))

    # Main sequence line
    ax.plot([0, 1], [1, 0], "k--", alpha=0.3, linewidth=1, label="Main sequence (A+I=1)")

    # Pain / useless zones
    ax.fill_between([0, 0.3], [0, 0], [0.3, 0], alpha=0.08, color="red",    label="Zone of Pain (D>0.3)")
    ax.fill_between([0.7, 1], [0.7, 1], [1, 1], alpha=0.08, color="orange", label="Zone of Uselessness")

    sc = ax.scatter(A, I, c=D, cmap="RdYlGn_r", s=80, vmin=0, vmax=0.5,
                    edgecolors="grey", linewidth=0.5, zorder=3)

    for name, a, i in zip(names, A, I):
        offset = (0.01, 0.01)
        if name in ("server.c", "cluster.c"):
            offset = (0.01, -0.04)
        ax.annotate(name, (a, i), xytext=(a+offset[0], i+offset[1]),
                    fontsize=7, alpha=0.85)

    cbar = plt.colorbar(sc, ax=ax, shrink=0.7)
    cbar.set_label("Distance D from main sequence", fontsize=8)

    ax.set_xlabel("Abstractness A")
    ax.set_ylabel("Instability I")
    ax.set_title("Redis Module Coupling: A vs I (Martin's Main Sequence)")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper right", fontsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig4_instability_scatter.png"))
    plt.close(fig)
    print("  Saved fig4_instability_scatter.png")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Generating charts...")
    fig1_loc()
    fig2_cc()
    fig3_velocity()
    fig4_instability()
    print("All charts generated.")
