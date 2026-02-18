"""V4 Transaction Analysis - Streamlit Launcher.

Run:  streamlit run v4_app.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

# Ensure bare imports resolve from this file's directory
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
    page_icon=":bar_chart:",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar form
# ---------------------------------------------------------------------------
st.sidebar.title("V4 Transaction Analysis")
st.sidebar.markdown("Paste file paths below, select storylines, and click **Run**.")

with st.sidebar.form("run_form"):
    txn_dir = st.text_input(
        "Transaction File Directory",
        help="Full path to the folder containing CSV or TXT transaction files",
    )
    file_ext = st.selectbox("File Type", ["csv", "txt"])
    odd_path = st.text_input(
        "ODD File Path",
        help="Full path to the ODD Excel file (.xlsx)",
    )
    client_id = st.text_input("Client ID", value="0000")
    client_name = st.text_input("Client Name", value="Client")

    st.markdown("---")
    st.markdown("**Storylines to Run**")
    selected: list[str] = []
    for key, label in STORYLINE_LABELS.items():
        if st.checkbox(label, value=True, key=f"cb_{key}"):
            selected.append(key)

    submitted = st.form_submit_button("Run Analysis", type="primary")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("V4 Transaction Analysis")

if not submitted:
    st.info(
        "Fill in file paths in the sidebar and click **Run Analysis** to begin. "
        "All fields are required."
    )
    st.stop()

# --- Pre-flight validation --------------------------------------------------
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

# --- Build config from base YAML + form overrides --------------------------
config_path = _HERE / "v4_config.yaml"
if config_path.exists():
    config = load_config(str(config_path))
else:
    config = {}

config["transaction_dir"] = txn_dir.strip()
config["file_extension"] = file_ext
config["odd_file"] = odd_path.strip()
config["client_id"] = client_id.strip()
config["client_name"] = client_name.strip()
config["output_dir"] = str(_HERE / "output" / f"{client_id.strip()}_{client_name.strip().replace(' ', '_')}")

# --- Run pipeline -----------------------------------------------------------
progress_bar = st.progress(0, text="Initializing...")
status_container = st.status("Running analysis...", expanded=True)


def _progress(step: int, total: int, label: str) -> None:
    pct = step / total if total > 0 else 0
    progress_bar.progress(pct, text=label)
    status_container.write(label)


try:
    with status_container:
        results, excel_path, html_path = run_pipeline(
            config, storylines=selected, progress_cb=_progress,
        )
    status_container.update(label="Analysis complete", state="complete")
except Exception:
    status_container.update(label="Analysis failed", state="error")
    st.error("An error occurred during analysis.")
    st.code(traceback.format_exc())
    st.stop()

# --- Results summary --------------------------------------------------------
total_sections = sum(len(r.get("sections", [])) for r in results.values())
total_figures = sum(
    len(s.get("figures", []))
    for r in results.values()
    for s in r.get("sections", [])
)
total_sheets = sum(len(r.get("sheets", [])) for r in results.values())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Storylines", len(results))
col2.metric("Sections", total_sections)
col3.metric("Charts", total_figures)
col4.metric("Excel Sheets", total_sheets)

# --- Per-storyline status ---------------------------------------------------
st.markdown("### Storyline Results")
for key, result in results.items():
    label = STORYLINE_LABELS.get(key, key)
    n_sec = len(result.get("sections", []))
    desc = result.get("description", "")
    if "Error:" in desc:
        st.error(f"**{label}** -- {desc}")
    else:
        st.success(f"**{label}** -- {n_sec} sections")

# --- Download buttons -------------------------------------------------------
st.markdown("### Download Reports")
dl_col1, dl_col2 = st.columns(2)

if excel_path.exists():
    with open(excel_path, "rb") as f:
        dl_col1.download_button(
            label="Download Excel Report",
            data=f.read(),
            file_name=excel_path.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if html_path.exists():
    with open(html_path, "rb") as f:
        dl_col2.download_button(
            label="Download HTML Dashboard",
            data=f.read(),
            file_name=html_path.name,
            mime="text/html",
        )

st.caption(f"Output saved to `{config['output_dir']}`")
