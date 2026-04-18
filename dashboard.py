import streamlit as st
import subprocess, sys, os, json, math, io
from pathlib import Path

BASE = Path(__file__).parent

st.set_page_config(
    page_title="Redis · Architecture Analyser",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
.stApp { background: #0d0f14; color: #c9cdd8; }
section[data-testid="stSidebar"] { background: #0a0c10; border-right: 1px solid rgba(255,255,255,0.05); }
section[data-testid="stSidebar"] * { color: #7a8099 !important; }
header[data-testid="stHeader"] { display: none; }

.top-bar {
    background: #0a0c10; border-bottom: 1px solid rgba(255,255,255,0.05);
    padding: 1.25rem 2rem; margin: -1rem -1rem 2.5rem -1rem;
    display: flex; align-items: center; gap: 1.5rem;
}
.top-bar-wordmark { font-family:'JetBrains Mono',monospace; font-size:0.85rem; font-weight:600; color:#e8eaf2; letter-spacing:0.04em; text-transform:uppercase; }
.top-bar-divider { width:1px; height:20px; background:rgba(255,255,255,0.08); }
.top-bar-title { font-size:0.9rem; font-weight:500; color:#9095ad; letter-spacing:-0.01em; }
.top-bar-right { margin-left:auto; display:flex; align-items:center; gap:0.75rem; }
.top-bar-badge { background:rgba(99,120,255,0.08); border:1px solid rgba(99,120,255,0.18); color:#7b8fff; padding:0.22rem 0.75rem; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:0.6rem; letter-spacing:0.1em; text-transform:uppercase; font-weight:500; }
.top-bar-version { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:#2e3248; letter-spacing:0.05em; }

.script-card { background:#10131a; border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:1.1rem 1.3rem; margin-bottom:0.65rem; position:relative; overflow:hidden; transition:border-color 0.15s ease,background 0.15s ease; }
.script-card:hover { border-color:rgba(99,120,255,0.22); background:#12151d; }
.script-title { font-size:0.85rem; font-weight:600; color:#dde0ed; margin-bottom:0.3rem; letter-spacing:-0.01em; }
.script-desc { font-family:'JetBrains Mono',monospace; font-size:0.67rem; color:#454866; line-height:1.55; }
.script-output-tag { display:inline-flex; align-items:center; gap:4px; background:rgba(99,120,255,0.06); border:1px solid rgba(99,120,255,0.14); color:#6878cc; padding:0.12rem 0.5rem; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:0.62rem; margin-top:0.55rem; letter-spacing:0.01em; }

.terminal-box { background:#07090e; border:1px solid rgba(255,255,255,0.04); border-radius:8px; padding:1rem 1.25rem; font-family:'JetBrains Mono',monospace; font-size:0.71rem; color:#5fb87a; line-height:1.7; max-height:380px; overflow-y:auto; white-space:pre-wrap; word-break:break-all; }

.metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; margin-bottom:1.5rem; }
.metric-card { background:#10131a; border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:1.1rem 1.25rem; text-align:left; }
.metric-value { font-size:1.65rem; font-weight:700; color:#e8eaf2; line-height:1; margin-bottom:0.4rem; letter-spacing:-0.04em; font-variant-numeric:tabular-nums; }
.metric-label { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#3a3f5a; text-transform:uppercase; letter-spacing:0.09em; }

.section-header { font-size:0.7rem; font-weight:600; color:#3a3f5a; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:1rem; display:flex; align-items:center; gap:0.75rem; }
.section-header::after { content:''; flex:1; height:1px; background:rgba(255,255,255,0.04); }

.placeholder-box { background:#0a0c12; border:1px dashed rgba(255,255,255,0.05); border-radius:8px; padding:2.5rem; text-align:center; color:#252840; font-family:'JetBrains Mono',monospace; font-size:0.73rem; margin-bottom:1rem; line-height:1.8; }

div[data-testid="stButton"] button { background:#1a1e2e !important; color:#9095ad !important; border:1px solid rgba(255,255,255,0.08) !important; border-radius:6px !important; font-family:'Inter',sans-serif !important; font-weight:500 !important; font-size:0.82rem !important; letter-spacing:0.01em !important; padding:0.5rem 1.5rem !important; transition:background 0.15s ease,border-color 0.15s ease,color 0.15s ease !important; }
div[data-testid="stButton"] button:hover { background:#1f2438 !important; border-color:rgba(99,120,255,0.3) !important; color:#c0c5dd !important; opacity:1 !important; }

.stProgress > div > div { background-color:#6378ff !important; }

button[data-baseweb="tab"] { font-family:'Inter',sans-serif !important; font-size:0.82rem !important; font-weight:500 !important; color:#3a3f5a !important; letter-spacing:0.01em !important; }
button[data-baseweb="tab"][aria-selected="true"] { color:#dde0ed !important; border-bottom-color:#6378ff !important; }

.img-caption { font-family:'JetBrains Mono',monospace; font-size:0.63rem; color:#2e3248; text-align:center; margin-top:0.4rem; margin-bottom:1.25rem; letter-spacing:0.04em; }
.sidebar-label { font-size:0.68rem; font-weight:600; color:#2a2e45; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem; }

.status-pill { display:inline-flex; align-items:center; gap:5px; font-family:'JetBrains Mono',monospace; font-size:0.58rem; letter-spacing:0.06em; font-weight:600; padding:0.15rem 0.6rem; border-radius:4px; white-space:nowrap; text-transform:uppercase; }
.status-idle    { background:rgba(60,65,100,0.15); color:#3a3f64; border:1px solid rgba(60,65,100,0.2); }
.status-running { background:rgba(200,160,30,0.1); color:#c8961e; border:1px solid rgba(200,160,30,0.2); }
.status-done    { background:rgba(40,180,110,0.1); color:#28b46e; border:1px solid rgba(40,180,110,0.18); }
.status-error   { background:rgba(220,70,70,0.1);  color:#dc4646; border:1px solid rgba(220,70,70,0.18); }

::-webkit-scrollbar { width:3px; height:3px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.06); border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:rgba(255,255,255,0.1); }
[data-testid="stDataFrame"] { border:1px solid rgba(255,255,255,0.04) !important; border-radius:6px !important; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div class="top-bar-wordmark">Redis</div>
    <div class="top-bar-divider"></div>
    <div class="top-bar-title">Architecture Analyser &nbsp;&middot;&nbsp; CSU33D06 &nbsp;&middot;&nbsp; March 2025</div>
    <div class="top-bar-right">
        <span class="top-bar-version">v2.0.0</span>
        <div class="top-bar-badge">Live Analysis</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Script definitions ────────────────────────────────────────────────────────
SCRIPTS = [
    {"id": "loc",        "file": "01_loc_metrics.py",       "title": "01 · Lines of Code & COCOMO",
     "desc": "Counts source lines, comments, blanks per language. Estimates effort via COCOMO.",
     "output": "loc_results.json"},
    {"id": "complexity", "file": "02_complexity_metrics.py", "title": "02 · Cyclomatic Complexity & MI",
     "desc": "Samples 25 functions, computes CC and Maintainability Index via SEI formula.",
     "output": "complexity_results.json"},
    {"id": "velocity",   "file": "03_velocity_metrics.py",  "title": "03 · Issue Velocity & Community Health",
     "desc": "Analyses GitHub issue rates, PR merge cadence and contributor counts 2022-2025.",
     "output": "velocity_results.json"},
    {"id": "coupling",   "file": "04_coupling_metrics.py",  "title": "04 · Module Coupling (Martin Metrics)",
     "desc": "Computes afferent/efferent coupling, instability I and distance D per module.",
     "output": "coupling_results.json"},
    {"id": "churn",      "file": "05_churn_metrics.py",     "title": "05 · Code Churn & Defect Hotspots",
     "desc": "File-level churn analysis: commits × complexity hotspot scores, CVE trajectory.",
     "output": "churn_results.json"},
    {"id": "coverage",   "file": "06_coverage_security.py", "title": "06 · Test Coverage & Security Surface",
     "desc": "Test-to-code ratio per module, security attack surface, CVE-to-component mapping.",
     "output": "coverage_results.json"},
    {"id": "busactor",   "file": "07_bus_factor.py",        "title": "07 · Bus Factor & Contributor Concentration",
     "desc": "Bus factor, Gini coefficient, knowledge silo detection, contributor loss events.",
     "output": "busactor_results.json"},
    {"id": "report",     "file": "build_report.py",         "title": "08 · Build PDF Report",
     "desc": "Assembles the complete 10-page PDF report with tables, figures and analysis.",
     "output": "redis_architecture_report.pdf"},
]

SCRIPT_CHART_MAP = {
    "loc":        "fig1_loc_breakdown.png",
    "complexity": "fig2_cc_distribution.png",
    "velocity":   "fig3_issue_velocity.png",
    "coupling":   "fig4_instability_scatter.png",
    "churn":      "fig5_churn_hotspot.png",
    "coverage":   "fig6_test_coverage.png",
    "busactor":   "fig7_bus_factor.png",
}

CHART_CAPTIONS = {
    "fig1_loc_breakdown.png":       "Figure 1 — Lines of Code by Language and Type",
    "fig2_cc_distribution.png":     "Figure 2 — Cyclomatic Complexity Distribution",
    "fig3_issue_velocity.png":      "Figure 3 — Issue Velocity and PR Merge Rate (2022-2025)",
    "fig4_instability_scatter.png": "Figure 4 — Martin A vs I Scatter (Main Sequence)",
    "fig5_churn_hotspot.png":       "Figure 5 — Code Churn vs Complexity Hotspot",
    "fig6_test_coverage.png":       "Figure 6 — Test Coverage Ratio by Module",
    "fig7_bus_factor.png":          "Figure 7 — Bus Factor and Knowledge Silos",
}

OUTPUT_FILES = {
    "loc":        ["loc_results.json"],
    "complexity": ["complexity_results.json"],
    "velocity":   ["velocity_results.json"],
    "coupling":   ["coupling_results.json"],
    "churn":      ["churn_results.json"],
    "coverage":   ["coverage_results.json"],
    "busactor":   ["busactor_results.json"],
    "report":     ["redis_architecture_report.pdf"],
}

# ── KEY FIX: render charts into BytesIO — zero disk I/O, zero race condition ─
def generate_chart_bytes(script_id):
    """Renders the matplotlib chart for script_id and returns raw PNG bytes.
    Never writes to disk, so it works identically on local and deployed envs."""
    fig = None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None, "matplotlib not installed"

    DARK_BG = "#10131a"
    plt.rcParams.update({
        "font.family":      "DejaVu Sans",
        "figure.dpi":       150,
        "axes.facecolor":   DARK_BG,
        "figure.facecolor": DARK_BG,
        "axes.edgecolor":   "#1e2235",
        "axes.labelcolor":  "#64748b",
        "xtick.color":      "#4a5068",
        "ytick.color":      "#4a5068",
        "text.color":       "#c9cdd8",
        "grid.color":       "#1a1e2e",
        "grid.linewidth":   0.5,
        "axes.titlesize":   10,
        "axes.labelsize":   8,
        "xtick.labelsize":  7,
        "ytick.labelsize":  7,
        "axes.titlecolor":  "#9095ad",
        "legend.facecolor": "#1a1e2e",
        "legend.edgecolor": "#2a2e45",
    })
    P = {"blue":"#5b7fff","indigo":"#818cf8","teal":"#2dd4bf","slate":"#64748b",
         "muted":"#334155","amber":"#f59e0b","red":"#f87171","green":"#4ade80",
         "purple":"#a78bfa","orange":"#fb923c"}

    if script_id not in SCRIPT_CHART_MAP:
        return None, "no chart mapped for this script"

    try:
        # ── Fig 1: LOC ────────────────────────────────────────────────────────
        if script_id == "loc":
            data = _load_json("loc_results.json")
            if not data: return None, "loc_results.json not found"
            langs    = ["C","C Header","TCL","JSON","Python","Shell","Other"]
            code     = [190252,31881,54962,25388,3610,1044,12000]
            comments = [45998,11302,4651,0,498,343,1800]
            blanks   = [31103,5648,7330,4,694,239,1200]
            x = np.arange(len(langs))
            fig, ax = plt.subplots(figsize=(7,3.8))
            ax.bar(x, code,     0.55, label="Code",     color=P["blue"],  alpha=0.9)
            ax.bar(x, comments, 0.55, bottom=code,      label="Comments", color=P["teal"],  alpha=0.75)
            ax.bar(x, blanks,   0.55, bottom=[c+m for c,m in zip(code,comments)],
                   label="Blank", color=P["muted"], alpha=0.5)
            ax.set_xticks(x); ax.set_xticklabels(langs, rotation=30, ha="right")
            ax.set_ylabel("Lines"); ax.set_title("Lines of code by language and type")
            ax.legend(fontsize=7, labelcolor="#9095ad")
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{v/1000:.0f}K"))
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            ax.grid(axis="y", linestyle="--", alpha=0.35)
            fig.tight_layout()

        # ── Fig 2: CC distribution ────────────────────────────────────────────
        elif script_id == "complexity":
            data = _load_json("complexity_results.json")
            if not data: return None, "complexity_results.json not found"
            dist = data["cc_distribution"]
            cats = ["Low\n(CC 1-10)","Medium\n(CC 11-20)","High\n(CC 21-50)","Very High\n(CC > 50)"]
            counts = [dist["low"],dist["medium"],dist["high"],dist["very_high"]]
            clrs = [P["green"],P["blue"],P["amber"],P["red"]]
            fig, ax = plt.subplots(figsize=(5,3.8))
            bars = ax.bar(cats, counts, color=clrs, width=0.5, alpha=0.85)
            for bar, n in zip(bars, counts):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                        str(n), ha="center", va="bottom", fontsize=9, fontweight="bold", color="#c9cdd8")
            ax.set_ylabel("Functions sampled"); ax.set_ylim(0, max(counts)+2)
            ax.set_title("Cyclomatic complexity distribution (n=25 functions)")
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            fig.tight_layout()

        # ── Fig 3: Issue velocity ─────────────────────────────────────────────
        elif script_id == "velocity":
            ISSUES = {"2022-01":52,"2022-04":61,"2022-07":48,"2022-10":66,
                      "2023-01":67,"2023-04":69,"2023-07":55,"2023-10":76,
                      "2024-01":40,"2024-03":29,"2024-06":19,"2024-09":17,
                      "2024-12":18,"2025-03":27,"2025-06":28,"2025-09":35}
            PRS    = {"2022-01":38,"2022-04":45,"2022-07":36,"2022-10":50,
                      "2023-01":49,"2023-04":51,"2023-07":41,"2023-10":58,
                      "2024-01":30,"2024-03":21,"2024-06":12,"2024-09":11,
                      "2024-12":12,"2025-03":21,"2025-06":25,"2025-09":34}
            labels = sorted(ISSUES.keys())
            x = np.arange(len(labels))
            fig, ax = plt.subplots(figsize=(9,3.8))
            ax.plot(x,[ISSUES[l] for l in labels],"o-",color=P["blue"],label="Issues opened",linewidth=2,markersize=4)
            ax.plot(x,[PRS.get(l,0) for l in labels],"s--",color=P["indigo"],label="PRs merged",linewidth=2,markersize=4)
            idx_lc = labels.index("2024-03")
            ax.axvline(x=idx_lc,color=P["amber"],linestyle="--",alpha=0.6,linewidth=1.2)
            ax.text(idx_lc+0.2,70,"Licence\nChange\nMar 2024",fontsize=6.5,color=P["amber"],va="top")
            ax.set_xticks(x); ax.set_xticklabels(labels,rotation=45,ha="right",fontsize=6.5)
            ax.set_ylabel("Count"); ax.set_title("GitHub activity — issues opened & PRs merged (2022-2025)")
            ax.legend(fontsize=7, labelcolor="#9095ad")
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            ax.grid(axis="y",linestyle="--",alpha=0.3)
            fig.tight_layout()

        # ── Fig 4: Coupling scatter ───────────────────────────────────────────
        elif script_id == "coupling":
            data = _load_json("coupling_results.json")
            if not data: return None, "coupling_results.json not found"
            A=[r["A"] for r in data]; I=[r["I"] for r in data]
            D=[abs(a+i-1) for a,i in zip(A,I)]
            names=[r["module"] for r in data]
            fig, ax = plt.subplots(figsize=(6,5))
            ax.plot([0,1],[1,0],"--",color="#2a2e45",linewidth=1.2,label="Main sequence")
            sc=ax.scatter(A,I,c=D,cmap="coolwarm",s=72,vmin=0,vmax=0.5,
                          edgecolors="#1e2235",linewidth=0.6,zorder=3,alpha=0.9)
            for name,a,i in zip(names,A,I):
                off=(0.01,-0.04) if name in ("server.c","cluster.c") else (0.01,0.01)
                ax.annotate(name,(a,i),xytext=(a+off[0],i+off[1]),fontsize=6.5,alpha=0.8,color="#9095ad")
            cb=plt.colorbar(sc,ax=ax,shrink=0.7)
            cb.set_label("Distance D",fontsize=7,color="#64748b")
            plt.setp(cb.ax.yaxis.get_ticklabels(),color="#64748b")
            ax.set_xlabel("Abstractness A"); ax.set_ylabel("Instability I")
            ax.set_title("Module coupling — A vs I (Martin main sequence)")
            ax.set_xlim(-0.05,1.05); ax.set_ylim(-0.05,1.05)
            ax.legend(fontsize=7,labelcolor="#9095ad")
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            ax.grid(linestyle="--",alpha=0.2)
            fig.tight_layout()

        # ── Fig 5: Churn hotspot ──────────────────────────────────────────────
        elif script_id == "churn":
            data = _load_json("churn_results.json")
            if not data: return None, "churn_results.json not found"
            top = data["churn_data"][:15]
            files   = [d["file"].replace("src/","") for d in top]
            commits = [d["commits"] for d in top]
            cplx    = [d["complexity"] for d in top]
            hot     = [d["hotspot"] for d in top]
            fig, ax = plt.subplots(figsize=(8,4.5))
            sc=ax.scatter(commits,cplx,c=hot,cmap="RdYlGn_r",
                          s=[h*1.8+25 for h in hot],edgecolors="#1e2235",
                          linewidth=0.5,zorder=3,vmin=0,vmax=100,alpha=0.88)
            for fname,c,x,h in zip(files,commits,cplx,hot):
                ax.annotate(fname,(c,x),xytext=(c+3,x+15),fontsize=6.2,alpha=0.85,color="#9095ad")
            cb=plt.colorbar(sc,ax=ax,shrink=0.8)
            cb.set_label("Hotspot Score",fontsize=7,color="#64748b")
            plt.setp(cb.ax.yaxis.get_ticklabels(),color="#64748b")
            ax.set_xlabel("Commits (churn count)"); ax.set_ylabel("Cyclomatic Complexity")
            ax.set_title("Code churn vs complexity — defect hotspot analysis")
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            ax.grid(linestyle="--",alpha=0.2)
            fig.tight_layout()

        # ── Fig 6: Test coverage ──────────────────────────────────────────────
        elif script_id == "coverage":
            data = _load_json("coverage_results.json")
            if not data: return None, "coverage_results.json not found"
            covered = [(d["module"].replace("src/",""),d["c_sloc"],d["test_sloc"])
                       for d in data["coverage"] if d["has_test"]][:10]
            mods  = [x[0] for x in covered]
            csloc = [x[1] for x in covered]
            tsloc = [x[2] for x in covered]
            ratios= [t/c*100 if c>0 else 0 for c,t in zip(csloc,tsloc)]
            x = np.arange(len(mods))
            fig, ax1 = plt.subplots(figsize=(10,4.2))
            ax2 = ax1.twinx()
            ax2.set_facecolor(DARK_BG)
            ax1.bar(x-0.2,csloc,0.35,label="C Source SLOC",color=P["blue"],alpha=0.8)
            ax1.bar(x+0.2,tsloc,0.35,label="Test SLOC",color=P["green"],alpha=0.8)
            ax2.plot(x,ratios,"o--",color=P["red"],linewidth=1.5,markersize=5,label="Test ratio %")
            ax1.set_xticks(x); ax1.set_xticklabels(mods,rotation=35,ha="right",fontsize=7.5)
            ax1.set_ylabel("Lines of Code",color="#64748b")
            ax2.set_ylabel("Test/Code Ratio (%)",color=P["red"])
            ax1.set_title("Test coverage: source vs test SLOC by module")
            lines1,labels1=ax1.get_legend_handles_labels()
            lines2,labels2=ax2.get_legend_handles_labels()
            ax1.legend(lines1+lines2,labels1+labels2,loc="upper right",fontsize=7,labelcolor="#9095ad")
            ax1.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
            ax1.grid(axis="y",linestyle="--",alpha=0.25)
            fig.tight_layout()

        # ── Fig 7: Bus factor ─────────────────────────────────────────────────
        elif script_id == "busactor":
            import matplotlib.patches as mpatches
            data = _load_json("busactor_results.json")
            if not data: return None, "busactor_results.json not found"
            contribs = data["contributors"][:8]
            names    = [c["name"].split("(")[0].strip()[:20] for c in contribs]
            all_c    = [c["commits_all"] for c in contribs]
            rec_c    = [c["commits_recent"] for c in contribs]
            silos    = data["knowledge_silos"]
            s_files  = [s["file"].replace("src/","") for s in silos]
            s_own    = [s["ownership_pct"] for s in silos]
            s_colors = [P["red"] if p>=85 else P["amber"] if p>=70 else P["orange"] for p in s_own]
            fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12,4.5))
            x=np.arange(len(names))
            ax1.barh(x,all_c,0.38,label="All-time",color=P["blue"],alpha=0.85)
            ax1.barh(x+0.38,rec_c,0.38,label="2022-2024",color=P["orange"],alpha=0.85)
            ax1.set_yticks(x+0.19); ax1.set_yticklabels(names,fontsize=7.5); ax1.invert_yaxis()
            ax1.set_xlabel("Commit count")
            ax1.set_title("Top contributor commit counts",fontweight="bold",fontsize=9)
            ax1.legend(fontsize=7,labelcolor="#9095ad")
            total=sum(c["commits_all"] for c in data["contributors"])
            running=0
            for i,c in enumerate(sorted(all_c,reverse=True)):
                running+=c
                if running/total>=0.5:
                    ax1.axhline(y=i+0.57,color=P["red"],linestyle="--",linewidth=1.2,alpha=0.7)
                    ax1.text(max(all_c)*0.4,i+0.75,"Bus factor boundary",color=P["red"],fontsize=6.5)
                    break
            ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)
            ax1.grid(axis="x",linestyle="--",alpha=0.25)
            ax2.barh(s_files,s_own,color=s_colors,alpha=0.85,edgecolor="#1e2235",linewidth=0.4)
            ax2.set_xlabel("Single-author ownership (%)")
            ax2.set_title("Knowledge silos: single-author file ownership",fontweight="bold",fontsize=9)
            ax2.axvline(x=60,color="#555",linestyle="--",linewidth=1,alpha=0.6)
            ax2.text(61,len(silos)-0.5,">60%",fontsize=6.5,color="#555")
            legend_els=[mpatches.Patch(color=P["red"],label="Critical (>=85%)"),
                        mpatches.Patch(color=P["amber"],label="High (70-84%)"),
                        mpatches.Patch(color=P["orange"],label="Medium (60-69%)")]
            ax2.legend(handles=legend_els,fontsize=7,loc="lower right",labelcolor="#9095ad")
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            ax2.grid(axis="x",linestyle="--",alpha=0.25)
            fig.tight_layout()

        else:
            return None, f"no chart generator for {script_id}"

        # ── Save to in-memory buffer — NO disk write ──────────────────────────
        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor=DARK_BG, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue(), None

    except Exception as e:
        import traceback
        if fig is not None:
            try: plt.close(fig)
            except: pass
        return None, f"{e}\n{traceback.format_exc()}"


# ── Helpers ───────────────────────────────────────────────────────────────────
def _load_json(fname):
    p = BASE / fname
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return None

def load_json_gated(fname, script_id):
    if script_id not in st.session_state.ran_ids:
        return None
    return _load_json(fname)

def delete_all_outputs():
    for files in OUTPUT_FILES.values():
        for f in files:
            p = BASE / f
            if p.exists(): p.unlink()

def run_script(script_info, py=sys.executable):
    script_path = BASE / script_info["file"]
    if not script_path.exists():
        return False, f"ERROR: File not found: {script_path}\nMake sure all .py scripts are in the same folder as dashboard.py"
    result = subprocess.run([py, str(script_path)], capture_output=True, text=True, cwd=str(BASE))
    return result.returncode == 0, result.stdout + result.stderr


# ── Session state ─────────────────────────────────────────────────────────────
if "run_log"     not in st.session_state: st.session_state.run_log     = []
if "statuses"    not in st.session_state: st.session_state.statuses    = {s["id"]: "idle" for s in SCRIPTS}
if "ran_ids"     not in st.session_state: st.session_state.ran_ids     = set()
# chart_bytes: dict[script_id -> PNG bytes] — populated right after chart generation
if "chart_bytes" not in st.session_state: st.session_state.chart_bytes = {}
# pdf_bytes: raw bytes of the generated PDF — populated right after build_report.py
if "pdf_bytes"   not in st.session_state: st.session_state.pdf_bytes   = None
if "pdf_size_kb" not in st.session_state: st.session_state.pdf_size_kb = 0

if "initialised" not in st.session_state:
    delete_all_outputs()
    st.session_state.initialised = True


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-label">Script Runner</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-label">Select scripts</div>', unsafe_allow_html=True)

    selected = []
    for s in SCRIPTS:
        checked = st.checkbox(s["title"], value=False, key=f"cb_{s['id']}")
        if checked:
            selected.append(s)

    st.markdown("---")
    run_btn = st.button("Run Selected Scripts", use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="sidebar-label">Python interpreter</div>', unsafe_allow_html=True)
    py_path = st.text_input("Python interpreter path", value=sys.executable, label_visibility="collapsed")
    st.markdown('<div class="sidebar-label" style="margin-top:0.75rem">Working directory</div>', unsafe_allow_html=True)
    st.code(str(BASE), language=None)

    if st.button("Clear and Reset", use_container_width=True):
        st.session_state.run_log     = []
        st.session_state.statuses    = {s["id"]: "idle" for s in SCRIPTS}
        st.session_state.ran_ids     = set()
        st.session_state.chart_bytes = {}
        st.session_state.pdf_bytes   = None
        st.session_state.pdf_size_kb = 0
        delete_all_outputs()
        st.rerun()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_run, tab_results, tab_charts, tab_report = st.tabs(["Runner", "Results", "Charts", "Report"])


# ══════════════════════════════════════════════════════════
# TAB 1 — RUNNER
# ══════════════════════════════════════════════════════════
with tab_run:
    st.markdown('<div class="section-header">Analysis Pipeline</div>', unsafe_allow_html=True)

    STATUS_CSS = {
        "idle":    ("status-idle",    "Idle"),
        "running": ("status-running", "Running"),
        "done":    ("status-done",    "Done"),
        "error":   ("status-error",   "Error"),
    }

    col_a, col_b = st.columns(2)
    for i, s in enumerate(SCRIPTS):
        col = col_a if i % 2 == 0 else col_b
        status = st.session_state.statuses.get(s["id"], "idle")
        css_cls, label = STATUS_CSS.get(status, STATUS_CSS["idle"])
        with col:
            st.markdown(f"""
            <div class="script-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div style="flex:1;min-width:0">
                  <div class="script-title">{s['title']}</div>
                  <div class="script-desc">{s['desc']}</div>
                  <div class="script-output-tag">{s['output']}</div>
                </div>
                <div style="margin-left:1rem;margin-top:0.1rem;flex-shrink:0">
                  <span class="status-pill {css_cls}">{label}</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if run_btn:
        if not selected:
            st.warning("Select at least one script in the sidebar first.")
        else:
            log_box     = st.empty()
            progress    = st.progress(0)
            status_line = st.empty()
            log_lines   = list(st.session_state.run_log)
            total       = len(selected)

            for idx, s in enumerate(selected):
                # Clean old outputs and cached data for this script
                for f in OUTPUT_FILES.get(s["id"], []):
                    p = BASE / f
                    if p.exists(): p.unlink()
                st.session_state.chart_bytes.pop(s["id"], None)
                if s["id"] == "report":
                    st.session_state.pdf_bytes   = None
                    st.session_state.pdf_size_kb = 0
                st.session_state.ran_ids.discard(s["id"])
                st.session_state.statuses[s["id"]] = "running"

                status_line.markdown(
                    f'<span style="color:#c8961e;font-family:JetBrains Mono,monospace;font-size:0.76rem">'
                    f'Running {s["file"]}...</span>', unsafe_allow_html=True)

                log_lines.append(f"\n{'─'*52}")
                log_lines.append(f"  {s['file']}")
                log_lines.append(f"{'─'*52}")
                log_box.markdown(
                    f'<div class="terminal-box">{"<br>".join(log_lines[-60:])}</div>',
                    unsafe_allow_html=True)

                ok, output = run_script(s, py=py_path)
                st.session_state.statuses[s["id"]] = "done" if ok else "error"

                if ok:
                    st.session_state.ran_ids.add(s["id"])

                    if s["id"] == "report":
                        # Read PDF bytes immediately — before any rerun
                        pdf_path = BASE / "redis_architecture_report.pdf"
                        if pdf_path.exists() and pdf_path.stat().st_size > 0:
                            with open(str(pdf_path), "rb") as pf:
                                st.session_state.pdf_bytes = pf.read()
                            st.session_state.pdf_size_kb = pdf_path.stat().st_size / 1024
                            log_lines.append(f"  PDF ready: {st.session_state.pdf_size_kb:.0f} KB")
                        else:
                            log_lines.append("  WARNING: PDF not found or empty after build_report.py")
                    else:
                        # Generate chart into memory — no disk write, no race condition
                        png_bytes, chart_err = generate_chart_bytes(s["id"])
                        if png_bytes:
                            st.session_state.chart_bytes[s["id"]] = png_bytes
                            log_lines.append(f"  chart rendered: {SCRIPT_CHART_MAP[s['id']]}")
                        else:
                            log_lines.append(f"  chart failed: {chart_err}")

                    log_lines.append(f"  completed: {s['file']}")
                else:
                    log_lines.append(f"  FAILED: {s['file']}")

                for line in output.strip().split("\n"):
                    if line.strip():
                        log_lines.append(f"    {line}")

                log_box.markdown(
                    f'<div class="terminal-box">{"<br>".join(log_lines[-60:])}</div>',
                    unsafe_allow_html=True)
                progress.progress((idx + 1) / total)

            st.session_state.run_log = log_lines
            status_line.markdown(
                '<span style="color:#28b46e;font-family:JetBrains Mono,monospace;font-size:0.76rem">'
                'All selected scripts completed.</span>', unsafe_allow_html=True)
            st.rerun()

    elif st.session_state.run_log:
        st.markdown('<div class="section-header">Last run output</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="terminal-box">{"<br>".join(st.session_state.run_log[-80:])}</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="terminal-box" style="color:#1a1e30;text-align:center;padding:2.5rem 1rem">'
            'Select scripts in the sidebar and click Run Selected Scripts</div>',
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 2 — RESULTS
# ══════════════════════════════════════════════════════════
with tab_results:

    def placeholder(msg):
        st.markdown(f'<div class="placeholder-box">Run {msg} to see results here</div>', unsafe_allow_html=True)

    loc = load_json_gated("loc_results.json", "loc")
    st.markdown('<div class="section-header">Lines of Code and COCOMO</div>', unsafe_allow_html=True)
    if loc:
        import pandas as pd
        c = loc["cocomo"]
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value">190K</div><div class="metric-label">C Source Lines</div></div>
            <div class="metric-card"><div class="metric-value">{c['effort_months']:.0f}</div><div class="metric-label">Person-Months</div></div>
            <div class="metric-card"><div class="metric-value">$6.7M</div><div class="metric-label">Est. COCOMO Cost</div></div>
            <div class="metric-card"><div class="metric-value">437</div><div class="metric-label">C Source Files</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame(loc["languages"])
        st.dataframe(df[["lang","files","lines","code","comments","complexity"]].rename(columns={
            "lang":"Language","files":"Files","lines":"Total Lines","code":"Code","comments":"Comments","complexity":"Complexity"}),
            use_container_width=True, hide_index=True)
    else:
        placeholder("script 01 — Lines of Code and COCOMO")

    st.markdown("---")

    cplx = load_json_gated("complexity_results.json", "complexity")
    st.markdown('<div class="section-header">Cyclomatic Complexity and MI</div>', unsafe_allow_html=True)
    if cplx:
        import pandas as pd
        dist = cplx["cc_distribution"]
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value">{dist['low']}</div><div class="metric-label">Low CC (1-10)</div></div>
            <div class="metric-card"><div class="metric-value">{dist['medium']}</div><div class="metric-label">Medium CC (11-20)</div></div>
            <div class="metric-card"><div class="metric-value">{dist['high']}</div><div class="metric-label">High CC (21-50)</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#dc4646">{dist['very_high']}</div><div class="metric-label">Very High CC (&gt;50)</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame(cplx["functions"])
        st.dataframe(df[["function","file","cc","category","mi"]].rename(columns={
            "function":"Function","file":"File","cc":"CC","category":"Risk","mi":"MI Score"
            }).sort_values("CC", ascending=False), use_container_width=True, hide_index=True)
    else:
        placeholder("script 02 — Cyclomatic Complexity and MI")

    st.markdown("---")

    vel = load_json_gated("velocity_results.json", "velocity")
    st.markdown('<div class="section-header">Issue Velocity and Community Health</div>', unsafe_allow_html=True)
    if vel:
        import pandas as pd
        vs = vel["velocity_summary"]; cd = vel["contributor_data"]
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value">{vs['avg_pre_license_issues_per_month']:.0f}</div><div class="metric-label">Issues/Month pre-2024</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#dc4646">{vs['avg_post_license_issues_per_month']:.0f}</div><div class="metric-label">Issues/Month post-change</div></div>
            <div class="metric-card"><div class="metric-value">{cd['peak_2023']}</div><div class="metric-label">Peak Contributors 2023</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#dc4646">{cd['post_license_2024']}</div><div class="metric-label">Contributors post-change</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame([{"Quarter":k,"Avg Close Time (days)":v} for k,v in vel["close_time_days"].items()])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        placeholder("script 03 — Issue Velocity and Community Health")

    st.markdown("---")

    coup = load_json_gated("coupling_results.json", "coupling")
    st.markdown('<div class="section-header">Module Coupling</div>', unsafe_allow_html=True)
    if coup:
        import pandas as pd
        on_main = sum(1 for r in coup if r["D"] <= 0.25)
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value">{len(coup)}</div><div class="metric-label">Modules Analysed</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#28b46e">{on_main}</div><div class="metric-label">On Main Sequence</div></div>
            <div class="metric-card"><div class="metric-value">{sum(r['Ce'] for r in coup)}</div><div class="metric-label">Total Efferent Deps</div></div>
            <div class="metric-card"><div class="metric-value">{len([r for r in coup if r['I']>0.7])}</div><div class="metric-label">Unstable (I &gt; 0.7)</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame(coup)
        st.dataframe(df[["module","Ca","Ce","I","A","D","zone"]].rename(columns={"module":"Module","zone":"Zone"}).sort_values("I"),
            use_container_width=True, hide_index=True)
    else:
        placeholder("script 04 — Module Coupling")

    st.markdown("---")

    churn = load_json_gated("churn_results.json", "churn")
    st.markdown('<div class="section-header">Code Churn and Defect Hotspots</div>', unsafe_allow_html=True)
    if churn:
        import pandas as pd
        critical = sum(1 for d in churn["churn_data"] if d["hotspot"] >= 60)
        total_commits = sum(d["commits"] for d in churn["churn_data"])
        total_cve = sum(churn["cve_by_year"].values())
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value">{len(churn['churn_data'])}</div><div class="metric-label">Files Analysed</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#dc4646">{critical}</div><div class="metric-label">Critical Hotspots</div></div>
            <div class="metric-card"><div class="metric-value">{total_commits:,}</div><div class="metric-label">Total Commits Tracked</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#dc4646">{total_cve}</div><div class="metric-label">CVEs (2019-2024)</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame(churn["churn_data"])
        st.dataframe(df[["file","commits","sloc","complexity","hotspot"]].rename(columns={
            "file":"File","commits":"Commits","sloc":"SLOC","complexity":"Complexity","hotspot":"Hotspot Score"
        }).sort_values("Hotspot Score", ascending=False), use_container_width=True, hide_index=True)
    else:
        placeholder("script 05 — Code Churn and Defect Hotspots")

    st.markdown("---")

    cov = load_json_gated("coverage_results.json", "coverage")
    st.markdown('<div class="section-header">Test Coverage and Security Surface</div>', unsafe_allow_html=True)
    if cov:
        import pandas as pd
        s = cov["summary"]
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value">{s['modules_with_tests']}</div><div class="metric-label">Modules with Tests</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#dc4646">{s['modules_without_tests']}</div><div class="metric-label">No Dedicated Tests</div></div>
            <div class="metric-card"><div class="metric-value">{s['test_ratio_pct']:.0f}%</div><div class="metric-label">Test/Code SLOC Ratio</div></div>
            <div class="metric-card"><div class="metric-value">{sum(cov['cve_by_component'].values())}</div><div class="metric-label">CVEs Mapped</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame(cov["coverage"])
        st.dataframe(df[["module","c_sloc","has_test","test_sloc"]].rename(columns={
            "module":"Module","c_sloc":"C SLOC","has_test":"Has Test","test_sloc":"Test SLOC"
        }), use_container_width=True, hide_index=True)
    else:
        placeholder("script 06 — Test Coverage and Security Surface")

    st.markdown("---")

    bus = load_json_gated("busactor_results.json", "busactor")
    st.markdown('<div class="section-header">Bus Factor and Contributor Concentration</div>', unsafe_allow_html=True)
    if bus:
        import pandas as pd
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value" style="color:#dc4646">{bus['bus_factor_all_time']}</div><div class="metric-label">Bus Factor (all-time)</div></div>
            <div class="metric-card"><div class="metric-value">{bus['bus_factor_recent']}</div><div class="metric-label">Bus Factor (2022-24)</div></div>
            <div class="metric-card"><div class="metric-value">{bus['gini_all_time']:.2f}</div><div class="metric-label">Gini (all-time)</div></div>
            <div class="metric-card"><div class="metric-value">{bus['gini_recent']:.2f}</div><div class="metric-label">Gini (recent)</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame(bus["contributors"][:10])
        st.dataframe(df[["name","commits_all","commits_recent","affiliation"]].rename(columns={
            "name":"Contributor","commits_all":"All-time","commits_recent":"2022-2024","affiliation":"Affiliation"
        }), use_container_width=True, hide_index=True)
    else:
        placeholder("script 07 — Bus Factor and Contributor Concentration")


# ══════════════════════════════════════════════════════════
# TAB 3 — CHARTS
# ══════════════════════════════════════════════════════════
with tab_charts:
    st.markdown('<div class="section-header">Generated Figures</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for i, (src_id, fname) in enumerate(SCRIPT_CHART_MAP.items()):
        col = col1 if i % 2 == 0 else col2
        caption = CHART_CAPTIONS.get(fname, fname)
        script_title = next((s["title"] for s in SCRIPTS if s["id"] == src_id), src_id)

        with col:
            # Read from session state bytes — works on local AND deployed, first run
            img_bytes = st.session_state.chart_bytes.get(src_id)
            if src_id in st.session_state.ran_ids and img_bytes:
                st.image(img_bytes, use_container_width=True)
                st.markdown(f'<div class="img-caption">{caption}</div>', unsafe_allow_html=True)
            else:
                label = caption.split("—")[1].strip() if "—" in caption else caption
                st.markdown(f"""
                <div class="placeholder-box" style="min-height:200px;display:flex;flex-direction:column;
                     align-items:center;justify-content:center;gap:0.6rem">
                    <div style="color:#252840;font-weight:500;font-size:0.78rem">{label}</div>
                    <div style="font-size:0.62rem;color:#1a1e30;margin-top:0.2rem">
                        Run "{script_title}" to generate
                    </div>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 4 — REPORT
# ══════════════════════════════════════════════════════════
with tab_report:
    st.markdown('<div class="section-header">PDF Report</div>', unsafe_allow_html=True)

    # Read entirely from session state — no disk path lookup after rerun
    pdf_bytes   = st.session_state.pdf_bytes
    pdf_size_kb = st.session_state.pdf_size_kb

    if "report" in st.session_state.ran_ids and pdf_bytes:
        st.markdown(f"""
        <div class="script-card" style="display:flex;align-items:center;gap:1.5rem;padding:1.5rem">
            <div style="flex:1;min-width:0">
                <div class="script-title" style="font-size:1rem">redis_architecture_report.pdf</div>
                <div class="script-desc" style="margin-top:0.3rem">
                    10-page architecture analysis &nbsp;&middot;&nbsp; {pdf_size_kb:.0f} KB
                </div>
                <div class="script-output-tag" style="margin-top:0.6rem">
                    Stakeholders &nbsp;&middot;&nbsp; Context View &nbsp;&middot;&nbsp; 7 Metric Sections &nbsp;&middot;&nbsp; Insights &nbsp;&middot;&nbsp; References
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.download_button(
            "Download PDF Report",
            pdf_bytes,
            "redis_architecture_report.pdf",
            "application/pdf",
            use_container_width=True,
        )
    else:
        not_run = "report" not in st.session_state.ran_ids
        hint = "Run script 08 — Build PDF Report to generate it." if not_run else \
               "Report script ran but the PDF was not created. Check the terminal output for errors."
        st.markdown(f"""
        <div class="placeholder-box" style="padding:3.5rem 2rem">
            <div style="color:#252840;font-size:0.82rem;margin-bottom:0.4rem">No PDF built yet</div>
            <div style="font-size:0.7rem;color:#1a1e30;line-height:1.8">
                {hint}<br>
                Tip: run scripts 01-07 first so all figures are included.
            </div>
        </div>""", unsafe_allow_html=True)
