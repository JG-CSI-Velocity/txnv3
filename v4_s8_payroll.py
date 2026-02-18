# v4_s8_payroll.py  --  Storyline 8: Payroll & Circular Economy
# Payroll detection, employer analysis, generational demographics, trends,
# and debit-spend recapture rate.
from __future__ import annotations

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from v4_themes import (
    COLORS, GENERATION_COLORS, apply_theme, format_currency, format_pct,
    horizontal_bar, line_trend, donut_chart, grouped_bar,
    insight_title, add_source_footer,
)

_KNOWN_PROCESSORS = {
    "ADP", "PAYCHEX", "INTUIT", "BAMBOOHR", "GUSTO", "PAYLOCITY",
    "PAYCOM", "CERIDIAN", "WORKDAY", "RIPPLING", "NAMELY",
}
_GEN_ORDER = ["Gen Z", "Millennial", "Gen X", "Boomer", "Silent"]


def _detect_payroll(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Identify payroll transactions via merchant name pattern matching."""
    pay_cfg = config.get("payroll", {})
    processors: list[str] = pay_cfg.get("processors", ["PAYROLL"])
    skip_terms = [t.upper() for t in pay_cfg.get("skip_terms", [])]
    min_spend: float = pay_cfg.get("min_spend", 10_000)
    max_match: int = pay_cfg.get("max_match_count", 1_000)

    merch_upper = df["merchant_consolidated"].str.upper()
    matched = pd.Series(False, index=df.index)
    labels = pd.Series("", index=df.index)

    for pattern in processors:
        pat = pattern.upper()
        hits = merch_upper.str.contains(pat, na=False, regex=False)
        is_known = any(kp in pat for kp in _KNOWN_PROCESSORS)
        if not is_known and skip_terms:
            residual = merch_upper.str.replace(pat, "", regex=False).str.strip()
            skip = pd.Series(False, index=df.index)
            for term in skip_terms:
                skip = skip | residual.str.contains(term, na=False, regex=False)
            hits = hits & ~skip
        matched = matched | hits
        labels = labels.where(~hits, merch_upper)

    payroll_df = df.loc[matched].copy()
    payroll_df["payroll_employer"] = labels.loc[matched]

    if min_spend > 0:
        stats = df.groupby("merchant_consolidated").agg(
            total=("amount", "sum"), accts=("primary_account_num", "nunique"),
        )
        cands = stats[(stats["total"] >= min_spend) & (stats["accts"] <= max_match)].index
        extra_mask = df["merchant_consolidated"].isin(cands) & ~df.index.isin(payroll_df.index)
        if extra_mask.any():
            extra = df.loc[extra_mask].copy()
            extra["payroll_employer"] = extra["merchant_consolidated"].str.upper()
            payroll_df = pd.concat([payroll_df, extra], ignore_index=True)
    return payroll_df


def run(ctx: dict) -> dict:
    """Run Payroll & Circular Economy analyses."""
    df = ctx["combined_df"]
    config = ctx.get("config", {})
    sections: list[dict] = []
    sheets: list[dict] = []
    payroll_df = _detect_payroll(df, config)
    empty_result = {
        "title": "S8: Payroll & Circular Economy",
        "description": "Payroll detection, employer analysis, workforce demographics, recapture rate",
        "sections": sections, "sheets": sheets,
    }
    if payroll_df.empty:
        sections.append({"heading": "Payroll Detection",
                         "narrative": "No payroll transactions were detected.",
                         "figures": [], "tables": []})
        return empty_result

    s, sh = _payroll_summary(df, payroll_df)
    sections.append(s); sheets.append(sh)
    s, sh = _top_employers(payroll_df)
    sections.append(s); sheets.append(sh)
    if "generation" in payroll_df.columns:
        s, sh = _payroll_by_generation(payroll_df)
        sections.append(s); sheets.append(sh)
    if "year_month" in payroll_df.columns:
        s, sh = _monthly_trends(payroll_df)
        sections.append(s); sheets.append(sh)
    circ = _circular_economy(df, payroll_df)
    if circ[0] is not None:
        sections.append(circ[0]); sheets.append(circ[1])
    return empty_result  # sections/sheets already mutated into it


def _payroll_summary(df: pd.DataFrame, pay: pd.DataFrame):
    total_pay = pay["amount"].sum()
    total_all = df["amount"].sum()
    n_employers = pay["payroll_employer"].nunique()
    n_accounts = pay["primary_account_num"].nunique()
    pct = (total_pay / total_all * 100) if total_all > 0 else 0

    fig = donut_chart(
        labels=["Payroll Spend", "Non-Payroll Spend"],
        values=[total_pay, max(total_all - total_pay, 0)],
        title="Payroll vs Non-Payroll Spend",
        colors=[COLORS["primary"], COLORS["neutral"]],
    )
    apply_theme(fig)

    narrative = (
        f"Detected <b>{format_currency(total_pay)}</b> in payroll transactions "
        f"across <b>{n_employers:,}</b> employers and <b>{n_accounts:,}</b> accounts. "
        f"Payroll represents <b>{pct:.1f}%</b> of total debit card spend."
    ) if total_all > 0 else f"Detected {format_currency(total_pay)} in payroll transactions."

    tbl = pd.DataFrame([
        {"Metric": "Total Payroll Spend", "Value": round(total_pay, 2)},
        {"Metric": "Unique Employers", "Value": n_employers},
        {"Metric": "Unique Accounts", "Value": n_accounts},
        {"Metric": "Payroll % of Total", "Value": round(pct, 1)},
    ])
    section = {"heading": "Payroll Summary", "narrative": narrative,
               "figures": [fig], "tables": [("Payroll Summary", tbl)]}
    sheet = {"name": "S8 Payroll Summary", "df": tbl,
             "currency_cols": [], "pct_cols": [], "number_cols": []}
    return section, sheet


def _top_employers(pay: pd.DataFrame):
    agg = (
        pay.groupby("payroll_employer")
        .agg(total=("amount", "sum"), employees=("primary_account_num", "nunique"),
             txns=("amount", "count"))
        .sort_values("total", ascending=False).head(20).reset_index()
    )
    agg["avg"] = (agg["total"] / agg["employees"].replace(0, 1)).round(2)
    agg.columns = ["Employer", "Total Payroll", "Unique Employees", "Transactions", "Avg per Employee"]

    fig = horizontal_bar(agg, x_col="Total Payroll", y_col="Employer",
                         title="Top 20 Employers by Payroll Spend", top_n=20)
    apply_theme(fig)

    top = agg.iloc[0] if not agg.empty else None
    narrative = (
        f"The top employer is <b>{top['Employer']}</b> with "
        f"{format_currency(top['Total Payroll'])} across "
        f"<b>{int(top['Unique Employees']):,}</b> employees."
    ) if top is not None else ""

    section = {"heading": "Top Employers", "narrative": narrative,
               "figures": [fig], "tables": [("Top Employers", agg)]}
    sheet = {"name": "S8 Top Employers", "df": agg,
             "currency_cols": ["Total Payroll", "Avg per Employee"],
             "pct_cols": [], "number_cols": ["Unique Employees", "Transactions"]}
    return section, sheet


def _payroll_by_generation(pay: pd.DataFrame):
    agg = (
        pay.groupby("generation")
        .agg(total=("amount", "sum"), accts=("primary_account_num", "nunique"))
        .reindex(_GEN_ORDER).dropna(how="all").fillna(0).reset_index()
    )
    agg.columns = ["Generation", "Total Payroll", "Unique Accounts"]
    colors = [GENERATION_COLORS.get(g, COLORS["neutral"]) for g in agg["Generation"]]

    fig = go.Figure(go.Bar(
        x=agg["Generation"], y=agg["Total Payroll"], marker_color=colors,
        text=agg["Total Payroll"].apply(format_currency), textposition="outside",
        textfont=dict(size=10), hovertemplate="%{x}: %{y:$,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=insight_title("Payroll Volume by Generation",
                            "Workforce demographics across credit union members"),
        yaxis=dict(title=None, tickprefix="$", tickformat=","),
        showlegend=False, height=500,
    )
    apply_theme(fig)

    total = agg["Total Payroll"].sum()
    if total > 0:
        top = agg.loc[agg["Total Payroll"].idxmax()]
        narrative = (
            f"<b>{top['Generation']}</b> leads payroll volume at "
            f"{format_currency(top['Total Payroll'])} "
            f"({top['Total Payroll'] / total * 100:.1f}% of total), "
            f"with <b>{int(top['Unique Accounts']):,}</b> accounts."
        )
    else:
        narrative = "No payroll volume to break down by generation."

    section = {"heading": "Payroll by Generation", "narrative": narrative,
               "figures": [fig], "tables": [("Payroll by Generation", agg)]}
    sheet = {"name": "S8 Payroll by Gen", "df": agg,
             "currency_cols": ["Total Payroll"], "pct_cols": [], "number_cols": ["Unique Accounts"]}
    return section, sheet


def _monthly_trends(pay: pd.DataFrame):
    m = (
        pay.groupby("year_month")
        .agg(total=("amount", "sum"), accts=("primary_account_num", "nunique"))
        .reset_index()
    )
    m["year_month"] = m["year_month"].astype(str)
    m.columns = ["Month", "Total Payroll", "Accounts"]

    fig = line_trend(m, x_col="Month", y_cols=["Total Payroll"],
                     title="Monthly Payroll Trends",
                     colors=[COLORS["primary"]], y_format="$,.0f")
    apply_theme(fig)

    if len(m) >= 2:
        f_val, l_val = m.iloc[0]["Total Payroll"], m.iloc[-1]["Total Payroll"]
        chg = ((l_val - f_val) / f_val * 100) if f_val > 0 else 0
        direction = "increased" if chg > 0 else "decreased"
        narrative = (
            f"Monthly payroll has <b>{direction} {abs(chg):.1f}%</b> from "
            f"{format_currency(f_val)} to {format_currency(l_val)} over "
            f"{len(m)} months."
        )
    else:
        narrative = "Insufficient months for trend analysis."

    section = {"heading": "Monthly Payroll Trends", "narrative": narrative,
               "figures": [fig], "tables": [("Monthly Payroll", m)]}
    sheet = {"name": "S8 Payroll Trends", "df": m,
             "currency_cols": ["Total Payroll"], "pct_cols": [], "number_cols": ["Accounts"]}
    return section, sheet


def _circular_economy(df: pd.DataFrame, pay: pd.DataFrame):
    """Recapture rate: debit spend / payroll received for payroll recipients."""
    pay_accts = pay["primary_account_num"].unique()
    pay_by_acct = pay.groupby("primary_account_num")["amount"].sum()
    non_pay = df[df["primary_account_num"].isin(pay_accts) & ~df.index.isin(pay.index)]
    deb_by_acct = non_pay.groupby("primary_account_num")["amount"].sum()

    combo = pd.DataFrame({"payroll_received": pay_by_acct, "debit_spend": deb_by_acct}).fillna(0)
    combo = combo[combo["payroll_received"] > 0]
    if combo.empty:
        return (None, None)

    combo["recapture_pct"] = (combo["debit_spend"] / combo["payroll_received"] * 100).clip(upper=500)
    avg_recap = combo["recapture_pct"].mean()

    has_gen = "generation" in df.columns
    if has_gen:
        acct_gen = (
            df.loc[df["primary_account_num"].isin(pay_accts)]
            .drop_duplicates("primary_account_num")[["primary_account_num", "generation"]]
            .set_index("primary_account_num")
        )
        combo = combo.join(acct_gen, how="left")
        gr = (combo.groupby("generation")["recapture_pct"].mean()
              .reindex(_GEN_ORDER).dropna().reset_index())
        gr.columns = ["Generation", "Avg Recapture %"]
        gr["Avg Recapture %"] = gr["Avg Recapture %"].round(1)
        colors = [GENERATION_COLORS.get(g, COLORS["neutral"]) for g in gr["Generation"]]
        fig = go.Figure(go.Bar(
            x=gr["Generation"], y=gr["Avg Recapture %"], marker_color=colors,
            text=gr["Avg Recapture %"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside", textfont=dict(size=10),
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        ))
        fig.update_layout(
            title=insight_title(f"Avg Recapture Rate: {avg_recap:.1f}%",
                                "Debit spend as % of payroll received, by generation"),
            yaxis=dict(title=None, ticksuffix="%"), showlegend=False, height=500,
        )
        apply_theme(fig)
        tbl = gr
    else:
        tbl = pd.DataFrame([{"Metric": "Avg Recapture Rate", "Value": f"{avg_recap:.1f}%"}])
        fig = donut_chart(
            labels=["Recaptured via Debit", "Not Recaptured"],
            values=[min(avg_recap, 100), max(100 - avg_recap, 0)],
            title=f"Average Recapture Rate: {avg_recap:.1f}%",
            colors=[COLORS["positive"], COLORS["neutral"]],
        )
        apply_theme(fig)

    narrative = (
        f"Members who receive payroll spend an average of "
        f"<b>{avg_recap:.1f}%</b> of their deposited payroll back through "
        f"the credit union's debit card. A higher recapture rate indicates "
        f"stronger member engagement and primary financial institution (PFI) status."
    )
    pct_cols = ["Avg Recapture %"] if "Avg Recapture %" in tbl.columns else []
    section = {"heading": "Circular Economy: Debit Spend Recapture",
               "narrative": narrative, "figures": [fig], "tables": [("Recapture Rate", tbl)]}
    sheet = {"name": "S8 Circular Economy", "df": tbl,
             "currency_cols": [], "pct_cols": pct_cols, "number_cols": []}
    return (section, sheet)
