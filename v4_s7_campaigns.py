# v4_s7_campaigns.py
# Storyline 7: Campaign Effectiveness
# =============================================================================
# Response rates, spend lift, segmentation performance, balance tier response

from __future__ import annotations

import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from v4_themes import (
    COLORS, CATEGORY_PALETTE, GENERATION_COLORS,
    apply_theme, format_currency, horizontal_bar,
    donut_chart, insight_title,
)

_MAIL_RE = re.compile(r"^[A-Z][a-z]{2}\d{2} Mail$")
_RESP_RE = re.compile(r"^[A-Z][a-z]{2}\d{2} Resp$")
_SEG_RE = re.compile(r"^[A-Z][a-z]{2}\d{2} Segmentation$")
_MIN_GROUP = 5


def _rate(num: int, den: int) -> float:
    """Percentage (0-100) with zero-division guard."""
    return round(num / den * 100, 1) if den else 0.0


def _has_campaign_data(odd: pd.DataFrame | None) -> bool:
    if odd is None or odd.empty:
        return False
    return "# of Offers" in odd.columns or any(_MAIL_RE.match(c) for c in odd.columns)


def _detect_cols(odd: pd.DataFrame):
    mail = sorted(c for c in odd.columns if _MAIL_RE.match(c))
    resp = sorted(c for c in odd.columns if _RESP_RE.match(c))
    seg = sorted(c for c in odd.columns if _SEG_RE.match(c))
    return mail, resp, seg


# -- Analysis 1: Campaign Overview -------------------------------------------

def _campaign_overview(odd):
    mailed = odd[odd["# of Offers"] > 0] if "# of Offers" in odd.columns else odd
    resp_mask = odd["# of Responses"] > 0 if "# of Responses" in odd.columns else pd.Series(False, index=odd.index)
    mc, rc = len(mailed), int(resp_mask.sum())
    non_rc = mc - rc
    rate = _rate(rc, mc)

    df = pd.DataFrame([
        {"Metric": "Total Accounts", "Value": len(odd)},
        {"Metric": "Accounts Mailed", "Value": mc},
        {"Metric": "Responders", "Value": rc},
        {"Metric": "Non-Responders", "Value": non_rc},
        {"Metric": "Response Rate (%)", "Value": rate},
    ])
    fig = donut_chart(
        ["Responders", "Non-Responders"], [rc, max(non_rc, 0)],
        "Campaign Response Breakdown",
        colors=[COLORS["positive"], COLORS["neutral"]],
    )
    fig.update_layout(title=insight_title(
        f"{rate:.1f}% overall campaign response rate",
        f"{rc:,} responders out of {mc:,} mailed",
    ))
    narr = (
        f"Of <b>{mc:,}</b> accounts that received campaign offers, "
        f"<b>{rc:,}</b> responded (<b>{rate:.1f}%</b> response rate). "
        f"Non-responders total <b>{max(non_rc, 0):,}</b>."
    )
    return df, fig, narr


# -- Analysis 2: Response Rate by Generation ----------------------------------

def _response_by_generation(odd):
    need = {"generation", "# of Offers", "# of Responses"}
    if not need.issubset(odd.columns):
        return pd.DataFrame(), go.Figure(), ""

    offered = odd[odd["# of Offers"] > 0].copy()
    if offered.empty:
        return pd.DataFrame(), go.Figure(), ""

    gs = offered.groupby("generation").agg(
        mailed=("# of Offers", "count"),
        responders=("# of Responses", lambda s: (s > 0).sum()),
    ).reset_index()
    gs = gs[gs["mailed"] >= _MIN_GROUP]
    gs["resp_rate"] = gs.apply(lambda r: _rate(r["responders"], r["mailed"]), axis=1)
    gs = gs.sort_values("resp_rate", ascending=False)
    gs.columns = ["Generation", "Mailed", "Responders", "Response Rate (%)"]

    colors = [GENERATION_COLORS.get(g, COLORS["neutral"]) for g in gs["Generation"]]
    fig = go.Figure(go.Bar(
        x=gs["Generation"], y=gs["Response Rate (%)"],
        marker_color=colors,
        text=[f"{v:.1f}%" for v in gs["Response Rate (%)"]],
        textposition="outside",
    ))
    fig.update_layout(
        title=insight_title("Campaign response rate by generation"),
        yaxis=dict(title="Response Rate (%)", ticksuffix="%"),
        xaxis=dict(title=None), showlegend=False,
    )
    apply_theme(fig)

    top = gs.iloc[0]
    narr = (
        f"<b>{top['Generation']}</b> leads at <b>{top['Response Rate (%)']:.1f}%</b> "
        f"({int(top['Responders']):,} of {int(top['Mailed']):,} mailed)."
    )
    return gs, fig, narr


