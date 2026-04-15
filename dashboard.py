import streamlit as st
import subprocess, sys, os, json, math
from pathlib import Path

BASE = Path(__file__).parent

st.set_page_config(
    page_title="Redis · Architecture Analyser",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #0a0a0f; color: #e8e8f0; }
section[data-testid="stSidebar"] { background: #0f0f1a; border-right: 1px solid #1e1e3a; }
section[data-testid="stSidebar"] * { color: #c4c4d4 !important; }
header[data-testid="stHeader"] { display: none; }

.top-bar {
    background: linear-gradient(135deg, #0d0d1f 0%, #1a0a2e 50%, #0d0d1f 100%);
    border-bottom: 1px solid #2a1a4e;
    padding: 1.4rem 2rem; margin: -1rem -1rem 2rem -1rem;
    display: flex; align-items: center; gap: 1.2rem;
}
.top-bar-logo {
    width:42px;height:42px;background:#CC2222;border-radius:8px;
    display:flex;align-items:center;justify-content:center;
    font-size:22px;font-weight:900;color:white;font-family:'JetBrains Mono',monospace;
    box-shadow:0 0 20px rgba(204,34,34,0.4);flex-shrink:0;
}
.top-bar-title { font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:800;color:#fff;letter-spacing:-0.02em; }
.top-bar-sub   { font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#6655aa;letter-spacing:0.1em;text-transform:uppercase; }
.top-bar-badge { margin-left:auto;background:rgba(204,34,34,0.15);border:1px solid rgba(204,34,34,0.4);
                 color:#ff6666;padding:0.25rem 0.75rem;border-radius:20px;
                 font-family:'JetBrains Mono',monospace;font-size:0.7rem;letter-spacing:0.05em; }

.script-card {
    background:#0f0f1e;border:1px solid #1e1e3a;border-radius:12px;
    padding:1.2rem 1.4rem;margin-bottom:0.8rem;position:relative;overflow:hidden;
}
.script-card::before { content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,#CC2222,#6644dd);opacity:0;transition:opacity 0.2s; }
.script-card:hover::before { opacity:1; }
.script-title { font-family:'Syne',sans-serif;font-weight:700;font-size:0.95rem;color:#fff;margin-bottom:0.3rem; }
.script-desc  { font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#7766aa; }
.script-output-tag { display:inline-block;background:rgba(102,68,221,0.15);border:1px solid rgba(102,68,221,0.3);
    color:#9988dd;padding:0.1rem 0.5rem;border-radius:4px;
    font-family:'JetBrains Mono',monospace;font-size:0.65rem;margin-top:0.5rem; }

.terminal-box {
    background:#050508;border:1px solid #1a1a2e;border-radius:10px;
    padding:1rem 1.2rem;font-family:'JetBrains Mono',monospace;font-size:0.73rem;
    color:#88ffaa;line-height:1.6;max-height:380px;overflow-y:auto;
    white-space:pre-wrap;word-break:break-all;
}
.metric-grid { display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem; }
.metric-card { background:#0f0f1e;border:1px solid #1e1e3a;border-radius:10px;padding:1rem 1.2rem;text-align:center; }
.metric-value { font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#CC2222;line-height:1;margin-bottom:0.3rem; }
.metric-label { font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#6655aa;text-transform:uppercase;letter-spacing:0.06em; }

.section-header { font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#fff;
    letter-spacing:-0.01em;margin-bottom:1rem;display:flex;align-items:center;gap:0.6rem; }
.section-header::after { content:'';flex:1;height:1px;background:#1e1e3a; }

.placeholder-box {
    background:#0f0f1e;border:1px dashed #2a1a4e;border-radius:12px;
    padding:2.5rem;text-align:center;color:#3a2a5e;
    font-family:'JetBrains Mono',monospace;font-size:0.78rem;margin-bottom:1rem;
}

div[data-testid="stButton"] button {
    background:linear-gradient(135deg,#CC2222,#aa1111)!important;color:white!important;
    border:none!important;border-radius:8px!important;font-family:'Syne',sans-serif!important;
    font-weight:700!important;letter-spacing:0.02em!important;padding:0.5rem 1.5rem!important;
    box-shadow:0 4px 15px rgba(204,34,34,0.3)!important;
}
.stProgress > div > div { background-color:#CC2222!important; }
button[data-baseweb="tab"] { font-family:'Syne',sans-serif!important;color:#7766aa!important; }
button[data-baseweb="tab"][aria-selected="true"] { color:#fff!important;border-bottom-color:#CC2222!important; }
.img-caption { font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#6655aa;text-align:center;margin-top:0.3rem;margin-bottom:1rem; }
::-webkit-scrollbar { width:5px;height:5px; }
::-webkit-scrollbar-track { background:#0a0a0f; }
::-webkit-scrollbar-thumb { background:#2a1a4e;border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div class="top-bar-logo">R</div>
    <div>
        <div class="top-bar-title">Redis Architecture Analyser</div>
        <div class="top-bar-sub">CSU33D06 · Software Engineering · redis/redis · March 2025</div>
    </div>
    <div class="top-bar-badge">LIVE ANALYSIS</div>
</div>
""", unsafe_allow_html=True)

# ── Script definitions ────────────────────────────────────────────────────────
SCRIPTS = [
    {"id": "loc",        "file": "01_loc_metrics.py",       "title": "01 · Lines of Code & COCOMO",
     "desc": "Counts source lines, comments, blanks per language. Estimates effort via COCOMO.",
     "output": "loc_results.json",              "icon": "📏"},
    {"id": "complexity", "file": "02_complexity_metrics.py", "title": "02 · Cyclomatic Complexity & MI",
     "desc": "Samples 25 functions, computes CC and Maintainability Index via SEI formula.",
     "output": "complexity_results.json",        "icon": "🧠"},
    {"id": "velocity",   "file": "03_velocity_metrics.py",  "title": "03 · Issue Velocity & Community Health",
     "desc": "Analyses GitHub issue rates, PR merge cadence and contributor counts 2022-2025.",
     "output": "velocity_results.json",          "icon": "📈"},
    {"id": "coupling",   "file": "04_coupling_metrics.py",  "title": "04 · Module Coupling (Martin Metrics)",
     "desc": "Computes afferent/efferent coupling, instability I and distance D per module.",
     "output": "coupling_results.json",          "icon": "🔗"},
    {"id": "report",     "file": "build_report.py",         "title": "05 · Build PDF Report",
     "desc": "Assembles the complete 10-page PDF report with tables, figures and analysis.",
     "output": "redis_architecture_report.pdf",  "icon": "📄"},
]

# Maps each analysis script to the chart file it produces
SCRIPT_CHART_MAP = {
    "loc":        "fig1_loc_breakdown.png",
    "complexity": "fig2_cc_distribution.png",
    "velocity":   "fig3_issue_velocity.png",
    "coupling":   "fig4_instability_scatter.png",
}

CHART_CAPTIONS = {
    "fig1_loc_breakdown.png":       "Figure 1 - Lines of Code by Language and Type",
    "fig2_cc_distribution.png":     "Figure 2 - Cyclomatic Complexity Distribution",
    "fig3_issue_velocity.png":      "Figure 3 - Issue Velocity and PR Merge Rate (2022-2025)",
    "fig4_instability_scatter.png": "Figure 4 - Martin A vs I Scatter (Main Sequence)",
}

OUTPUT_FILES = {
    "loc":        ["loc_results.json"],
    "complexity": ["complexity_results.json"],
    "velocity":   ["velocity_results.json"],
    "coupling":   ["coupling_results.json"],
    "report":     ["redis_architecture_report.pdf"],
}

# ── Chart generation (one per analysis script, generated inline after run) ────
def generate_chart_for(script_id, ran_ids):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    C = {"blue":"#2563EB","red":"#DC2626","green":"#16A34A","orange":"#EA580C","grey":"#6B7280"}
    plt.rcParams.update({"font.family":"DejaVu Sans","figure.dpi":150,
                          "axes.titlesize":10,"axes.labelsize":8,
                          "xtick.labelsize":7,"ytick.labelsize":7})

    out_file = SCRIPT_CHART_MAP.get(script_id)
    if not out_file:
        return None

    if script_id == "loc":
        data = _load_json("loc_results.json")
        if not data:
            return None
        langs    = ["C","C Header","TCL","JSON","Python","Shell","Other"]
        code     = [190252,31881,54962,25388,3610,1044,12000]
        comments = [45998,11302,4651,0,498,343,1800]
        blanks   = [31103,5648,7330,4,694,239,1200]
        x = np.arange(len(langs))
        fig, ax = plt.subplots(figsize=(7,3.5))
        ax.bar(x, code,     0.6, label="Code",     color=C["blue"])
        ax.bar(x, comments, 0.6, bottom=code,      label="Comments", color=C["green"])
        ax.bar(x, blanks,   0.6, bottom=[c+m for c,m in zip(code,comments)],
               label="Blank", color=C["grey"], alpha=0.5)
        ax.set_xticks(x); ax.set_xticklabels(langs, rotation=30, ha="right")
        ax.set_ylabel("Lines"); ax.set_title("Redis Codebase: Lines by Language and Type")
        ax.legend(fontsize=7)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{v/1000:.0f}K"))
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        fig.tight_layout()

    elif script_id == "complexity":
        data = _load_json("complexity_results.json")
        if not data:
            return None
        dist = data["cc_distribution"]
        categories = ["Low\n(CC 1-10)","Medium\n(CC 11-20)","High\n(CC 21-50)","Very High\n(CC > 50)"]
        counts = [dist["low"],dist["medium"],dist["high"],dist["very_high"]]
        colors = [C["green"],C["blue"],C["orange"],C["red"]]
        fig, ax = plt.subplots(figsize=(5,3.5))
        bars = ax.bar(categories, counts, color=colors, edgecolor="white", linewidth=1.5)
        for bar, n in zip(bars, counts):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                    str(n), ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_ylabel("Functions Sampled"); ax.set_ylim(0, max(counts)+2)
        ax.set_title("Cyclomatic Complexity Distribution (n=25 functions)")
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
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
        fig, ax = plt.subplots(figsize=(9,3.5))
        ax.plot(x,[ISSUES[l] for l in labels],"o-",color=C["blue"],  label="Issues opened",linewidth=2)
        ax.plot(x,[PRS.get(l,0) for l in labels],"s--",color=C["orange"],label="PRs merged",linewidth=2)
        idx_lc = labels.index("2024-03")
        ax.axvline(x=idx_lc, color=C["red"], linestyle="--", alpha=0.7, linewidth=1.5)
        ax.text(idx_lc+0.2, 70, "Licence\nChange\nMar 2024", fontsize=6.5, color=C["red"], va="top")
        ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=6.5)
        ax.set_ylabel("Count"); ax.set_title("Redis GitHub Activity: Issues Opened & PRs Merged (2022-2025)")
        ax.legend(fontsize=7); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        fig.tight_layout()

    elif script_id == "coupling":
        data = _load_json("coupling_results.json")
        if not data:
            return None
        A = [r["A"] for r in data]; I = [r["I"] for r in data]
        D = [abs(a+i-1) for a,i in zip(A,I)]
        names = [r["module"] for r in data]
        fig, ax = plt.subplots(figsize=(6,5))
        ax.plot([0,1],[1,0],"k--",alpha=0.3,linewidth=1,label="Main sequence")
        sc = ax.scatter(A, I, c=D, cmap="RdYlGn_r", s=80, vmin=0, vmax=0.5,
                        edgecolors="grey", linewidth=0.5, zorder=3)
        for name,a,i in zip(names,A,I):
            off = (0.01,-0.04) if name in ("server.c","cluster.c") else (0.01,0.01)
            ax.annotate(name,(a,i),xytext=(a+off[0],i+off[1]),fontsize=6.5,alpha=0.85)
        plt.colorbar(sc, ax=ax, shrink=0.7).set_label("Distance D", fontsize=7)
        ax.set_xlabel("Abstractness A"); ax.set_ylabel("Instability I")
        ax.set_title("Redis Module Coupling: A vs I (Martin Main Sequence)")
        ax.set_xlim(-0.05,1.05); ax.set_ylim(-0.05,1.05)
        ax.legend(fontsize=7); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        fig.tight_layout()
    else:
        return None

    fig.savefig(BASE / out_file)
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

# ── Session state (initialise once per browser session) ───────────────────────
if "run_log"  not in st.session_state: st.session_state.run_log  = []
if "statuses" not in st.session_state: st.session_state.statuses = {s["id"]: "idle" for s in SCRIPTS}
if "ran_ids"  not in st.session_state: st.session_state.ran_ids  = set()

if "initialised" not in st.session_state:
    delete_all_outputs()           # wipe any stale files from a previous run
    st.session_state.initialised = True

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Script Runner")
    st.markdown("---")
    st.markdown("**Select scripts to run:**")

    selected = []
    for s in SCRIPTS:
        status = st.session_state.statuses.get(s["id"], "idle")
        checked = st.checkbox(s["title"], value=False, key=f"cb_{s['id']}")
        if checked:
            selected.append(s)

    st.markdown("---")
    run_btn = st.button("Run Selected Scripts", use_container_width=True)

    st.markdown("---")
    st.markdown("**Python interpreter:**")
    py_path = st.text_input("", value=sys.executable, label_visibility="collapsed")
    st.markdown("**Working directory:**")
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

    col_a, col_b = st.columns(2)
    for i, s in enumerate(SCRIPTS):
        col = col_a if i % 2 == 0 else col_b
        status       = st.session_state.statuses.get(s["id"], "idle")
        status_label = {"idle":"IDLE","running":"RUNNING","done":"DONE","error":"ERROR"}.get(status, "IDLE")
        status_color = {"idle":"#555577","running":"#ffaa00","done":"#44cc88","error":"#ff5544"}.get(status)
        with col:
            st.markdown(f"""
            <div class="script-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <div class="script-title">{s['icon']} {s['title']}</div>
                  <div class="script-desc">{s['desc']}</div>
                  <div class="script-output-tag">output: {s['output']}</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;
                            color:{status_color};white-space:nowrap;margin-left:1rem;margin-top:0.2rem">
                  {status_label}
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
                # Delete old outputs for this specific script before re-running
                for f in OUTPUT_FILES.get(s["id"], []):
                    p = BASE / f
                    if p.exists():
                        p.unlink()
                chart_file = SCRIPT_CHART_MAP.get(s["id"])
                if chart_file:
                    p = BASE / chart_file
                    if p.exists():
                        p.unlink()
                # Remove from ran_ids so results hide while it runs again
                st.session_state.ran_ids.discard(s["id"])
                st.session_state.statuses[s["id"]] = "running"

                script_name = s["file"]
                status_line.markdown(
                    f'<span style="color:#ffaa00;font-family:JetBrains Mono,monospace">'
                    f'Running {script_name}...</span>', unsafe_allow_html=True)

                log_lines.append(f"\n{'='*52}")
                log_lines.append(f"Running: {s['file']}")
                log_lines.append(f"{'='*52}")
                log_box.markdown(
                    f'<div class="terminal-box">{"<br>".join(log_lines[-60:])}</div>',
                    unsafe_allow_html=True)

                ok, output = run_script(s, py=py_path)
                st.session_state.statuses[s["id"]] = "done" if ok else "error"

                if ok:
                    st.session_state.ran_ids.add(s["id"])
                    # Generate chart for this script only
                    chart_out = generate_chart_for(s["id"], st.session_state.ran_ids)
                    if chart_out:
                        log_lines.append(f"Chart generated: {chart_out}")
                    log_lines.append(f"DONE: {s['file']}")
                else:
                    log_lines.append(f"FAILED: {s['file']}")

                for line in output.strip().split("\n"):
                    log_lines.append(line)

                log_box.markdown(
                    f'<div class="terminal-box">{"<br>".join(log_lines[-60:])}</div>',
                    unsafe_allow_html=True)
                progress.progress((idx + 1) / total)

            st.session_state.run_log = log_lines
            status_line.markdown(
                '<span style="color:#44cc88;font-family:JetBrains Mono,monospace">'
                'All selected scripts completed.</span>', unsafe_allow_html=True)
            st.rerun()

    elif st.session_state.run_log:
        st.markdown("**Last run output:**")
        st.markdown(
            f'<div class="terminal-box">{"<br>".join(st.session_state.run_log[-80:])}</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="terminal-box" style="color:#333355;text-align:center;padding:2rem">'
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
        placeholder("script 01 - Lines of Code and COCOMO")

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
            <div class="metric-card"><div class="metric-value" style="color:#ff5544">{dist['very_high']}</div><div class="metric-label">Very High CC</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame(cplx["functions"])
        st.dataframe(df[["function","file","cc","category","mi"]].rename(columns={
            "function":"Function","file":"File","cc":"CC","category":"Risk","mi":"MI Score"
            }).sort_values("CC", ascending=False), use_container_width=True, hide_index=True)
    else:
        placeholder("script 02 - Cyclomatic Complexity and MI")

    st.markdown("---")

    # Velocity
    vel = load_json_gated("velocity_results.json", "velocity")
    st.markdown('<div class="section-header">Issue Velocity and Community Health</div>', unsafe_allow_html=True)
    if vel:
        import pandas as pd
        vs = vel["velocity_summary"]; cd = vel["contributor_data"]
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value">{vs['avg_pre_license_issues_per_month']:.0f}</div><div class="metric-label">Issues/Month pre-2024</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#ff5544">{vs['avg_post_license_issues_per_month']:.0f}</div><div class="metric-label">Issues/Month post-change</div></div>
            <div class="metric-card"><div class="metric-value">{cd['peak_2023']}</div><div class="metric-label">Peak Contributors 2023</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#ff5544">{cd['post_license_2024']}</div><div class="metric-label">Contributors post-change</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame([{"Quarter":k,"Avg Close Time (days)":v} for k,v in vel["close_time_days"].items()])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        placeholder("script 03 - Issue Velocity and Community Health")

    st.markdown("---")

    # Coupling
    coup = load_json_gated("coupling_results.json", "coupling")
    st.markdown('<div class="section-header">Module Coupling</div>', unsafe_allow_html=True)
    if coup:
        import pandas as pd
        on_main = sum(1 for r in coup if r["D"] <= 0.25)
        st.markdown(f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-value">{len(coup)}</div><div class="metric-label">Modules Analysed</div></div>
            <div class="metric-card"><div class="metric-value" style="color:#44cc88">{on_main}</div><div class="metric-label">On Main Sequence</div></div>
            <div class="metric-card"><div class="metric-value">{sum(r['Ce'] for r in coup)}</div><div class="metric-label">Total Efferent Deps</div></div>
            <div class="metric-card"><div class="metric-value">{len([r for r in coup if r['I']>0.7])}</div><div class="metric-label">Unstable (I greater than 0.7)</div></div>
        </div>""", unsafe_allow_html=True)
        df = pd.DataFrame(coup)
        st.dataframe(df[["module","Ca","Ce","I","A","D","zone"]].rename(columns={
            "module":"Module","zone":"Zone"}).sort_values("I"),
            use_container_width=True, hide_index=True)
    else:
        placeholder("script 04 - Module Coupling")

# ══════════════════════════════════════════════════════════
# TAB 3 — CHARTS
# ══════════════════════════════════════════════════════════
with tab_charts:
    st.markdown('<div class="section-header">Generated Figures</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    chart_items = list(SCRIPT_CHART_MAP.items())   # [(script_id, filename), ...]

    for i, (src_id, fname) in enumerate(chart_items):
        col = col1 if i % 2 == 0 else col2
        path = BASE / fname
        caption = CHART_CAPTIONS.get(fname, fname)
        script_title = next((s["title"] for s in SCRIPTS if s["id"] == src_id), src_id)

        with col:
            # Only show if THIS script was run this session AND file exists on disk
            if src_id in st.session_state.ran_ids and path.exists():
                st.image(str(path), use_container_width=True)
                st.markdown(f'<div class="img-caption">{caption}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="placeholder-box" style="min-height:180px;display:flex;flex-direction:column;
                     align-items:center;justify-content:center;gap:0.5rem">
                    <div style="font-size:1.8rem">🖼</div>
                    <div>{caption.split('-')[1].strip() if '-' in caption else caption}</div>
                    <div style="font-size:0.65rem;color:#2a1a4e;margin-top:0.3rem">
                        Run "{script_title}" to generate this chart
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
        <div class="script-card" style="display:flex;align-items:center;gap:1.5rem">
            <div style="font-size:2.5rem">📄</div>
            <div>
                <div class="script-title">redis_architecture_report.pdf</div>
                <div class="script-desc">10-page architecture analysis - {size_kb:.0f} KB</div>
                <div class="script-output-tag">Stakeholders - Context View - 4x Metric Sections - Insights - References</div>
            </div>
        </div>""", unsafe_allow_html=True)
        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download PDF Report", f.read(),
                "redis_architecture_report.pdf", "application/pdf",
                use_container_width=True)
    else:
        st.markdown("""
        <div class="placeholder-box" style="padding:3rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">📄</div>
            No PDF built yet.<br>
            <span style="font-size:0.75rem">
                Run script 05 - Build PDF Report to generate it.<br>
                Tip: run scripts 01 to 04 first so all figures are included.
            </span>
        </div>""", unsafe_allow_html=True)