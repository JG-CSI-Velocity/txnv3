"""V4 Transaction Analysis - Analyst Workbench.

Run:  streamlit run v4_app.py
"""
from __future__ import annotations

import re
import sys
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import streamlit as st

from v4_data_loader import load_config
from v4_run import STORYLINE_LABELS, run_pipeline

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="V4 Transaction Analysis",
    page_icon="\u2588",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --navy:    #2E4057;
    --teal:    #048A81;
    --amber:   #F18F01;
    --green:   #2D936C;
    --red:     #C73E1D;
    --slate:   #8B95A2;
    --surface: #111827;
    --card:    #1F2937;
    --border:  #374151;
    --text:    #E5E7EB;
    --muted:   #9CA3AF;
}

/* Global */
.stApp { background: var(--surface); color: var(--text); }
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

/* Force light text on dark background for all Streamlit elements */
.stMarkdown, .stMarkdown p, .stMarkdown li,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
.stMarkdown h5, .stMarkdown h6 { color: var(--text); }
p, span, div, label, li { color: var(--text); }
.stTextInput label, .stSelectbox label, .stCheckbox label,
.stRadio label, .stMultiSelect label { color: var(--muted) !important; }
.stTextInput input, .stSelectbox select {
    color: var(--text) !important;
    background: var(--card) !important;
    border-color: var(--border) !important;
}
input, textarea { color: var(--text) !important; }
.stSelectbox > div > div { color: var(--text) !important; }
[data-baseweb="select"] { color: var(--text) !important; }
[data-baseweb="select"] * { color: var(--text) !important; }
[data-baseweb="input"] input { color: var(--text) !important; }
.stCheckbox span { color: var(--text) !important; }
.stAlert p { color: inherit; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0D1117;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stMarkdown h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--teal);
    border-bottom: 2px solid var(--teal);
    padding-bottom: 0.5rem;
}
section[data-testid="stSidebar"] label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.25rem;
}
div[data-testid="stMetric"] label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--teal);
}

/* Header bar */
.header-bar {
    background: linear-gradient(135deg, var(--navy) 0%, #1a2d42 100%);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}
.header-bar h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #fff;
    margin: 0 0 0.25rem 0;
    letter-spacing: 0.02em;
}
.header-bar .sub {
    font-size: 0.85rem;
    color: var(--slate);
}
.header-bar .client-tag {
    display: inline-block;
    background: var(--teal);
    color: #fff;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
    letter-spacing: 0.05em;
    margin-top: 0.5rem;
}

/* Section cards */
.section-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}
.section-card h4 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: var(--teal);
    margin: 0 0 0.5rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.section-card .narrative {
    font-size: 0.9rem;
    color: var(--text);
    line-height: 1.6;
}
.section-card .narrative b, .section-card .narrative strong {
    color: var(--amber);
    font-weight: 600;
}

/* Status pill */
.pill-ok {
    display: inline-block;
    background: rgba(45, 147, 108, 0.15);
    color: var(--green);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    letter-spacing: 0.03em;
}
.pill-err {
    display: inline-block;
    background: rgba(199, 62, 29, 0.15);
    color: var(--red);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
}

/* Download bar */
.dl-bar {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.5rem;
    margin-top: 1.5rem;
}
.dl-bar h4 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin: 0 0 0.75rem 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--card);
    border-radius: 6px 6px 0 0;
    border: 1px solid var(--border);
    border-bottom: none;
    padding: 0.25rem 0.5rem 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--muted);
    padding: 0.6rem 0.9rem;
    border-radius: 4px 4px 0 0;
}
.stTabs [aria-selected="true"] {
    background: var(--surface);
    color: var(--teal);
    border: 1px solid var(--border);
    border-bottom: 2px solid var(--teal);
}
.stTabs [data-baseweb="tab-panel"] {
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 6px 6px;
    padding: 1rem;
    background: var(--surface);
}