# -- Analysis 3: Spend Lift ---------------------------------------------------

def _spend_lift(odd):
    if "Total Spend" not in odd.columns or "# of Responses" not in odd.columns:
        return pd.DataFrame(), go.Figure(), ""

    odd = odd.copy()
    odd["resp_flag"] = np.where(odd["# of Responses"] > 0, "Responder", "Non-Responder")

    base = odd.groupby("resp_flag").agg(
        accounts=("resp_flag", "count"),
        avg_spend=("Total Spend", "mean"),
    ).reset_index()
    base["avg_spend"] = base["avg_spend"].round(2)
    base.columns = ["Group", "Accounts", "Avg Spend"]

    if "Response Grouping" in odd.columns:
        grp = odd.groupby("Response Grouping").agg(
            accounts=("Response Grouping", "count"),
            avg_spend=("Total Spend", "mean"),
        ).reset_index()
        grp["avg_spend"] = grp["avg_spend"].round(2)
        grp.columns = ["Group", "Accounts", "Avg Spend"]
        combined = pd.concat([base, grp], ignore_index=True)
    else:
        combined = base.copy()

    fig = go.Figure(go.Bar(
        x=combined["Group"], y=combined["Avg Spend"],
        marker_color=CATEGORY_PALETTE[:len(combined)],
        text=[format_currency(v) for v in combined["Avg Spend"]],
        textposition="outside",
    ))
    fig.update_layout(
        title=insight_title("Average spend: responders vs non-responders"),
        yaxis=dict(title="Avg Total Spend", tickprefix="$", tickformat=","),
        xaxis=dict(title=None), showlegend=False,
    )
    apply_theme(fig)

    r_row = base[base["Group"] == "Responder"]
    n_row = base[base["Group"] == "Non-Responder"]
    if not r_row.empty and not n_row.empty:
        rs, ns = r_row["Avg Spend"].iloc[0], n_row["Avg Spend"].iloc[0]
        lift = _rate(int(rs - ns), int(ns)) if ns else 0
        narr = (
            f"Responders average <b>{format_currency(rs)}</b> vs "
            f"<b>{format_currency(ns)}</b> for non-responders "
            f"(<b>{lift:.1f}%</b> lift)."
        )
    else:
        narr = "Insufficient data to compute spend lift."
    return combined, fig, narr


# -- Analysis 4: Monthly Mail & Response Tracking -----------------------------

def _monthly_tracking(odd):
    mail_cols, _, _ = _detect_cols(odd)
    if not mail_cols:
        return pd.DataFrame(), go.Figure(), ""

    rows = []
    for mc in mail_cols:
        label = mc.replace(" Mail", "")
        rc = f"{label} Resp"
        m = int((odd[mc] == 1).sum()) if mc in odd.columns else 0
        r = int((odd[rc] == 1).sum()) if rc in odd.columns else 0
        rows.append({"Month": label, "Mailed": m, "Responded": r, "Response Rate (%)": _rate(r, m)})

    tdf = pd.DataFrame(rows)
    if tdf.empty:
        return pd.DataFrame(), go.Figure(), ""

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tdf["Month"], y=tdf["Mailed"], name="Mailed",
        marker_color=COLORS["primary"], opacity=0.7, yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=tdf["Month"], y=tdf["Response Rate (%)"], name="Response Rate %",
        mode="lines+markers", line=dict(color=COLORS["accent"], width=3),
        marker=dict(size=8), yaxis="y2",
    ))
    fig.update_layout(
        title=insight_title("Monthly campaign cadence & response rate"),
        yaxis=dict(title="Accounts Mailed", tickformat=","),
        yaxis2=dict(
            title="Response Rate (%)", overlaying="y", side="right",
            ticksuffix="%", range=[0, max(tdf["Response Rate (%)"].max() * 1.3, 10)],
        ),
        legend=dict(orientation="h", y=-0.15), hovermode="x unified",
    )
    apply_theme(fig)

    narr = (
        f"Campaign data spans <b>{len(tdf)}</b> months with an average "
        f"response rate of <b>{tdf['Response Rate (%)'].mean():.1f}%</b>."
    )
    return tdf, fig, narr


