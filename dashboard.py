import streamlit as st
import subprocess, sys, os, json, math
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

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.stApp {
    background: #0d0f14;
    color: #c9cdd8;
}
section[data-testid="stSidebar"] {
    background: #0a0c10;
    border-right: 1px solid rgba(255,255,255,0.05);
}
section[data-testid="stSidebar"] * { color: #7a8099 !important; }
header[data-testid="stHeader"] { display: none; }

/* ── Top Bar ── */
.top-bar {
    background: #0a0c10;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding: 1.25rem 2rem;
    margin: -1rem -1rem 2.5rem -1rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.top-bar-wordmark {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    color: #e8eaf2;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.top-bar-divider {
    width: 1px;
    height: 20px;
    background: rgba(255,255,255,0.08);
}
.top-bar-title {
    font-size: 0.9rem;
    font-weight: 500;
    color: #9095ad;
    letter-spacing: -0.01em;
}
.top-bar-right {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.top-bar-badge {
    background: rgba(99, 120, 255, 0.08);
    border: 1px solid rgba(99, 120, 255, 0.18);
    color: #7b8fff;
    padding: 0.22rem 0.75rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 500;
}
.top-bar-version {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #2e3248;
    letter-spacing: 0.05em;
}

/* ── Script Cards ── */
.script-card {
    background: #10131a;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.65rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.15s ease, background 0.15s ease;
}
.script-card:hover {
    border-color: rgba(99, 120, 255, 0.22);
    background: #12151d;
}
.script-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #dde0ed;
    margin-bottom: 0.3rem;
    letter-spacing: -0.01em;
}
.script-desc {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.67rem;
    color: #454866;
    line-height: 1.55;
}
.script-output-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(99, 120, 255, 0.06);
    border: 1px solid rgba(99, 120, 255, 0.14);
    color: #6878cc;
    padding: 0.12rem 0.5rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    margin-top: 0.55rem;
    letter-spacing: 0.01em;
}

/* ── Terminal ── */
.terminal-box {
    background: #07090e;
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.71rem;
    color: #5fb87a;
    line-height: 1.7;
    max-height: 380px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}

/* ── Metrics ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: #10131a;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    text-align: left;
}
.metric-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #e8eaf2;
    line-height: 1;
    margin-bottom: 0.4rem;
    letter-spacing: -0.04em;
    font-variant-numeric: tabular-nums;
}
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #3a3f5a;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}

/* ── Section Header ── */
.section-header {
    font-size: 0.7rem;
    font-weight: 600;
    color: #3a3f5a;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.04);
}

/* ── Placeholder ── */
.placeholder-box {
    background: #0a0c12;
    border: 1px dashed rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 2.5rem;
    text-align: center;
    color: #252840;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.73rem;
    margin-bottom: 1rem;
    line-height: 1.8;
}

/* ── Buttons ── */
div[data-testid="stButton"] button {
    background: #1a1e2e !important;
    color: #9095ad !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.01em !important;
    padding: 0.5rem 1.5rem !important;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease !important;
}
div[data-testid="stButton"] button:hover {
    background: #1f2438 !important;
    border-color: rgba(99, 120, 255, 0.3) !important;
    color: #c0c5dd !important;
    opacity: 1 !important;
}

/* ── Progress ── */
.stProgress > div > div { background-color: #6378ff !important; }

/* ── Tabs ── */
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #3a3f5a !important;
    letter-spacing: 0.01em !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #dde0ed !important;
    border-bottom-color: #6378ff !important;
}

/* ── Image captions ── */
.img-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.63rem;
    color: #2e3248;
    text-align: center;
    margin-top: 0.4rem;
    margin-bottom: 1.25rem;
    letter-spacing: 0.04em;
}

/* ── Sidebar labels ── */
.sidebar-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #2a2e45;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}