/* Expander styling */
.streamlit-expanderHeader {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: var(--muted);
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--muted);
}
.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.3;
}
.empty-state h3 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem;
    color: var(--slate);
    margin-bottom: 0.5rem;
}
.empty-state p {
    font-size: 0.85rem;
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Form submit button override */
.stFormSubmitButton > button {
    background: var(--teal) !important;
    color: #fff !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    border: none !important;
    width: 100%;
}
.stFormSubmitButton > button:hover {
    background: #069e94 !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)


def _strip_html(text: str) -> str:
    """Remove HTML tags for plain-text contexts."""
    return re.sub(r"<[^>]+>", "", text)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("V4 WORKBENCH")

    with st.form("run_form"):
        st.markdown("##### DATA SOURCES")
        txn_dir = st.text_input(
            "Transaction directory",
            value=st.session_state.get("last_txn_dir", ""),
            help="Folder with CSV/TXT files (year subfolders OK)",
            placeholder="/path/to/1453 - Connex",
        )
        c1, c2 = st.columns([2, 1])
        with c1:
            odd_path = st.text_input(
                "ODD file (.xlsx)",
                value=st.session_state.get("last_odd_path", ""),
                placeholder="/path/to/1453-ODD.xlsx",
            )
        with c2:
            file_ext = st.selectbox("Type", ["csv", "txt"], label_visibility="visible")

        st.markdown("##### CLIENT")
        id_col, name_col = st.columns(2)
        with id_col:
            client_id = st.text_input("ID", value="0000")
        with name_col:
            client_name = st.text_input("Name", value="Client")

        st.markdown("##### STORYLINES")
        all_on = st.checkbox("Select all", value=True, key="select_all")
        selected: list[str] = []
        for key, label in STORYLINE_LABELS.items():
            short = label.split(": ", 1)[-1] if ": " in label else label
            tag = label.split(":")[0] if ":" in label else ""
            if st.checkbox(f"`{tag}` {short}", value=all_on, key=f"cb_{key}"):
                selected.append(key)

        st.markdown("---")
        submitted = st.form_submit_button("RUN ANALYSIS")

# ---------------------------------------------------------------------------
# Main area - Header
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="header-bar">'
    '<h1>V4 Transaction Analysis</h1>'
    '<span class="sub">Debit card portfolio analytics workbench</span>'
    "</div>",
    unsafe_allow_html=True,
)

if not submitted:
    st.markdown(
        '<div class="empty-state">'
        '<div class="icon">///</div>'
        "<h3>Ready to analyze</h3>"
        "<p>Configure data sources and client info in the sidebar, "
        "select your storylines, and hit RUN ANALYSIS.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
errors: list[str] = []
if not txn_dir.strip():
    errors.append("Transaction directory is required.")
elif not Path(txn_dir.strip()).exists():
    errors.append(f"Transaction directory not found: `{txn_dir.strip()}`")
elif not list(Path(txn_dir.strip()).rglob(f"*.{file_ext}")):
    errors.append(f"No `.{file_ext}` files found in `{txn_dir.strip()}`")

if not odd_path.strip():
    errors.append("ODD file path is required.")
elif not Path(odd_path.strip()).exists():
    errors.append(f"ODD file not found: `{odd_path.strip()}`")

if not selected:
    errors.append("Select at least one storyline.")

if errors:
    for e in errors:
        st.error(e)
    st.stop()

# Remember paths for next run
st.session_state["last_txn_dir"] = txn_dir.strip()
st.session_state["last_odd_path"] = odd_path.strip()

# ---------------------------------------------------------------------------
# Build config
# ---------------------------------------------------------------------------
config_path = _HERE / "v4_config.yaml"
config = load_config(str(config_path)) if config_path.exists() else {}

config["transaction_dir"] = txn_dir.strip()
config["file_extension"] = file_ext
config["odd_file"] = odd_path.strip()
config["client_id"] = client_id.strip()
config["client_name"] = client_name.strip()
config["output_dir"] = str(
    _HERE / "output" / f"{client_id.strip()}_{client_name.strip().replace(' ', '_')}"
)

# ---------------------------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------------------------
progress_bar = st.progress(0, text="Initializing...")
status_box = st.status("Running analysis...", expanded=True)


def _progress(step: int, total: int, label: str) -> None:
    pct = step / total if total > 0 else 0
    progress_bar.progress(pct, text=label)
    status_box.write(f"`{label}`")


t0 = time.time()
try:
    with status_box:
        results, excel_path, html_path = run_pipeline(
            config, storylines=selected, progress_cb=_progress,
        )
    elapsed = time.time() - t0
    status_box.update(label=f"Complete in {elapsed:.1f}s", state="complete")
except Exception:
    status_box.update(label="Analysis failed", state="error")
    st.error("Pipeline error -- see traceback below.")
    st.code(traceback.format_exc())
    st.stop()

# ---------------------------------------------------------------------------
# Client banner
# ---------------------------------------------------------------------------
st.markdown(
    f'<div class="header-bar" style="padding:1rem 1.5rem;">'
    f'<span class="client-tag">{client_id.strip()} - {client_name.strip()}</span>'
    f'<span class="sub" style="margin-left:1rem;">{elapsed:.1f}s</span>'
    f"</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Metrics row
# ---------------------------------------------------------------------------
total_sections = sum(len(r.get("sections", [])) for r in results.values())
total_figures = sum(
    len(s.get("figures", []))
    for r in results.values()
    for s in r.get("sections", [])
)
total_sheets = sum(len(r.get("sheets", [])) for r in results.values())

m1, m2, m3, m4 = st.columns(4)
m1.metric("Storylines", len(results))
m2.metric("Sections", total_sections)
m3.metric("Charts", total_figures)
m4.metric("Sheets", total_sheets)

# ---------------------------------------------------------------------------
# Tabbed results viewer
# ---------------------------------------------------------------------------
if results:
    tab_labels = []
    tab_keys = []
    for key in results:
        label = STORYLINE_LABELS.get(key, key)
        short = label.split(":")[0] if ":" in label else label
        tab_labels.append(short)
        tab_keys.append(key)

    tabs = st.tabs(tab_labels)

    for tab, key in zip(tabs, tab_keys):
        result = results[key]
        label = STORYLINE_LABELS.get(key, key)
        sections = result.get("sections", [])
        desc = result.get("description", "")

        with tab:
            # Status pill
            if "Error:" in desc:
                st.markdown(f'<span class="pill-err">ERROR</span> {desc}', unsafe_allow_html=True)
                continue

            st.markdown(
                f'<span class="pill-ok">OK</span> '
                f'<span style="color:var(--muted);font-size:0.8rem;">'
                f'{len(sections)} sections</span>',
                unsafe_allow_html=True,
            )

            for section in sections:
                heading = section.get("heading", "")
                narrative = section.get("narrative", "")
                figures = section.get("figures", [])
                tables = section.get("tables", [])

                st.markdown(
                    f'<div class="section-card">'
                    f"<h4>{heading}</h4>"
                    f'<div class="narrative">{narrative}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

                for fig in figures:
                    st.plotly_chart(fig, use_container_width=True, key=f"{key}_{heading}_{id(fig)}")

                for tbl_title, tbl_df in tables:
                    with st.expander(f"Table: {tbl_title}"):
                        st.dataframe(tbl_df, use_container_width=True)

# ---------------------------------------------------------------------------
# Download bar
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="dl-bar"><h4>Export Deliverables</h4></div>',
    unsafe_allow_html=True,
)

dl1, dl2, dl3 = st.columns(3)

if excel_path.exists():
    with open(excel_path, "rb") as f:
        dl1.download_button(
            "Excel Workbook",
            data=f.read(),
            file_name=excel_path.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

if html_path.exists():
    with open(html_path, "rb") as f:
        dl2.download_button(
            "HTML Dashboard",
            data=f.read(),
            file_name=html_path.name,
            mime="text/html",
            use_container_width=True,
        )

dl3.caption(f"Saved to `{config['output_dir']}`")