# -- Analysis 5: Campaign Segmentation Performance ----------------------------

def _segmentation_performance(odd):
    _, _, seg_cols = _detect_cols(odd)
    if not seg_cols:
        return pd.DataFrame(), go.Figure(), ""

    latest = seg_cols[-1]
    label = latest.replace(" Segmentation", "")
    rc = f"{label} Resp"

    sd = odd[[latest]].copy()
    sd["responded"] = (odd[rc] == 1).astype(int) if rc in odd.columns else 0
    sd["spend"] = odd["Total Spend"] if "Total Spend" in odd.columns else 0
    sd = sd.dropna(subset=[latest])
    sd = sd[sd[latest].astype(str).str.strip() != ""]
    if sd.empty:
        return pd.DataFrame(), go.Figure(), ""

    st = sd.groupby(latest).agg(
        accounts=(latest, "count"), responders=("responded", "sum"),
        avg_spend=("spend", "mean"),
    ).reset_index()
    st = st[st["accounts"] >= _MIN_GROUP]
    st["resp_rate"] = st.apply(lambda r: _rate(int(r["responders"]), int(r["accounts"])), axis=1)
    st["avg_spend"] = st["avg_spend"].round(2)
    st = st.sort_values("resp_rate", ascending=True)
    st.columns = ["Segment", "Accounts", "Responders", "Avg Spend", "Response Rate (%)"]

    fig = horizontal_bar(
        st, x_col="Response Rate (%)", y_col="Segment",
        title=f"Response Rate by Segment ({label})",
        color=COLORS["secondary"], show_values=True, value_format="{:.1f}%", top_n=20,
    )
    fig.update_layout(title=insight_title(
        f"Segmentation performance for {label}", f"{len(st)} segments analyzed",
    ))

    narr = f"For <b>{label}</b>, <b>{len(st)}</b> segments identified. "
    if not st.empty:
        best = st.iloc[-1]
        narr += (
            f"Top segment: <b>{best['Segment']}</b> at "
            f"<b>{best['Response Rate (%)']:.1f}%</b> response rate."
        )
    return st, fig, narr


# -- Analysis 6: Response by Balance Tier -------------------------------------

def _response_by_balance_tier(odd):
    if "balance_tier" not in odd.columns or "# of Responses" not in odd.columns:
        return pd.DataFrame(), go.Figure(), ""

    offered = odd[odd["# of Offers"] > 0].copy() if "# of Offers" in odd.columns else odd.copy()
    if offered.empty:
        return pd.DataFrame(), go.Figure(), ""

    offered["resp_flag"] = np.where(offered["# of Responses"] > 0, "Responder", "Non-Responder")
    ct = pd.crosstab(offered["balance_tier"], offered["resp_flag"])
    for col in ["Responder", "Non-Responder"]:
        if col not in ct.columns:
            ct[col] = 0
    ct = ct[["Responder", "Non-Responder"]]

    ct_pct = (ct.div(ct.sum(axis=1), axis=0) * 100).round(1).reset_index()

    summary = ct.copy()
    summary["Total"] = summary.sum(axis=1)
    summary["Response Rate (%)"] = (summary["Responder"] / summary["Total"] * 100).round(1)
    summary = summary.reset_index()
    summary.columns = ["Balance Tier", "Responders", "Non-Responders", "Total", "Response Rate (%)"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ct_pct["balance_tier"], y=ct_pct["Responder"],
        name="Responder", marker_color=COLORS["positive"],
    ))
    fig.add_trace(go.Bar(
        x=ct_pct["balance_tier"], y=ct_pct["Non-Responder"],
        name="Non-Responder", marker_color=COLORS["neutral"],
    ))
    fig.update_layout(
        barmode="stack", title=insight_title("Response rate by balance tier"),
        yaxis=dict(title="% of Accounts", ticksuffix="%", range=[0, 100]),
        xaxis=dict(title=None),
    )
    apply_theme(fig)

    if not summary.empty:
        best = summary.loc[summary["Response Rate (%)"].idxmax()]
        narr = (
            f"<b>{best['Balance Tier']}</b> leads at "
            f"<b>{best['Response Rate (%)']:.1f}%</b> "
            f"({int(best['Responders']):,} responders)."
        )
    else:
        narr = ""
    return summary, fig, narr