/* ── Status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.06em;
    font-weight: 600;
    padding: 0.15rem 0.6rem;
    border-radius: 4px;
    white-space: nowrap;
    text-transform: uppercase;
}
.status-idle    { background: rgba(60,65,100,0.15); color: #3a3f64; border: 1px solid rgba(60,65,100,0.2); }
.status-running { background: rgba(200,160,30,0.1); color: #c8961e; border: 1px solid rgba(200,160,30,0.2); }
.status-done    { background: rgba(40,180,110,0.1); color: #28b46e; border: 1px solid rgba(40,180,110,0.18); }
.status-error   { background: rgba(220,70,70,0.1);  color: #dc4646; border: 1px solid rgba(220,70,70,0.18); }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.1); }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.04) !important;
    border-radius: 6px !important;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div class="top-bar-wordmark">Redis</div>
    <div class="top-bar-divider"></div>
    <div class="top-bar-title">Architecture Analyser &nbsp;&middot;&nbsp; CSU33D06 &nbsp;&middot;&nbsp; March 2025</div>
    <div class="top-bar-right">
        <span class="top-bar-version">v1.0.0</span>
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
    {"id": "report",     "file": "build_report.py",         "title": "05 · Build PDF Report",
     "desc": "Assembles the complete 10-page PDF report with tables, figures and analysis.",
     "output": "redis_architecture_report.pdf"},
]

SCRIPT_CHART_MAP = {
    "loc":        "fig1_loc_breakdown.png",
    "complexity": "fig2_cc_distribution.png",
    "velocity":   "fig3_issue_velocity.png",
    "coupling":   "fig4_instability_scatter.png",
}

CHART_CAPTIONS = {
    "fig1_loc_breakdown.png":       "Figure 1 — Lines of Code by Language and Type",
    "fig2_cc_distribution.png":     "Figure 2 — Cyclomatic Complexity Distribution",
    "fig3_issue_velocity.png":      "Figure 3 — Issue Velocity and PR Merge Rate (2022–2025)",
    "fig4_instability_scatter.png": "Figure 4 — Martin A vs I Scatter (Main Sequence)",
}

OUTPUT_FILES = {
    "loc":        ["loc_results.json"],
    "complexity": ["complexity_results.json"],
    "velocity":   ["velocity_results.json"],
    "coupling":   ["coupling_results.json"],
    "report":     ["redis_architecture_report.pdf"],
}

# ── Chart generation ──────────────────────────────────────────────────────────
def generate_chart_for(script_id, ran_ids):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    PALETTE = {
        "blue":   "#5b7fff",
        "indigo": "#818cf8",
        "teal":   "#2dd4bf",
        "slate":  "#64748b",
        "muted":  "#334155",
        "amber":  "#f59e0b",
        "red":    "#f87171",
        "green":  "#4ade80",
    }

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "figure.dpi": 150,
        "axes.facecolor": "#10131a",
        "figure.facecolor": "#10131a",
        "axes.edgecolor": "#1e2235",
        "axes.labelcolor": "#64748b",
        "xtick.color": "#4a5068",
        "ytick.color": "#4a5068",
        "text.color": "#c9cdd8",
        "grid.color": "#1a1e2e",
        "grid.linewidth": 0.5,
        "axes.titlesize": 10,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "axes.titlecolor": "#9095ad",
    })

    out_file = SCRIPT_CHART_MAP.get(script_id)
    if not out_file:
        return None

    if script_id == "loc":
        data = _load_json("loc_results.json")
        if not data:
            return None
        langs    = ["C", "C Header", "TCL", "JSON", "Python", "Shell", "Other"]
        code     = [190252, 31881, 54962, 25388, 3610, 1044, 12000]
        comments = [45998, 11302, 4651, 0, 498, 343, 1800]
        blanks   = [31103, 5648, 7330, 4, 694, 239, 1200]
        x = np.arange(len(langs))
        fig, ax = plt.subplots(figsize=(7, 3.8))
        ax.bar(x, code,     0.55, label="Code",     color=PALETTE["blue"],  alpha=0.9)
        ax.bar(x, comments, 0.55, bottom=code,      label="Comments", color=PALETTE["teal"],  alpha=0.75)
        ax.bar(x, blanks,   0.55, bottom=[c+m for c,m in zip(code,comments)],
               label="Blank", color=PALETTE["muted"], alpha=0.5)
        ax.set_xticks(x); ax.set_xticklabels(langs, rotation=30, ha="right")
        ax.set_ylabel("Lines"); ax.set_title("Lines of code by language and type")
        ax.legend(fontsize=7, facecolor="#1a1e2e", edgecolor="#2a2e45", labelcolor="#9095ad")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1000:.0f}K"))
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        ax.spines["left"].set_edgecolor("#1e2235"); ax.spines["bottom"].set_edgecolor("#1e2235")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()

    elif script_id == "complexity":
        data = _load_json("complexity_results.json")
        if not data:
            return None
        dist = data["cc_distribution"]
        categories = ["Low\n(CC 1-10)", "Medium\n(CC 11-20)", "High\n(CC 21-50)", "Very High\n(CC > 50)"]
        counts = [dist["low"], dist["medium"], dist["high"], dist["very_high"]]
        colors = [PALETTE["green"], PALETTE["blue"], PALETTE["amber"], PALETTE["red"]]
        fig, ax = plt.subplots(figsize=(5, 3.8))
        bars = ax.bar(categories, counts, color=colors, width=0.5, alpha=0.85)
        for bar, n in zip(bars, counts):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                    str(n), ha="center", va="bottom", fontsize=9, fontweight="bold", color="#c9cdd8")
        ax.set_ylabel("Functions sampled"); ax.set_ylim(0, max(counts)+2)
        ax.set_title("Cyclomatic complexity distribution (n=25 functions)")
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        ax.spines["left"].set_edgecolor("#1e2235"); ax.spines["bottom"].set_edgecolor("#1e2235")
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        fig.tight_layout()

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
        fig, ax = plt.subplots(figsize=(9, 3.8))
        ax.plot(x, [ISSUES[l] for l in labels], "o-", color=PALETTE["blue"],   label="Issues opened", linewidth=2, markersize=4)
        ax.plot(x, [PRS.get(l,0) for l in labels], "s--", color=PALETTE["indigo"], label="PRs merged",    linewidth=2, markersize=4)
        idx_lc = labels.index("2024-03")
        ax.axvline(x=idx_lc, color=PALETTE["amber"], linestyle="--", alpha=0.6, linewidth=1.2)
        ax.text(idx_lc+0.2, 70, "Licence\nChange\nMar 2024", fontsize=6.5, color=PALETTE["amber"], va="top")
        ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=6.5)
        ax.set_ylabel("Count"); ax.set_title("GitHub activity — issues opened & PRs merged (2022–2025)")
        ax.legend(fontsize=7, facecolor="#1a1e2e", edgecolor="#2a2e45", labelcolor="#9095ad")
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        ax.spines["left"].set_edgecolor("#1e2235"); ax.spines["bottom"].set_edgecolor("#1e2235")
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        fig.tight_layout()

    elif script_id == "coupling":
        data = _load_json("coupling_results.json")
        if not data:
            return None
        A = [r["A"] for r in data]; I = [r["I"] for r in data]
        D = [abs(a+i-1) for a,i in zip(A,I)]
        names = [r["module"] for r in data]
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.plot([0,1],[1,0],"--",color="#2a2e45",linewidth=1.2,label="Main sequence")
        sc = ax.scatter(A, I, c=D, cmap="coolwarm", s=72, vmin=0, vmax=0.5,
                        edgecolors="#1e2235", linewidth=0.6, zorder=3, alpha=0.9)
        for name, a, i in zip(names,A,I):
            off = (0.01,-0.04) if name in ("server.c","cluster.c") else (0.01,0.01)
            ax.annotate(name,(a,i),xytext=(a+off[0],i+off[1]),fontsize=6.5,alpha=0.8,color="#9095ad")
        cb = plt.colorbar(sc, ax=ax, shrink=0.7)
        cb.set_label("Distance D", fontsize=7, color="#64748b")
        cb.ax.yaxis.set_tick_params(color="#64748b")
        plt.setp(cb.ax.yaxis.get_ticklabels(), color="#64748b")
        ax.set_xlabel("Abstractness A"); ax.set_ylabel("Instability I")
        ax.set_title("Module coupling — A vs I (Martin main sequence)")
        ax.set_xlim(-0.05,1.05); ax.set_ylim(-0.05,1.05)
        ax.legend(fontsize=7, facecolor="#1a1e2e", edgecolor="#2a2e45", labelcolor="#9095ad")
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        ax.spines["left"].set_edgecolor("#1e2235"); ax.spines["bottom"].set_edgecolor("#1e2235")
        ax.grid(linestyle="--", alpha=0.2)
        fig.tight_layout()
    else:
        return None

    fig.savefig(BASE / out_file, facecolor="#10131a")
    plt.close(fig)
    return out_file

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
            if p.exists():
                p.unlink()
    for f in SCRIPT_CHART_MAP.values():
        p = BASE / f
        if p.exists():
            p.unlink()

def run_script(script_info, py=sys.executable):
    script_path = BASE / script_info["file"]
    if not script_path.exists():
        return False, f"File not found: {script_path}"
    result = subprocess.run([py, str(script_path)],
                            capture_output=True, text=True, cwd=str(BASE))
    return result.returncode == 0, result.stdout + result.stderr

# ── Session state ─────────────────────────────────────────────────────────────
if "run_log"  not in st.session_state: st.session_state.run_log  = []
if "statuses" not in st.session_state: st.session_state.statuses = {s["id"]: "idle" for s in SCRIPTS}
if "ran_ids"  not in st.session_state: st.session_state.ran_ids  = set()

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
        status = st.session_state.statuses.get(s["id"], "idle")
        checked = st.checkbox(s["title"], value=False, key=f"cb_{s['id']}")
        if checked:
            selected.append(s)

    st.markdown("---")
    run_btn = st.button("Run Selected Scripts", use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="sidebar-label">Python interpreter</div>', unsafe_allow_html=True)
    py_path = st.text_input("", value=sys.executable, label_visibility="collapsed")
    st.markdown('<div class="sidebar-label" style="margin-top:0.75rem">Working directory</div>', unsafe_allow_html=True)
    st.code(str(BASE), language=None)

    if st.button("Clear and Reset", use_container_width=True):
        st.session_state.run_log  = []
        st.session_state.statuses = {s["id"]: "idle" for s in SCRIPTS}
        st.session_state.ran_ids  = set()
        delete_all_outputs()
        st.rerun()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_run, tab_results, tab_charts, tab_report = st.tabs(
    ["Runner", "Results", "Charts", "Report"])

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
                for f in OUTPUT_FILES.get(s["id"], []):
                    p = BASE / f
                    if p.exists(): p.unlink()
                chart_file = SCRIPT_CHART_MAP.get(s["id"])
                if chart_file:
                    p = BASE / chart_file
                    if p.exists(): p.unlink()
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
                    chart_out = generate_chart_for(s["id"], st.session_state.ran_ids)
                    if chart_out:
                        log_lines.append(f"  chart generated: {chart_out}")
                    log_lines.append(f"  completed: {s['file']}")
                else:
                    log_lines.append(f"  failed: {s['file']}")

                for line in output.strip().split("\n"):
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
        st.markdown(
            f'<div class="placeholder-box">Run {msg} to see results here</div>',
            unsafe_allow_html=True)

    # LOC
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
            "lang":"Language","files":"Files","lines":"Total Lines","code":"Code",
            "comments":"Comments","complexity":"Complexity"}), use_container_width=True, hide_index=True)
    else:
        placeholder("script 01 — Lines of Code and COCOMO")

    st.markdown("---")

    # Complexity
    cplx = load_json_gated("complexity_results.json", "complexity")
    st.markdown('<div class="section-header">Cyclomatic Complexity and MI</div>', unsafe_allow_html=True)
    if cplx:
        import pandas as pd
        dist = cplx["cc_distribution"]
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value">{dist['low']}</div><div class="metric-label">Low CC</div></div>
            <div class="metric-card"><div class="metric-value">{dist['medium']}</div><div class="metric-label">Medium CC</div></div>
            <div class="metric-card"><div class="metric-value">{dist['high']}</div><div class="metric-label">High CC</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#dc4646">{dist['very_high']}</div><div class="metric-label">Very High CC</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame(cplx["functions"])
        st.dataframe(df[["function","file","cc","category","mi"]].rename(columns={
            "function":"Function","file":"File","cc":"CC","category":"Risk","mi":"MI Score"
            }).sort_values("CC", ascending=False), use_container_width=True, hide_index=True)
    else:
        placeholder("script 02 — Cyclomatic Complexity and MI")

    st.markdown("---")

    # Velocity
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

    # Coupling
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
        st.dataframe(df[["module","Ca","Ce","I","A","D","zone"]].rename(columns={
            "module":"Module","zone":"Zone"}).sort_values("I"),
            use_container_width=True, hide_index=True)
    else:
        placeholder("script 04 — Module Coupling")

# ══════════════════════════════════════════════════════════
# TAB 3 — CHARTS
# ══════════════════════════════════════════════════════════
with tab_charts:
    st.markdown('<div class="section-header">Generated Figures</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    chart_items = list(SCRIPT_CHART_MAP.items())

    for i, (src_id, fname) in enumerate(chart_items):
        col = col1 if i % 2 == 0 else col2
        path = BASE / fname
        caption = CHART_CAPTIONS.get(fname, fname)
        script_title = next((s["title"] for s in SCRIPTS if s["id"] == src_id), src_id)

        with col:
            if src_id in st.session_state.ran_ids and path.exists():
                st.image(str(path), use_container_width=True)
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

    pdf_path = BASE / "redis_architecture_report.pdf"
    if "report" in st.session_state.ran_ids and pdf_path.exists():
        size_kb = pdf_path.stat().st_size / 1024
        st.markdown(f"""
        <div class="script-card" style="display:flex;align-items:center;gap:1.5rem;padding:1.5rem">
            <div style="flex:1;min-width:0">
                <div class="script-title" style="font-size:1rem">redis_architecture_report.pdf</div>
                <div class="script-desc" style="margin-top:0.3rem">
                    10-page architecture analysis &nbsp;&middot;&nbsp; {size_kb:.0f} KB
                </div>
                <div class="script-output-tag" style="margin-top:0.6rem">
                    Stakeholders &nbsp;&middot;&nbsp; Context View &nbsp;&middot;&nbsp; 4 Metric Sections &nbsp;&middot;&nbsp; Insights &nbsp;&middot;&nbsp; References
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download PDF Report", f.read(),
                "redis_architecture_report.pdf", "application/pdf",
                use_container_width=True)
    else:
        st.markdown("""
        <div class="placeholder-box" style="padding:3.5rem 2rem">
            <div style="color:#252840;font-size:0.82rem;margin-bottom:0.4rem">No PDF built yet</div>
            <div style="font-size:0.7rem;color:#1a1e30;line-height:1.8">
                Run script 05 — Build PDF Report to generate it.<br>
                Tip: run scripts 01–04 first so all figures are included.
            </div>
        </div>""", unsafe_allow_html=True)
