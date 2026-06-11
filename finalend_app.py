import streamlit as st
import pandas as pd
import re
import io
import os
import tempfile
import warnings
import traceback
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

warnings.filterwarnings("ignore")

# ── Page config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="ProcessMine — Enterprise Batch Job Analyzer",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #fffdf8;
    --bg2: #f8f4ea;
    --bg3: #f1eadf;

    --border: #e6dccd;
    --border2: #d8c8b2;

    --accent: #9a6b2f;
    --accent2: #b07a36;
    --accent3: #d4a76a;

    --warn: #ffb800;
    --danger: #ff4757;

    --text: #5b4636;
    --text2: #8b7355;
    --text3: #b89b7a;

    --mono: 'Space Mono', monospace;
    --sans: 'DM Sans', sans-serif;
}
            
.block-container {
    padding-top: 1.5rem !important;
}

html, body, .stApp {
    font-family: var(--sans) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Main area */
.main .block-container {
    background: var(--bg) !important;
    padding: 2rem 2.5rem !important;
    max-width: 1400px !important;
}

/* Hide default elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── HEADER BANNER ── */
.pm-header {
    background: linear-gradient(135deg,
var(--bg) 0%,
var(--bg2) 100%);
    border: 1px solid var(--border);
box-shadow:
    0 2px 10px rgba(15, 23, 42, 0.04),
    0 1px 2px rgba(15, 23, 42, 0.06);
    border-radius: 12px;
    padding: 1.2rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    text-align: center;
}
.pm-title {
    font-family: var(--mono) !important;
    font-size: 1.8rem !important;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -1px;
    margin: 0;
    line-height: 1.1;
}
.pm-subtitle {
    font-size: 0.95rem;
    color: var(--text2);
    margin-top: 0.4rem;
    letter-spacing: 0.02em;
}
.pm-badge {
     display: inline-block;
    background: rgba(181,122,46,0.12);
    border: 1px solid rgba(181,122,46,0.25);
    color: var(--accent);
    font-family: var(--mono);
    font-size: 0.7rem;
    padding: 2px 10px;
    border-radius: 20px;
    margin-right: 8px;
    letter-spacing: 0.05em;
}

/* ── SECTION HEADERS ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2rem 0 1.2rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}
.section-num {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--accent);
    background: rgba(181,122,46,0.10);
    border: 1px solid rgba(181,122,46,0.20);
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.1em;
}
.section-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text);
    margin: 0;
}

/* ── METRIC CARDS ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin: 1rem 0;
}
.metric-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: var(--border2); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.blue::before  { background: var(--accent); }
.metric-card.green::before { background: var(--accent3); }
.metric-card.yellow::before{ background: var(--warn); }
.metric-card.red::before   { background: var(--danger); }
.metric-label {
    font-size: 0.72rem;
    color: var(--text3);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    font-family: var(--mono);
}
.metric-value {
    font-family: var(--mono);
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.metric-sub {
    font-size: 0.75rem;
    color: var(--text2);
    margin-top: 0.3rem;
}

/* ── CARDS ── */
.pm-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ── STATUS PILLS ── */
.pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-family: var(--mono);
    font-weight: 700;
}
.pill-green  {
    background: rgba(181,122,46,0.10);
    color: var(--accent);
    border: 1px solid rgba(181,122,46,0.20);
}

.pill-blue   {
    background: rgba(212,167,106,0.14);
    color: var(--accent);
    border: 1px solid rgba(212,167,106,0.24);
}
.pill-yellow { background: rgba(255,184,0,0.12); color: var(--warn);    border: 1px solid rgba(255,184,0,0.3); }
.pill-red    { background: rgba(255,71,87,0.12);  color: var(--danger);  border: 1px solid rgba(255,71,87,0.3); }