# =============================================================================
# Main Runner
# =============================================================================

def _add(sections, sheets, heading, df, fig, narr, sheet_name, **col_spec):
    """Append a section+sheet pair only when data is present."""
    if df.empty:
        return
    sections.append({
        "heading": heading, "narrative": narr,
        "figures": [fig], "tables": [(heading, df)],
    })
    sheets.append({"name": sheet_name, "df": df, **col_spec})


def run(ctx: dict) -> dict:
    """Run Campaign Effectiveness analyses and return storyline payload."""
    odd = ctx.get("odd_df")

    if not _has_campaign_data(odd):
        return {
            "title": "S7: Campaign Effectiveness",
            "description": "No campaign data available in the ODD file.",
            "sections": [{
                "heading": "Campaign Effectiveness",
                "narrative": (
                    "No campaign data available. The ODD file does not contain "
                    "campaign-related columns (# of Offers, MmmYY Mail)."
                ),
                "figures": [], "tables": [],
            }],
            "sheets": [],
        }

    sections, sheets = [], []

    # 1 - Campaign Overview (always appended when campaign data exists)
    ov_df, ov_fig, ov_narr = _campaign_overview(odd)
    sections.append({
        "heading": "Campaign Overview", "narrative": ov_narr,
        "figures": [ov_fig], "tables": [("Campaign Overview", ov_df)],
    })
    sheets.append({
        "name": "S7 Campaign Overview", "df": ov_df,
        "currency_cols": [], "pct_cols": [], "number_cols": ["Value"],
    })

    # 2 - Response by Generation
    _add(sections, sheets, "Response Rate by Generation",
         *_response_by_generation(odd), "S7 Response by Gen",
         currency_cols=[], pct_cols=["Response Rate (%)"],
         number_cols=["Mailed", "Responders"])

    # 3 - Spend Lift
    _add(sections, sheets, "Spend Lift: Responders vs Non-Responders",
         *_spend_lift(odd), "S7 Spend Lift",
         currency_cols=["Avg Spend"], pct_cols=[], number_cols=["Accounts"])

    # 4 - Monthly Tracking
    _add(sections, sheets, "Monthly Mail & Response Tracking",
         *_monthly_tracking(odd), "S7 Monthly Tracking",
         currency_cols=[], pct_cols=["Response Rate (%)"],
         number_cols=["Mailed", "Responded"])

    # 5 - Segmentation
    _add(sections, sheets, "Campaign Segmentation Performance",
         *_segmentation_performance(odd), "S7 Segmentation",
         currency_cols=["Avg Spend"], pct_cols=["Response Rate (%)"],
         number_cols=["Accounts", "Responders"])

    # 6 - Balance Tier
    _add(sections, sheets, "Response by Balance Tier",
         *_response_by_balance_tier(odd), "S7 Balance Tier Resp",
         currency_cols=[], pct_cols=["Response Rate (%)"],
         number_cols=["Responders", "Non-Responders", "Total"])

    return {
        "title": "S7: Campaign Effectiveness",
        "description": (
            "Campaign response rates, spend lift analysis, "
            "generational and balance-tier response patterns"
        ),
        "sections": sections,
        "sheets": sheets,
    }