/* ── TABLES ── */
.stDataFrame { border-radius: 8px; overflow: hidden; }
[data-testid="stDataFrameResizable"] { border: 1px solid var(--border) !important; border-radius: 8px !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    color: white !important;
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.4rem !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── INPUTS ── */
.stFileUploader > div, .stSelectbox > div, .stTextInput > div, .stTextArea > div {
    background: var(--bg3) !important;
    border-color: var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
.stFileUploader label, .stSelectbox label, .stTextInput label, .stTextArea label,
.stNumberInput label, .stSlider label {
    color: var(--text2) !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.03em !important;
}

/* ── EXPANDER ── */
.stExpander {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
/* Expander OPEN */
details[open] summary {
    background: var(--bg2) !important;
}

/* Text preview saat OPEN */
details[open] summary * {
    color: var(--text) !important;
}
/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-bottom: 1px solid var(--border) !important;
    border-radius: 8px 8px 0 0 !important;
    gap: 24px !important;
    padding: 0.7rem 1.5rem !important;
    margin-right: 0.5rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text2) !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
    border-radius: 6px 6px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(181,122,46,0.12) !important;
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ── ALERTS ── */
.stSuccess { background: rgba(0,255,157,0.08) !important; border-color: var(--accent3) !important; border-radius: 8px !important; }
.stWarning { background: rgba(255,184,0,0.08) !important; border-color: var(--warn) !important; border-radius: 8px !important; }
.stError   { background: rgba(255,71,87,0.08)  !important; border-color: var(--danger) !important; border-radius: 8px !important; }
.stInfo    {  background: rgba(181,122,46,0.08) !important; border-color: var(--accent2) !important; border-radius: 8px !important; }

/* ── SIDEBAR STYLES ── */
.sidebar-logo {
    font-family: var(--mono);
    font-size: 1.1rem;
    color: var(--accent);
    font-weight: 700;
    letter-spacing: -0.5px;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.sidebar-section {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--text3);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.6rem 0;
}
.step-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 4px;
    font-size: 0.82rem;
}
.step-done   { background: rgba(0,255,157,0.08); color: var(--accent3); }
.step-active { background: rgba(181,122,46,0.12); color: var(--accent); }
.step-idle   { color: var(--text3); }

/* Progress bar custom */
.stProgress > div > div { background: linear-gradient(90deg, var(--accent2), var(--accent)) !important; border-radius: 4px !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] section {
    background: linear-gradient(135deg,
var(--bg) 0%,
var(--bg2) 100%) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 0.5rem !important;
    box-shadow:
        0 2px 10px rgba(15, 23, 42, 0.04),
        0 1px 2px rgba(15, 23, 42, 0.06);
}

[data-testid="stFileUploader"] section:hover {
    border-color: var(--accent) !important;
}

/* Text drag and drop */
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section div,
[data-testid="stFileUploader"] label {
    color: var(--text) !important;
}

/* Browse button ONLY */
[data-testid="stFileUploader"] section button {
    background: #9a6b2f !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

[data-testid="stFileUploader"] section button:hover {
    background: #7c5422 !important;
}

            
/* Uploaded file area */
[data-testid="stFileUploaderFile"] {
    background: #f8f4ea !important;

    border: 1px solid #ebe7df !important;

    border-radius: 14px !important;

    padding: 0.85rem 1rem !important;

    box-shadow:
        0 1px 3px rgba(0,0,0,0.04);
}

/* Hilangkan background abu bawaan */
[data-testid="stFileUploaderFileData"] {
    background: transparent !important;
}

/* Nama file */
[data-testid="stFileUploaderFileName"] {
    color: var(--text) !important;

    font-weight: 500 !important;

    font-size: 0.95rem !important;
}

/* File size */
[data-testid="stFileUploaderFileSize"] {
    color: var(--text2) !important;
}

/* Semua text di uploader */
[data-testid="stFileUploaderFile"] * {
    color: var(--text) !important;
}

/* Icon file */
[data-testid="stFileUploaderFile"] svg {
    color: #9a6b2f !important;
}

/* Tombol X */
[data-testid="stFileUploaderDeleteBtn"] {
    border-radius: 0 !important;

    background: transparent !important;

    padding: 0 !important;

    width: auto !important;
    height: auto !important;

    min-width: unset !important;
}

/* Icon X */
[data-testid="stFileUploaderDeleteBtn"] svg {
    color: var(--accent) !important;

    width: 18px !important;
    height: 18px !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# HELPER FUNCTIONS



def parse_log_with_mapping(log_text: str, mapping: list[dict]) -> pd.DataFrame:
    """
    Generic log parser. mapping = [{'keyword': '...', 'activity': '...'}, ...]
    Automatically detects case boundaries using configurable begin/end keywords.
    """
    time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[,.]?\d*)")

    # Sort mapping: longer keywords first to avoid partial matches
    sorted_mapping = sorted(
        mapping, key=lambda x: len(x.get("keyword", "0")), reverse=True
    )

    begin_kw = next(
        (m["keyword"] for m in mapping if m["activity"] == "Start Batch"), "BEGIN"
    )
    end_kw = next(
        (m["keyword"] for m in mapping if m["activity"] == "End Process"), "END"
    )
    case_kw = next(
        (m.get("case_keyword", "") for m in mapping if m.get("case_keyword")), ""
    )
    case_pat = re.compile(m.get("case_pattern", r"([A-Z0-9_]+)")) if case_kw else None

    events = []
    current_case_id = None
    case_counter = 0
    temp_events = []
    seen_flags = {}  # for dedup per case

    lines = log_text.splitlines()

    for line in lines:
        # Skip noise lines
        if any(skip in line for skip in [" at ", "parameters:", "Caused by:", "\tat "]):
            continue

        m_time = time_pattern.search(line)
        if not m_time:
            continue

        raw_ts = m_time.group(1).replace(",", ".")
        try:
            # Try multiple formats
            for fmt in [
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
            ]:
                try:
                    ts = datetime.strptime(raw_ts[:26], fmt)
                    break
                except:
                    continue
            else:
                continue
        except:
            continue

        # Detect case start
        if begin_kw and begin_kw in line:
            case_counter += 1
            current_case_id = f"CASE_{case_counter:05d}"
            seen_flags = {}
            temp_events = []

        if current_case_id is None:
            continue

        # Try to extract a more meaningful case ID if case_keyword is configured
        if case_kw and case_kw in line and case_pat:
            m_case = case_pat.search(line)
            if m_case:
                current_case_id = f"{m_case.group(1)}_{case_counter:05d}"
                # Backfill
                for ev in temp_events:
                    ev["case:concept:name"] = current_case_id

        # Match activity
        matched_activity = None
        for rule in sorted_mapping:
            kw = rule.get("keyword", "")
            act = rule.get("activity", "")
            dedup = rule.get("dedup", False)

            if kw and kw in line:
                if dedup:
                    if act in seen_flags:
                        break
                    seen_flags[act] = True
                matched_activity = act
                break

        if matched_activity:
            ev = {
                "case:concept:name": current_case_id,
                "concept:name": matched_activity,
                "time:timestamp": ts,
            }
            events.append(ev)
            temp_events.append(ev)

    if not events:
        return pd.DataFrame()

    df = pd.DataFrame(events)
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
    df = df.sort_values(["case:concept:name", "time:timestamp"]).reset_index(drop=True)
    return df


def compute_duration(df: pd.DataFrame) -> pd.DataFrame:
    """Add duration_ms = inter-event time within each case.
    Mengikuti logika notebook:
      1. Hitung inter-event time
      2. Drop last event per case (tidak punya next)
      3. Buang durasi NEGATIF (anomali timestamp)
      4. Buang outlier > P99 global
    """
    df = df.copy().sort_values(["case:concept:name", "time:timestamp"])
    df["next_ts"] = df.groupby("case:concept:name")["time:timestamp"].shift(-1)
    df["duration_ms"] = (df["next_ts"] - df["time:timestamp"]).dt.total_seconds() * 1000
    # Step 1: drop last event per case
    df = df.dropna(subset=["duration_ms"])
    # Step 2: buang durasi negatif (anomali timestamp di log) — sama seperti notebook
    df = df[df["duration_ms"] >= 0]
    # Step 3: buang outlier > P99 global
    q99 = df["duration_ms"].quantile(0.99)
    df = df[df["duration_ms"] <= q99].copy()
    return df


def compute_bottleneck_table(
    df_dur: pd.DataFrame, noise_acts: list = None
) -> pd.DataFrame:
    """Bottleneck analysis — persis 1:1 dengan notebook.

    Notebook:
        df_waktu = df_perf.copy()   # include semua activity
        exclude_acts = {Start Batch, End Batch} ∪ TECHNICAL_ACTIVITIES
        df_bottleneck = df_waktu[~exclude]  # buang dari ranking saja

    Di sini:
        df_dur = sudah berisi semua activity (dari df RAW)
        exclude = start_act + end_act + noise_acts (pilihan user)
        noise_acts menggantikan peran TECHNICAL_ACTIVITIES —
        user memilih sendiri activity mana yang ingin dibuang dari ranking.
    """
    import streamlit as _st
    _tfi = _st.session_state.get("trace_filter_info") or {}
    start_act = _tfi.get("start_act") or "Start Batch"
    end_act   = _tfi.get("end_act")   or "End Batch"

    # Exclude: start/end (penanda case) + noise pilihan user
    exclude_acts = {start_act, end_act} | set(noise_acts or [])
    df_f = df_dur[~df_dur["concept:name"].isin(exclude_acts)].copy()

    if df_f.empty:
        return pd.DataFrame()

    p95_vals = df_f.groupby("concept:name")["duration_ms"].quantile(0.95)

    grp = (
        df_f.groupby("concept:name")["duration_ms"]
        .agg(
            frekuensi="count",
            total_waktu="sum",
            rata_rata="mean",
            median="median",
            maks="max",
            variasi="std",
        )
        .reset_index()
    )

    grp["p95"]      = grp["concept:name"].map(p95_vals).round(1)
    grp["pct_total"] = (grp["total_waktu"] / grp["total_waktu"].sum() * 100).round(1)
    grp = grp.sort_values("total_waktu", ascending=False).reset_index(drop=True)
    grp.index = grp.index + 1

    for col in ["total_waktu", "rata_rata", "median", "maks", "variasi"]:
        grp[col] = grp[col].round(1)

    return grp


def compute_transition_delay(df_raw: pd.DataFrame, noise_acts: list = None) -> pd.DataFrame:
    """Transition delay — persis 1:1 dengan notebook.

    Notebook:
        df_trans = df_perf.copy()       # raw, semua activity
        hitung next_time & duration_ms dari scratch
        filter negatif
        exclude_trans = {Start,End} ∪ TECHNICAL_ACTIVITIES dari SOURCE
        P99 per-transisi (tidak ada filter frekuensi minimum)
        agregasi rata-rata, sort desc, head(10)

    Di sini noise_acts menggantikan TECHNICAL_ACTIVITIES.
    """
    import streamlit as _st
    _tfi = _st.session_state.get("trace_filter_info") or {}
    start_act = _tfi.get("start_act") or "Start Batch"
    end_act   = _tfi.get("end_act")   or "End Batch"

    exclude_src = {start_act, end_act} | set(noise_acts or [])

    df_t = df_raw.copy().sort_values(["case:concept:name", "time:timestamp"])

    # Hitung duration dari scratch — sama persis notebook
    df_t["_next_ts"]  = df_t.groupby("case:concept:name")["time:timestamp"].shift(-1)
    df_t["next_act"]  = df_t.groupby("case:concept:name")["concept:name"].shift(-1)
    df_t["duration_ms"] = (
        df_t["_next_ts"] - df_t["time:timestamp"]
    ).dt.total_seconds() * 1000
    df_t = df_t.drop(columns=["_next_ts"])

    df_t = df_t.dropna(subset=["next_act", "duration_ms"])
    df_t = df_t[df_t["duration_ms"] >= 0]

    # Exclude source setelah shift — temporal terjaga
    df_t = df_t[~df_t["concept:name"].isin(exclude_src)]
    df_t["transition"] = df_t["concept:name"] + " → " + df_t["next_act"]

    # P99 per-transisi — tidak ada filter frekuensi minimum (sama notebook)
    p99_per = df_t.groupby("transition")["duration_ms"].transform(
        lambda x: x.quantile(0.99)
    )
    df_t = df_t[df_t["duration_ms"] <= p99_per]

    result = (
        df_t.groupby("transition")["duration_ms"]
        .agg(
            frekuensi="count",
            rata_rata="mean",
            median="median",
            p95=lambda x: x.quantile(0.95),
        )
        .reset_index()
    )

    MIN_FREQ = 3
    n_excluded = int((result["frekuensi"] < MIN_FREQ).sum())
    result = result[result["frekuensi"] >= MIN_FREQ].copy()
    result.attrs["n_excluded_low_freq"] = n_excluded

    
    result = result.sort_values("rata_rata", ascending=False).reset_index(drop=True)
    result.index = result.index + 1
    for col in ["rata_rata", "median", "p95"]:
        result[col] = result[col].round(1)
    return result


def make_plotly_bar(df, x_col, y_col, title, color="#00d4ff", h=400):
    df_plot = df.head(10).copy()
    fig = go.Figure(
        go.Bar(
            x=df_plot[x_col],
            y=df_plot[y_col].str[:35]
            + ("…" if df_plot[y_col].str.len().max() > 35 else ""),
            orientation="h",
            marker=dict(
                color=df_plot[x_col],
                colorscale=[[0, "#E8DDD0"], [0.5, "#C4872F"], [1, "#B57A2E"]],
                showscale=False,
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            text=df_plot[x_col].round(1).astype(str),
            textposition="outside",
            textfont=dict(family="Space Mono", size=11, color="#5B4636"),
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(family="DM Sans", size=14, color="#5B4636")),
        paper_bgcolor="#F5F1EB",
        plot_bgcolor="#F5F1EB",
        font=dict(family="DM Sans", color="#5B4636"),
        height=h,
        yaxis=dict(
            autorange="reversed",
            gridcolor="#D6C2A8",
            tickfont=dict(size=11, family="Space Mono"),
        ),
        xaxis=dict(gridcolor="#D6C2A8", tickfont=dict(size=10)),
        margin=dict(l=10, r=80, t=40, b=20),
    )
    return fig


def fitness_gauge(value: float, label: str):

    percent = round(value * 100, 1)

    if value >= 0.8:
        color = "#B57A2E"
        status = "Excellent"
    elif value >= 0.5:
        color = "#D4A76A"
        status = "Moderate"
    else:
        color = "#D9534F"
        status = "Low"

    fig = go.Figure()

    # Progress bar
    fig.add_trace(
        go.Bar(
            x=[percent],
            y=[""],
            orientation="h",
            marker=dict(color=color, line=dict(color=color)),
            width=0.35,
            text=f"{percent}%",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(family="Space Mono", size=18, color="white"),
            hoverinfo="skip",
        )
    )

    # Background bar
    fig.add_trace(
        go.Bar(
            x=[100 - percent],
            y=[""],
            orientation="h",
            marker=dict(color="#E8DDD0"),
            width=0.35,
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        barmode="stack",
        title=dict(
            text=label, font=dict(family="DM Sans", size=18, color="#5B4636"), x=0
        ),
        paper_bgcolor="#F5F1EB",
        plot_bgcolor="#F5F1EB",
        font=dict(family="DM Sans", color="#5B4636"),
        xaxis=dict(
            range=[0, 100], showgrid=False, showticklabels=False, zeroline=False
        ),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        annotations=[
            dict(
                text=status,
                x=100,
                y=0,
                showarrow=False,
                font=dict(size=14, color=color, family="DM Sans"),
                xanchor="right",
            )
        ],
        height=180,
        margin=dict(t=60, b=20, l=20, r=20),
        showlegend=False,
    )

    return fig


def run_conformance(df: pd.DataFrame, bpmn_bytes):
    """Run conformance checking using pm4py."""
    import pm4py
    from pm4py.objects.log.util import dataframe_utils

    df_pm = df[["case:concept:name", "concept:name", "time:timestamp"]].copy()
    df_pm = pm4py.format_dataframe(
        df_pm,
        case_id="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )
    log = pm4py.convert_to_event_log(df_pm)

    # Load BPMN
    with tempfile.NamedTemporaryFile(suffix=".bpmn", delete=False) as f:
        f.write(bpmn_bytes)
        bpmn_path = f.name

    bpmn = pm4py.read_bpmn(bpmn_path)
    os.unlink(bpmn_path)
    net, im, fm = pm4py.convert_to_petri_net(bpmn)

    # Fitness
    fitness = pm4py.fitness_token_based_replay(log, net, im, fm)

    # FIX: Normalize perc_fit_traces — handle berbagai key & format pm4py
    raw_pct = (
        fitness.get("perc_fit_traces")
        or fitness.get("percentage_of_fitting_traces")
        or fitness.get("percFitTraces")
        or 0
    )
    fitness["perc_fit_traces"] = raw_pct  # pastikan key ini selalu ada & benar

    # Precision
    try:
        precision = pm4py.precision_token_based_replay(log, net, im, fm)
    except:
        try:
            precision = pm4py.precision_alignments(log, net, im, fm)
        except:
            precision = None

    # Alignments / deviations
    try:
        aligned = pm4py.conformance_diagnostics_alignments(log, net, im, fm)
        deviations = {}
        for trace_result in aligned:
            for move in trace_result.get("alignment", []):
                log_m, model_m = move
                if log_m == ">>" or model_m == ">>":
                    key = f"log: {log_m}  |  model: {model_m}"
                    deviations[key] = deviations.get(key, 0) + 1
        sorted_dev = sorted(deviations.items(), key=lambda x: x[1], reverse=True)
    except:
        sorted_dev = []

    return fitness, precision, sorted_dev


def run_discovery_viz(df: pd.DataFrame):
    """Run Heuristic Miner and return figure bytes."""
    import pm4py
    from pm4py.visualization.heuristics_net import visualizer as hn_viz

    df_pm = df[["case:concept:name", "concept:name", "time:timestamp"]].copy()
    df_pm = pm4py.format_dataframe(
        df_pm,
        case_id="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )
    log = pm4py.convert_to_event_log(df_pm)

    heu_net = pm4py.discover_heuristics_net(
        log,
        dependency_threshold=st.session_state.get("dep_thresh", 0.8),
        and_threshold=st.session_state.get("and_thresh", 0.65),
        loop_two_threshold=0.5,
    )

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        out_path = f.name

    gviz = hn_viz.apply(
        heu_net, parameters={hn_viz.Variants.PYDOTPLUS.value.Parameters.FORMAT: "png"}
    )
    hn_viz.save(gviz, out_path)

    with open(out_path, "rb") as f:
        img_bytes = f.read()
    os.unlink(out_path)
    return img_bytes


def get_variants(df: pd.DataFrame) -> pd.DataFrame:
    """Get process variants with frequency."""
    variants = df.groupby("case:concept:name")["concept:name"].apply(
        lambda x: " → ".join(x.tolist())
    )
    vc = variants.value_counts().reset_index()
    vc.columns = ["Variant Path", "Frequency"]
    vc["%"] = (vc["Frequency"] / vc["Frequency"].sum() * 100).round(1)
    vc.index = vc.index + 1
    return vc


# ═══════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════

defaults = {
    "df_raw": None,
    "df_clean": None,
    "df_dur": None,
    "mapping": [],
    "log_stats": {},
    "bottleneck_df": None,
    "transition_df": None,
    "fitness": None,
    "precision": None,
    "deviations": [],
    "discovery_img": None,
    "bpi_df": None,  # kept for legacy session compatibility
    "step": 0,  # 0=upload, 1=mapping, 2=parsed, 3=analyzed
    "dep_thresh": 0.8,
    "and_thresh": 0.65,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

# with st.sidebar:
#     st.markdown('<div class="sidebar-logo">⬡ ProcessMine</div>', unsafe_allow_html=True)

#     st.markdown('<div class="sidebar-section">PIPELINE STATUS</div>', unsafe_allow_html=True)

#     steps = [
#         (0, "01 — Upload Log File"),
#         (1, "02 — Configure Mapping"),
#         (2, "03 — Parse & Preview"),
#         (3, "04 — Run Analysis"),
#     ]
#     current = st.session_state.step
#     for idx, label in steps:
#         if idx < current:
#             cls = 'step-done'; icon = '✓'
#         elif idx == current:
#             cls = 'step-active'; icon = '▶'
#         else:
#             cls = 'step-idle'; icon = '○'
#         st.markdown(f'<div class="step-indicator {cls}">{icon} &nbsp;{label}</div>', unsafe_allow_html=True)

#     st.markdown('<div class="sidebar-section">DISCOVERY PARAMS</div>', unsafe_allow_html=True)
#     st.session_state.dep_thresh = st.slider("Dependency Threshold", 0.1, 1.0, 0.8, 0.05,
#         help="Min dependency strength to show an edge. Higher = simpler model.")
#     st.session_state.and_thresh = st.slider("AND Threshold", 0.1, 1.0, 0.65, 0.05,
#         help="Threshold for AND-split/join detection.")

#     st.markdown('<div class="sidebar-section">ABOUT</div>', unsafe_allow_html=True)
#     st.markdown("""<div style="font-size:0.78rem; color:#4a6278; line-height:1.6;">
#         Generic Process Mining Tool for Enterprise Batch Jobs.<br><br>
#         Supports any log format via configurable keyword mapping.<br><br>
#         Built with PM4Py + Streamlit.
#     </div>""", unsafe_allow_html=True)

#     if st.session_state.step >= 2 and st.session_state.df_clean is not None:
#         st.markdown('<div class="sidebar-section">QUICK STATS</div>', unsafe_allow_html=True)
#         s = st.session_state.log_stats
#         for label, val in [("Cases", s.get('total_cases','-')), ("Events", s.get('total_events','-')), ("Activities", s.get('unique_activities','-'))]:
#             st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #1e2a38;">
#                 <span style="font-size:0.78rem;color:#4a6278;">{label}</span>
#                 <span style="font-family:Space Mono;font-size:0.82rem;color:#00d4ff;">{val}</span>
#             </div>""", unsafe_allow_html=True)

#     if st.session_state.step >= 3:
#         st.markdown("<br>", unsafe_allow_html=True)
#         if st.button("🔄  Reset All"):
#             for k, v in defaults.items():
#                 st.session_state[k] = v
#             st.rerun()


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════

st.markdown(
    """
<div class="pm-header">
    <p class="pm-title">Analisa Confermance Checking dan Deteksi Bottleneck</p>
    <p class="pm-subtitle">Enterprise Batch Job — Process Mining</p>
    
</div>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════
# STEP 0: UPLOAD
# ═══════════════════════════════════════════════════════════════

st.markdown(
    """<div class="section-header">  
    <span class="section-title">Upload Event Log</span>
</div>""",
    unsafe_allow_html=True,
)

# col_up1, col_up2 = st.columns([2, 1])

# with col_up1:
#     uploaded_log = st.file_uploader(
#         "Upload file log (.txt, .log, .csv)",
#         type=['txt','log','csv'],
#         help="Upload raw log file dari sistem backend. Bisa dari job apapun."
#     )
uploaded_log = st.file_uploader(
    "Upload file log (.txt, .log, .csv)",
    type=["txt", "log", "csv"],
    help="Upload raw log file dari sistem backend. Bisa dari job apapun.",
)

st.markdown(
    """
    </div>
</div>
""",
    unsafe_allow_html=True,
)
# with col_up2:
#     st.markdown("""<div class="pm-card" style="height:100%;">
#         <div style="font-size:0.75rem;color:#4a6278;font-family:Space Mono;letter-spacing:0.05em;margin-bottom:0.8rem;">FORMAT YANG DIDUKUNG</div>
#         <div style="font-size:0.82rem;color:#8fa3bc;line-height:1.8;">
#         ✓ &nbsp;Raw text log (Java/Spring)<br>
#         ✓ &nbsp;Structured log (.log)<br>
#         ✓ &nbsp;CSV event log<br>
#         ✓ &nbsp;Any timestamp-based log
#         </div>
#     </div>""", unsafe_allow_html=True)

if uploaded_log:
    raw_bytes = uploaded_log.read()
    try:
        log_text = raw_bytes.decode("utf-8")
    except:
        log_text = raw_bytes.decode("latin-1")

    st.session_state["log_text"] = log_text

    # CSV path: auto-parse
    if uploaded_log.name.endswith(".csv"):
        try:
            df_csv = pd.read_csv(io.StringIO(log_text))
            # Try to auto-detect columns
            cols = df_csv.columns.str.lower().tolist()
            case_col = next(
                (
                    c
                    for c in df_csv.columns
                    if any(k in c.lower() for k in ["case", "id", "batch"])
                ),
                df_csv.columns[0],
            )
            act_col = next(
                (
                    c
                    for c in df_csv.columns
                    if any(
                        k in c.lower() for k in ["activity", "event", "action", "name"]
                    )
                ),
                df_csv.columns[1] if len(df_csv.columns) > 1 else df_csv.columns[0],
            )
            ts_col = next(
                (
                    c
                    for c in df_csv.columns
                    if any(k in c.lower() for k in ["time", "timestamp", "date", "ts"])
                ),
                df_csv.columns[2] if len(df_csv.columns) > 2 else df_csv.columns[0],
            )

            df_csv = df_csv.rename(
                columns={
                    case_col: "case:concept:name",
                    act_col: "concept:name",
                    ts_col: "time:timestamp",
                }
            )
            df_csv["time:timestamp"] = pd.to_datetime(
                df_csv["time:timestamp"], errors="coerce"
            )
            df_csv = df_csv.dropna(
                subset=["case:concept:name", "concept:name", "time:timestamp"]
            )
            df_csv = df_csv.sort_values(
                ["case:concept:name", "time:timestamp"]
            ).reset_index(drop=True)
            st.session_state.df_raw = df_csv
            st.session_state.step = 2
            st.success(
                f"✓ CSV parsed: {len(df_csv)} events, {df_csv['case:concept:name'].nunique()} cases"
            )
        except Exception as e:
            st.error(f"CSV parse error: {e}")
    else:
        st.session_state.step = max(st.session_state.step, 1)
        # Preview
        with st.expander("👁  Preview Log File (first 30 lines)", expanded=False):
            preview_lines = log_text.splitlines()[:30]
            st.code("\n".join(preview_lines), language="text")
        st.success(
            f"✓ File loaded: **{uploaded_log.name}** ({len(log_text):,} characters, {len(log_text.splitlines()):,} lines)"
        )


# ═══════════════════════════════════════════════════════════════
# STEP 1: MAPPING CONFIGURATION
# ═══════════════════════════════════════════════════════════════

if st.session_state.step >= 1 and not (
    uploaded_log and uploaded_log.name.endswith(".csv")
):
    st.markdown(
        """<div class="section-header">
        <span class="section-title">Configure Activity Mapping</span>
    </div>""",
        unsafe_allow_html=True,
    )

    # st.markdown("""<div class="pm-card">
    #     <div style="font-size:0.85rem;color:#8fa3bc;line-height:1.7;">
    #     Define how keywords in your log file map to activity names.
    #     This makes ProcessMine work with <b style="color:#00d4ff;">any batch job</b> — not just one specific system.<br>
    #     <span style="color:#4a6278;font-size:0.78rem;"> Tip: Keywords are matched in order — put more specific keywords first.</span>
    #     </div>
    # </div>""", unsafe_allow_html=True)

    tab_manual, tab_upload = st.tabs([" Manual Entry", " Upload CSV"])

    # ── TAB UPLOAD CSV ──
    with tab_upload:
        st.markdown(
            '<div style="font-size:0.82rem;color:var(--text2);margin-bottom:0.8rem;">Upload file <b>CSV</b> atau <b>Excel (.xlsx/.xls)</b> dengan kolom <b>keyword</b> dan <b>activity</b>. Urutan baris menentukan prioritas matching — keyword lebih spesifik taruh di atas.</div>',
            unsafe_allow_html=True,
        )
        mapping_file = st.file_uploader(
            "Upload mapping (CSV atau Excel — kolom: keyword, activity)",
            type=["csv", "xlsx", "xls"],
            key="mapping_upload",
        )
        if mapping_file:
            try:
                fname = mapping_file.name.lower()
                if fname.endswith(".xlsx") or fname.endswith(".xls"):
                    df_map = pd.read_excel(mapping_file)
                else:
                    df_map = pd.read_csv(mapping_file, sep=None, engine="python")

                df_map.columns = df_map.columns.str.strip()
                col_lower = {c.lower(): c for c in df_map.columns}
                kw_col  = col_lower.get("keyword")
                act_col = col_lower.get("activity")

                if kw_col is None or act_col is None:
                    st.error(
                        f"File harus punya kolom **keyword** dan **activity**. "
                        f"Kolom yang ditemukan: {list(df_map.columns)}"
                    )
                else:
                    df_map = df_map[[kw_col, act_col]].dropna(subset=[kw_col, act_col])
                    df_map.columns = ["keyword", "activity"]
                    df_map["keyword"]  = df_map["keyword"].astype(str).str.strip()
                    df_map["activity"] = df_map["activity"].astype(str).str.strip()
                    df_map = df_map[df_map["keyword"] != ""]

                    st.session_state.mapping = df_map.to_dict("records")
                    st.success(f"✓ {len(st.session_state.mapping)} mapping rules berhasil dimuat dari **{mapping_file.name}**")
                    st.dataframe(df_map, use_container_width=True, height=200)
            except Exception as e:
                st.error(f"Error membaca file: {e}")

    # ── TAB MANUAL ENTRY ──
    with tab_manual:
        st.markdown(
            '<div style="font-size:0.82rem;color:var(--text2);margin-bottom:0.8rem;">Tambah mapping satu per satu. Keyword lebih spesifik (panjang) taruh lebih dulu — sistem otomatis mengurutkan dari terpanjang.</div>',
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([4, 4, 1])
        with c1:
            new_kw = st.text_input(
                "Keyword (substring dalam baris log)",
                key="new_kw",
                placeholder="e.g. INSERT INTO RepaymentFile",
            )
        with c2:
            new_act = st.text_input(
                "Activity Name", key="new_act", placeholder="e.g. Insert Repayment Data"
            )
        with c3:
            st.write("")
            st.write("")
            if st.button("＋ Add", use_container_width=True):
                if new_kw and new_act:
                    st.session_state.mapping.append(
                        {"keyword": new_kw, "activity": new_act}
                    )
                    st.rerun()
                else:
                    st.warning("Keyword dan Activity tidak boleh kosong.")

        if st.session_state.mapping:
            df_m = pd.DataFrame(st.session_state.mapping)

            # Tampilkan tabel dengan tombol hapus per baris
            st.markdown(
                '<div style="font-size:0.78rem;color:var(--text3);font-family:var(--mono);letter-spacing:0.08em;margin:0.8rem 0 0.4rem 0;">MAPPING RULES (klik ✕ untuk hapus satu baris)</div>',
                unsafe_allow_html=True,
            )
            for i, row in enumerate(st.session_state.mapping):
                col_idx, col_kw, col_act, col_del = st.columns([0.5, 4, 4, 0.7])
                with col_idx:
                    st.markdown(
                        f'<div style="font-family:var(--mono);font-size:0.75rem;color:var(--text3);padding-top:0.55rem;text-align:center;">{i+1}</div>',
                        unsafe_allow_html=True,
                    )
                with col_kw:
                    st.markdown(
                        f'<div style="background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:0.4rem 0.8rem;font-size:0.82rem;color:var(--text);font-family:var(--mono);">{row["keyword"]}</div>',
                        unsafe_allow_html=True,
                    )
                with col_act:
                    st.markdown(
                        f'<div style="background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:0.4rem 0.8rem;font-size:0.82rem;color:var(--accent);">{row["activity"]}</div>',
                        unsafe_allow_html=True,
                    )
                with col_del:
                    if st.button("✕", key=f"del_{i}", help=f"Hapus: {row['keyword']}"):
                        st.session_state.mapping.pop(i)
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            # Export mapping yang sedang aktif
            csv_map_export = pd.DataFrame(st.session_state.mapping)[["keyword","activity"]].to_csv(index=False).encode()
            st.download_button(
                "Export Mapping Ini sebagai CSV",
                csv_map_export,
                "mapping_config.csv",
                "text/csv",
            )

    # PARSE BUTTON
    st.markdown("<br>", unsafe_allow_html=True)
    col_parse1, col_parse2, _ = st.columns([1, 2, 3])
    with col_parse2:
        if st.button("▶  PARSE EVENT LOG", use_container_width=True):
            if not st.session_state.mapping:
                st.error("Please configure at least one mapping rule first.")
            elif "log_text" not in st.session_state:
                st.error("Please upload a log file first.")
            else:
                with st.spinner("Parsing log file..."):
                    try:
                        df_raw = parse_log_with_mapping(
                            st.session_state.log_text, st.session_state.mapping
                        )
                        if df_raw.empty:
                            st.error(
                                "No events could be extracted. Check your keyword mapping."
                            )
                        else:
                            st.session_state.df_raw = df_raw
                            st.session_state.step = 2
                            st.rerun()
                    except Exception as e:
                        st.error(f"Parse error: {e}\n{traceback.format_exc()}")


# ═══════════════════════════════════════════════════════════════
# STEP 2: PREVIEW & STATS
# ═══════════════════════════════════════════════════════════════

if st.session_state.step >= 2 and st.session_state.df_raw is not None:
    df = st.session_state.df_raw.copy()

    # ── FILTER TRACE TIDAK LENGKAP (sama seperti notebook Cell 15) ──────────
    # Deteksi activity Start dan End dari mapping user — STRICT match
    # Prioritas: cari activity yang DIAWALI dengan "Start"/"Begin"/"End"
    # untuk menghindari false-positive (e.g. "Generate Batch Number" mengandung "end")
    _mapping = st.session_state.get("mapping", [])
    _all_acts_in_data = set(df["concept:name"].unique().tolist())

    def _find_act(mapping, data_acts, start_keywords, end_keywords, prefer_startswith=True):
        """Cari activity dari mapping yang ada di data, match by keyword."""
        # Pass 1: cari dari mapping — activity yang namanya diawali keyword
        for m in mapping:
            act = m["activity"]
            if act not in data_acts:
                continue
            act_l = act.lower()
            kws = start_keywords if prefer_startswith else end_keywords
            if prefer_startswith:
                if any(act_l.startswith(k) for k in kws):
                    return act
            else:
                if any(act_l.startswith(k) for k in kws):
                    return act
        # Pass 2: fallback — substring match dari mapping
        for m in mapping:
            act = m["activity"]
            if act not in data_acts:
                continue
            act_l = act.lower()
            kws = start_keywords if prefer_startswith else end_keywords
            if any(k in act_l for k in kws):
                return act
        # Pass 3: fallback dari data langsung
        for act in sorted(data_acts):
            act_l = act.lower()
            kws = start_keywords if prefer_startswith else end_keywords
            if any(act_l.startswith(k) for k in kws):
                return act
        return None

    _start_act = _find_act(_mapping, _all_acts_in_data,
                            start_keywords=["start", "begin"], end_keywords=[], prefer_startswith=True)
    _end_act   = _find_act(_mapping, _all_acts_in_data,
                            start_keywords=["end"], end_keywords=["end"], prefer_startswith=False)

    # Jika start/end ketemu, lakukan filter
    if _start_act and _end_act and _start_act != _end_act:
        _case_acts  = df.groupby("case:concept:name")["concept:name"].apply(set)
        _has_start  = _case_acts.apply(lambda x: _start_act in x)
        _has_end    = _case_acts.apply(lambda x: _end_act   in x)
        _complete   = _has_start & _has_end
        _n_before   = df["case:concept:name"].nunique()
        _complete_cases = _complete[_complete].index.tolist()
        df          = df[df["case:concept:name"].isin(_complete_cases)].reset_index(drop=True)
        _n_after    = df["case:concept:name"].nunique()
        _n_dropped  = _n_before - _n_after
        st.session_state["trace_filter_info"] = {
            "start_act": _start_act,
            "end_act":   _end_act,
            "before":    _n_before,
            "after":     _n_after,
            "dropped":   _n_dropped,
            "no_start":  int((~_has_start).sum()),
            "no_end":    int((~_has_end).sum()),
        }
    else:
        # Tidak bisa deteksi → skip filter, pakai semua data
        st.session_state["trace_filter_info"] = {
            "skipped": True,
            "start_act": _start_act,
            "end_act":   _end_act,
        }
    # ────────────────────────────────────────────────────────────────────────

    # Compute stats
    n_cases = df["case:concept:name"].nunique()
    n_events = len(df)
    n_acts = df["concept:name"].nunique()
    avg_acts = round(n_events / n_cases, 1) if n_cases else 0
    ts_min = df["time:timestamp"].min() if n_events > 0 else None
    ts_max = df["time:timestamp"].max() if n_events > 0 else None

    # Guard: jika semua case ter-drop, tampilkan error yang informatif
    if n_cases == 0:
        _tfi = st.session_state.get("trace_filter_info", {})
        _s = _tfi.get("start_act", "?") if _tfi else "?"
        _e = _tfi.get("end_act",   "?") if _tfi else "?"
        _acts_found = sorted(df["concept:name"].unique().tolist()) if len(st.session_state.df_raw) > 0 else []
        st.error(
            f"**0 case valid setelah filter kelengkapan trace.** "
            f"Activity start yang dicari: *{_s}*, activity end: *{_e}*. "
            f"Activity yang ada di data: `{_acts_found}`. "
            f"Pastikan mapping kamu punya activity yang namanya diawali 'Start'/'Begin' dan 'End'."
        )
        st.stop()

    st.session_state.df_clean = df
    st.session_state.log_stats = {
        "total_cases": n_cases,
        "total_events": n_events,
        "unique_activities": n_acts,
        "avg_acts_per_case": avg_acts,
        "date_start": str(ts_min.date()) if ts_min is not None else "-",
        "date_end":   str(ts_max.date()) if ts_max is not None else "-",
    }

    st.markdown(
        """<div class="section-header">
        <span class="section-title">Event Log Preview & Statistics</span>
    </div>""",
        unsafe_allow_html=True,
    )

    # ── INFO FILTER KELENGKAPAN TRACE ────────────────────────────────────────
    _tfi = st.session_state.get("trace_filter_info")
    if _tfi and not _tfi.get("skipped"):
        if _tfi.get("dropped", 0) > 0:
            st.warning(
                f"**Filter Kelengkapan Trace:** ditemukan **{_tfi['before']} case** → "
                f"**{_tfi['dropped']} case di-drop** karena tidak punya "
                f"*{_tfi['start_act']}* dan/atau *{_tfi['end_act']}* "
                f"({_tfi['no_start']} tanpa start, {_tfi['no_end']} tanpa end) → "
                f"**{_tfi['after']} case valid** digunakan untuk analisis."
            )
        else:
            st.success(
                f" **Filter Kelengkapan Trace:** Semua {_tfi['before']} case memiliki "
                f"*{_tfi['start_act']}* dan *{_tfi['end_act']}* — tidak ada yang di-drop."
            )
    elif _tfi and _tfi.get("skipped"):
        s = _tfi.get("start_act") or "?"
        e = _tfi.get("end_act") or "?"
        st.info(f" Filter kelengkapan trace dilewati — activity start (*{s}*) atau end (*{e}*) tidak terdeteksi dari mapping.")
    else:
        st.info(" Filter kelengkapan trace dilewati — activity start/end tidak terdeteksi dari mapping.")
    # ─────────────────────────────────────────────────────────────────────────

    # Metric cards
    st.markdown(
        f"""<div class="metric-grid">
        <div class="metric-card blue">
            <div class="metric-label">Total Cases</div>
            <div class="metric-value">{n_cases:,}</div>
            <div class="metric-sub">unique executions</div>
        </div>
        <div class="metric-card green">
            <div class="metric-label">Total Events</div>
            <div class="metric-value">{n_events:,}</div>
            <div class="metric-sub">log entries parsed</div>
        </div>
        <div class="metric-card yellow">
            <div class="metric-label">Activity Types</div>
            <div class="metric-value">{n_acts}</div>
            <div class="metric-sub">unique activities</div>
        </div>
        <div class="metric-card blue">
            <div class="metric-label">Avg Events/Case</div>
            <div class="metric-value">{avg_acts}</div>
            <div class="metric-sub">activities per run</div>
        </div>
        <div class="metric-card green">
            <div class="metric-label">Observation Start</div>
            <div class="metric-value" style="font-size:1.1rem;">{ts_min.strftime('%d %b %Y') if ts_min is not None else '-'}</div>
            <div class="metric-sub">{ts_min.strftime('%H:%M:%S') if ts_min is not None else '-'}</div>
        </div>
        <div class="metric-card green">
            <div class="metric-label">Observation End</div>
            <div class="metric-value" style="font-size:1.1rem;">{ts_max.strftime('%d %b %Y') if ts_max is not None else '-'}</div>
            <div class="metric-sub">{ts_max.strftime('%H:%M:%S') if ts_max is not None else '-'}</div>
        </div>
    </div>""",
        unsafe_allow_html=True,
    )

    # Preview tabs
    tab_prev1, tab_prev2, tab_prev3 = st.tabs(
        ["  Event Log Table", "  Activity Distribution", " "]
    )

    with tab_prev1:
        st.dataframe(df.head(200), use_container_width=True, height=300)
        st.caption(f"Showing first 200 of {n_events:,} events")

    with tab_prev2:
        act_counts = df["concept:name"].value_counts().reset_index()
        act_counts.columns = ["Activity", "Count"]
        fig_act = make_plotly_bar(
            act_counts,
            "Count",
            "Activity",
            "Activity Frequency Distribution",
            h=max(300, min(600, len(act_counts) * 28)),
        )
        st.plotly_chart(fig_act, use_container_width=True)

    with tab_prev3:
        ts_daily = df.groupby(df["time:timestamp"].dt.date).size().reset_index()
        ts_daily.columns = ["Date", "Event Count"]
        fig_ts = px.area(
            ts_daily,
            x="Date",
            y="Event Count",
            title="Daily Event Volume",
            color_discrete_sequence=["#00d4ff"],
        )
        fig_ts.update_layout(
            paper_bgcolor="#151b24",
            plot_bgcolor="#151b24",
            font=dict(family="DM Sans", color="#8fa3bc"),
            title_font=dict(size=14, color="#e2eaf4"),
            xaxis=dict(gridcolor="#1e2a38"),
            yaxis=dict(gridcolor="#1e2a38"),
            height=280,
            margin=dict(t=40, b=20, l=20, r=20),
        )
        fig_ts.update_traces(fillcolor="rgba(0,144,255,0.15)", line_color="#00d4ff")
        st.plotly_chart(fig_ts, use_container_width=True)

    # Compute duration dari df LENGKAP dulu (sama seperti notebook)
    df_dur = compute_duration(df)
    st.session_state.df_dur = df_dur

    # Pilih activity yang mau dibuang dari bottleneck
    all_activities = sorted(df["concept:name"].unique().tolist())

    # Default: activity start/end dari mapping user
    start_acts = [
        m["activity"]
        for m in st.session_state.mapping
        if m["activity"] in all_activities
        and any(k in m["activity"].lower() for k in ["start", "begin"])
    ]
    end_acts = [
        m["activity"]
        for m in st.session_state.mapping
        if m["activity"] in all_activities
        and any(k in m["activity"].lower() for k in ["end", "finish"])
    ]
    default_exclude = list(set(start_acts + end_acts))

    st.markdown(
        """<div class="pm-card" style="padding:1rem 1.4rem;margin-bottom:0.5rem;">
        <div style="font-size:0.72rem;color:var(--text3);font-family:var(--mono);letter-spacing:0.08em;margin-bottom:0.5rem;">NOISE ACTIVITY FILTER</div>
        <div style="font-size:0.82rem;color:var(--text2);">
        Activity yang dipilih akan <b>dihapus dari seluruh analisis</b> — bottleneck, transition delay, <b>dan Heuristic Net</b>. Gunakan untuk activity teknis yang tidak relevan secara bisnis (misal: Check Batch Mode).
        </div></div>""",
        unsafe_allow_html=True,
    )
    noise_acts = st.multiselect(
        "Pilih activity noise yang ingin dihapus dari semua analisis",
        options=all_activities,
        default=[a for a in default_exclude if a in all_activities],
        help="Activity ini difilter dari event log sebelum analisis — termasuk dari Heuristic Net.",
    )
    st.session_state["noise_acts"] = noise_acts

    # Terapkan filter noise ke df_clean — dipakai oleh SEMUA analisis termasuk discovery
    if noise_acts:
        df_filtered = df[~df["concept:name"].isin(noise_acts)].copy()
    else:
        df_filtered = df.copy()
    st.session_state.df_clean = df_filtered

    # Run Analysis button
    st.markdown("<br>", unsafe_allow_html=True)
    col_run1, col_run2, _ = st.columns([1, 2, 3])
    with col_run2:
        if st.button("▶  RUN FULL ANALYSIS", use_container_width=True):
            with st.spinner("Running analysis..."):
                # ── Bottleneck & Transition Delay ────────────────────────
                # Keduanya menggunakan df RAW (sebelum noise filter),
                # sama persis dengan notebook yang pakai df_perf.
                # df_perf di notebook = df_clean (include semua activity,
                # termasuk TECHNICAL_ACTIVITIES).
                #
                # Noise acts hanya dibuang dari RANKING AKHIR,
                # bukan dari data source — supaya temporal tidak lompat.
                # Ini persis perilaku notebook:
                #   df_waktu = df_perf.copy()  ← include semua
                #   exclude_acts = {Start,End} ∪ TECHNICAL  ← buang di ranking
                #
                # df_filtered tetap dipakai untuk Heuristic Net saja.

                # df untuk bottleneck & transition = df RAW
                df_perf = df.copy()
                df_dur_raw = compute_duration(df_perf)
                st.session_state.df_dur = df_dur_raw

                # Bottleneck: noise_acts dibuang di dalam fungsi (dari ranking)
                st.session_state.bottleneck_df = compute_bottleneck_table(
                    df_dur_raw, noise_acts=noise_acts
                )
                # Transition delay: noise_acts dibuang dari source setelah shift
                st.session_state.transition_df = compute_transition_delay(
                    df_perf, noise_acts=noise_acts
                )
                st.session_state.step = 3
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# STEP 3: FULL ANALYSIS
# ═══════════════════════════════════════════════════════════════

if st.session_state.step >= 3:
    df = st.session_state.df_clean   # sudah difilter noise
    df_dur = st.session_state.df_dur  # sudah dari df_clean
    bn_df = st.session_state.bottleneck_df
    tr_df = st.session_state.transition_df

    st.markdown(
        """<div class="section-header">
        <span class="section-title">Analysis Results</span>
    </div>""",
        unsafe_allow_html=True,
    )

    main_tab1, main_tab2, main_tab3 = st.tabs(
        [
            "Process Discovery",
            "Conformance Check",
            "Bottleneck Analysis",
        ]
    )

    # ─────────────────────────────────────────────────────────
    # TAB 1: PROCESS DISCOVERY
    # ─────────────────────────────────────────────────────────
    with main_tab1:
        st.markdown("### Process Discovery")
        st.markdown(
            '<div style="font-size:0.85rem;color:var(--text2);">Model proses diekstrak dari event log menggunakan algoritma Heuristic Miner. Activity noise yang dipilih di step sebelumnya sudah dikeluarkan dari model ini.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # Tampilkan info noise yang sudah difilter
        noise_applied = st.session_state.get("noise_acts", [])
        if noise_applied:
            st.info(f" Activity yang difilter dari analisis ini: **{', '.join(noise_applied)}**")

        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            # Variants
            st.markdown("#### Process Variants")
            var_df = get_variants(df)
            top_vars = var_df.head(10).copy()
            top_vars["Variant Path"] = top_vars["Variant Path"].str[:80] + "…"
            st.dataframe(top_vars, use_container_width=True, height=300)

        with col_d2:
            # Case duration distribution
            st.markdown("#### Case Duration Distribution")
            case_dur = (
                df.groupby("case:concept:name")
                .agg(start=("time:timestamp", "min"), end=("time:timestamp", "max"))
                .reset_index()
            )
            case_dur["duration_sec"] = (
                case_dur["end"] - case_dur["start"]
            ).dt.total_seconds()
            case_dur = case_dur[case_dur["duration_sec"] > 0]

            fig_dur = px.histogram(
                case_dur,
                x="duration_sec",
                nbins=40,
                title="Case Duration Distribution (seconds)",
                color_discrete_sequence=["#C4872F"],
            )
            fig_dur.update_layout(
                paper_bgcolor="#F5F1EB",
                plot_bgcolor="#F5F1EB",
                font=dict(family="DM Sans", color="#5B4636"),
                title_font=dict(size=13, color="#5B4636"),
                xaxis=dict(gridcolor="#D6C2A8", title="Duration (s)"),
                yaxis=dict(gridcolor="#D6C2A8", title="Count"),
                height=300,
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig_dur, use_container_width=True)

        # Heuristic Net — pakai df (filtered) bukan df_raw
        st.markdown("#### Heuristic Net (Process Model)")
        st.markdown(
            '<div style="font-size:0.8rem;color:var(--text2);margin-bottom:0.8rem;">Model di bawah hanya menampilkan activity yang <b>tidak</b> masuk daftar noise filter di atas.</div>',
            unsafe_allow_html=True,
        )
        col_viz1, col_viz2 = st.columns([3, 1])
        with col_viz2:
            st.markdown(
                f"""<div class="pm-card">
                <div class="metric-label">PARAMS</div>
                <div style="font-size:0.8rem;color:var(--text2);line-height:1.8;">
                Dep threshold: <b style="color:var(--accent);">{st.session_state.dep_thresh}</b><br>
                AND threshold: <b style="color:var(--accent);">{st.session_state.and_thresh}</b><br>
                Activities: <b style="color:var(--accent);">{df['concept:name'].nunique()}</b>
                </div>
            </div>""",
                unsafe_allow_html=True,
            )
            run_viz = st.button("⬡  Generate Heuristic Net", use_container_width=True)

        with col_viz1:
            if run_viz or st.session_state.discovery_img:
                if run_viz:
                    # Gunakan df yang sudah difilter noise
                    df_viz = df.copy()
                    with st.spinner("Running Heuristic Miner..."):
                        try:
                            img = run_discovery_viz(df_viz)
                            st.session_state.discovery_img = img
                        except Exception as e:
                            st.error(f"Discovery error: {e}")
                            st.info(
                                " Make sure graphviz is installed: apt-get install graphviz"
                            )

                if st.session_state.discovery_img:
                    st.image(st.session_state.discovery_img, use_container_width=True)
            else:
                st.markdown(
                    """<div class="pm-card" style="text-align:center;padding:3rem;">
                    <div style="font-size:3rem;margin-bottom:1rem;">⬡</div>
                    <div style="color:var(--text2);font-size:0.9rem;">Klik "Generate Heuristic Net" untuk memvisualisasikan model proses</div>
                </div>""",
                    unsafe_allow_html=True,
                )

    # ─────────────────────────────────────────────────────────
    # TAB 2: CONFORMANCE CHECKING
    # ─────────────────────────────────────────────────────────
    with main_tab2:
        st.markdown("### Conformance Checking")
        st.markdown(
            '<div style="font-size:0.85rem;color:#8fa3bc;">Compare actual process (event log) against reference model (BPMN). Upload your BPMN file to run this analysis.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        bpmn_file = st.file_uploader(
            "Upload BPMN Reference Model (.bpmn)", type=["bpmn", "xml"], key="bpmn_up"
        )

        if bpmn_file:
            bpmn_bytes = bpmn_file.read()
            col_conf1, _ = st.columns([1, 2])
            with col_conf1:
                if st.button("▶  Run Conformance Checking", use_container_width=True):
                    with st.spinner(
                        "Running Token-Based Replay & Alignment Analysis..."
                    ):
                        try:
                            fitness, precision, deviations = run_conformance(
                                df, bpmn_bytes
                            )
                            st.session_state.fitness = fitness
                            st.session_state.precision = precision
                            st.session_state.deviations = deviations
                            st.rerun()
                        except Exception as e:
                            st.error(f"Conformance error: {e}")
                            st.code(traceback.format_exc())

        if st.session_state.fitness is not None:
            fitness = st.session_state.fitness
            precision = st.session_state.precision
            deviations = st.session_state.deviations

            fit_val = fitness.get("average_trace_fitness", 0)
            prec_val = precision if isinstance(precision, float) else 0.0

            # FIX: Ambil perc_fit_traces dengan fallback, lalu normalize ke 0–1
            fit_pct_raw = (
                fitness.get("perc_fit_traces")
                or fitness.get("percentage_of_fitting_traces")
                or fitness.get("percFitTraces")
                or 0
            )
            fit_pct_normalized = fit_pct_raw / 100 if fit_pct_raw > 1 else fit_pct_raw

            # Gauges
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                st.plotly_chart(
                    fitness_gauge(fit_val, "Average Trace Fitness"),
                    use_container_width=True,
                )
            with col_g2:
                st.plotly_chart(
                    fitness_gauge(prec_val, "Precision"), use_container_width=True
                )
            with col_g3:
                st.plotly_chart(
                    fitness_gauge(fit_pct_normalized, "% Fit Traces"),
                    use_container_width=True,
                )

            # Metrics detail
            with st.container():
                if deviations:
                    st.markdown("#### Top Deviations")
                    dev_df = pd.DataFrame(
                        deviations[:15], columns=["Deviation", "Frequency"]
                    )
                    dev_df["Deviation"] = dev_df["Deviation"].str[:60]
                    st.dataframe(dev_df, use_container_width=True, height=300)

                    total_log_moves = sum(
                        v for k, v in deviations if ">>" in k.split("|")[0]
                    )
                    total_model_moves = sum(
                        v for k, v in deviations if ">>" in k.split("|")[1] if "|" in k
                    )
                    st.markdown(
                        f"""<div class="pm-card">
                        <div style="display:flex;gap:2rem;">
                            <div><div class="metric-label">LOG MOVES</div><div class="metric-value" style="font-size:1.4rem;color:#ff4757;">{total_log_moves}</div></div>
                            <div><div class="metric-label">MODEL MOVES</div><div class="metric-value" style="font-size:1.4rem;color:#ffb800;">{total_model_moves}</div></div>
                        </div>
                    </div>""",
                        unsafe_allow_html=True,
                    )
        else:
            st.info(
                "Upload a BPMN file and click 'Run Conformance Checking' to see results here."
            )

    # ─────────────────────────────────────────────────────────
    # TAB 3: BOTTLENECK ANALYSIS
    # ─────────────────────────────────────────────────────────
    with main_tab3:
        st.markdown("### Bottleneck Analysis")
        st.markdown(
            '<div style="font-size:0.85rem;color:#8fa3bc;">Multi-dimensional performance analysis based on inter-event time (duration_ms). Each metric reveals a different aspect of system performance.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        if bn_df is not None and not bn_df.empty:
            sub1, sub2, sub3, sub4 = st.tabs(
                [
                    " Total Time Ranking",
                    " Frequency Ranking",
                    " Mean Duration Ranking",
                    " Transition Delays",
                ]
            )

            with sub1:
                st.markdown(
                    "**Activities ranked by cumulative total time — highest contributors to system load**"
                )
                col_b1, col_b2 = st.columns([1, 1])
                with col_b1:
                    display_cols = [
                        "concept:name",
                        "frekuensi",
                        "total_waktu",
                        "rata_rata",
                        "median",
                        "p95",
                        "maks",
                        "pct_total",
                        "variasi",
                    ]
                    st.dataframe(
                        bn_df[display_cols]
                        .head(15)
                        .rename(
                            columns={
                                "concept:name": "Activity",
                                "frekuensi": "Freq",
                                "total_waktu": "Total (ms)",
                                "rata_rata": "Mean (ms)",
                                "median": "Median (ms)",
                                "p95": "P95 (ms)",
                                "maks": "Max (ms)",
                                "pct_total": "% Total",
                                "variasi": "Volatility",
                            }
                        ),
                        use_container_width=True,
                        height=400,
                    )
                with col_b2:
                    fig_bn = make_plotly_bar(
                        bn_df.head(10),
                        "total_waktu",
                        "concept:name",
                        "Top Bottleneck — Total Time (ms)",
                        h=400,
                    )
                    st.plotly_chart(fig_bn, use_container_width=True)

            with sub2:
                top_freq = bn_df.sort_values("frekuensi", ascending=False)
                col_f1, col_f2 = st.columns([1, 1])
                with col_f1:
                    st.dataframe(
                        top_freq[
                            ["concept:name", "frekuensi", "rata_rata", "pct_total"]
                        ]
                        .head(10)
                        .rename(
                            columns={
                                "concept:name": "Activity",
                                "frekuensi": "Frequency",
                                "rata_rata": "Mean (ms)",
                                "pct_total": "% Total Time",
                            }
                        ),
                        use_container_width=True,
                        height=350,
                    )
                with col_f2:
                    fig_fr = make_plotly_bar(
                        top_freq.head(10),
                        "frekuensi",
                        "concept:name",
                        "Top Activities by Execution Frequency",
                        h=350,
                    )
                    st.plotly_chart(fig_fr, use_container_width=True)

            with sub3:
                top_dur = bn_df.sort_values("rata_rata", ascending=False)
                col_d1, col_d2 = st.columns([1, 1])
                with col_d1:
                    st.dataframe(
                        top_dur[
                            ["concept:name", "rata_rata", "median", "p95", "variasi"]
                        ]
                        .head(10)
                        .rename(
                            columns={
                                "concept:name": "Activity",
                                "rata_rata": "Mean (ms)",
                                "median": "Median (ms)",
                                "p95": "P95 (ms)",
                                "variasi": "Volatility",
                            }
                        ),
                        use_container_width=True,
                        height=350,
                    )
                with col_d2:
                    fig_dr = make_plotly_bar(
                        top_dur.head(10),
                        "rata_rata",
                        "concept:name",
                        "Top Activities by Mean Duration (ms)",
                        h=350,
                    )
                    st.plotly_chart(fig_dr, use_container_width=True)

            with sub4:
                if tr_df is not None and not tr_df.empty:
                    col_t1, col_t2 = st.columns([1, 1])
                    with col_t1:
                        st.dataframe(
                            tr_df[
                                [
                                    "transition",
                                    "frekuensi",
                                    "rata_rata",
                                    "median",
                                    "p95",
                                ]
                            ]
                            .head(15)
                            .rename(
                                columns={
                                    "transition": "Transition (A → B)",
                                    "frekuensi": "Freq",
                                    "rata_rata": "Mean Delay (ms)",
                                    "median": "Median (ms)",
                                    "p95": "P95 (ms)",
                                }
                            ),
                            use_container_width=True,
                            height=400,
                        )
                    with col_t2:
                        fig_tr = make_plotly_bar(
                            tr_df.head(10),
                            "rata_rata",
                            "transition",
                            "Top Transition Delays — Mean (ms)",
                            h=400,
                        )
                        st.plotly_chart(fig_tr, use_container_width=True)
                else:
                    st.info("No transition data available.")

            # Summary synthesis card
            if not bn_df.empty:
                top1 = bn_df.iloc[0]["concept:name"] if len(bn_df) > 0 else "-"
                top2 = bn_df.iloc[1]["concept:name"] if len(bn_df) > 1 else "-"
                top3 = bn_df.iloc[2]["concept:name"] if len(bn_df) > 2 else "-"
                st.markdown(
                    f"""<div class="pm-card" style="border-color:#2a3a50;margin-top:1rem;">
                    <div style="font-family:Space Mono;font-size:0.7rem;color:#4a6278;letter-spacing:0.1em;margin-bottom:0.8rem;">BOTTLENECK SYNTHESIS</div>
                    <div style="font-size:0.9rem;color:#5B4636;line-height:1.7;">
                    Based on total time analysis, the top 3 bottleneck activities are:<br>
                    <span class="pill pill-red">#{1} {top1}</span>&nbsp;
                    <span class="pill pill-yellow">#{2} {top2}</span>&nbsp;
                    <span class="pill pill-blue">#{3} {top3}</span>
                    </div>
                </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.warning(
                "No bottleneck data available. Ensure event log has valid timestamps."
            )