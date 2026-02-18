# v4_s9_lifecycle.py
# Storyline 9: Lifecycle Management
# =============================================================================
# 8 lifecycle stages from acquisition to attrition, one section per stage.
# Requires ODD columns: Date Opened, Date Closed, Debit?, Avg Bal, generation
# Uses combined_df for transaction-level metrics.

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from v4_themes import (
    COLORS, CATEGORY_PALETTE, GENERATION_COLORS,
    apply_theme, format_currency,
    horizontal_bar, donut_chart, heatmap, line_trend,
    lollipop_chart, grouped_bar, waterfall_chart,
    insight_title,
)


def run(ctx: dict) -> dict:
    """Run Lifecycle Management analyses."""
    df = ctx["combined_df"]
    odd = ctx["odd_df"]

    sections, sheets = [], []

    _data_coverage(odd, df, sections, sheets)
    _stage2_acquisition(odd, sections, sheets)
    _stage3_onboarding(odd, df, sections, sheets)
    _stage4_early_engagement(odd, df, ctx, sections, sheets)
    _stage5_daily_banking(odd, df, sections, sheets)
    _stage6_expansion(df, ctx, sections, sheets)
    _stage7_retention(odd, df, sections, sheets)
    _stage8_attrition(odd, df, ctx, sections, sheets)

    return {
        "title": "S9: Lifecycle Management",
        "description": (
            "8-stage lifecycle from acquisition to attrition: "
            "onboarding, engagement, daily banking, expansion, retention, attrition"
        ),
        "sections": sections,
        "sheets": sheets,
    }


# =============================================================================
# Data Coverage Summary
# =============================================================================

_STAGES = [
    ("1. Awareness", "NONE", "No awareness data available", "Marketing funnel data"),
    ("2. Acquisition", "STRONG", "New account openings, debit card possession", ""),
    ("3. Onboarding", "PARTIAL", "Activation rates, time-to-first-txn", "Digital onboarding events"),
    ("4. Early Engagement", "PARTIAL", "90-day spend profile, merchant diversity", "App login data"),
    ("5. Daily Banking", "FULL", "Primary bank score, txn frequency, ticket size", ""),
    ("6. Expansion", "PARTIAL", "MCC expansion, e-commerce growth", "Loan cross-sell data"),
    ("7. Retention", "STRONG", "Closure rate, survival, dormancy", "NPS / satisfaction"),
    ("8. Attrition", "FULL", "Lifecycle class, revenue at risk", ""),
]

_COVERAGE_COLORS = {"FULL": "#2D936C", "STRONG": "#68B684", "PARTIAL": "#F18F01", "NONE": "#C73E1D"}


def _data_coverage(odd, df, sections, sheets):
    rows = []
    for stage, level, metrics, gaps in _STAGES:
        rows.append({
            "Stage": stage, "Coverage": level,
            "Key Metrics": metrics, "Data Gaps": gaps or "None",
        })
    cov_df = pd.DataFrame(rows)

    fig = go.Figure(go.Bar(
        x=[_COVERAGE_COLORS.get(r["Coverage"], COLORS["neutral"]) for _, r in cov_df.iterrows()],
        y=cov_df["Stage"],
        orientation="h",
        marker_color=[_COVERAGE_COLORS.get(r["Coverage"], COLORS["neutral"]) for _, r in cov_df.iterrows()],
        text=cov_df["Coverage"],
        textposition="inside",
    ))
    fig.update_layout(
        title=insight_title("Lifecycle Data Coverage", "Green = full data, orange = partial, red = none"),
        xaxis=dict(visible=False), yaxis=dict(autorange="reversed"),
        height=350,
    )
    fig = apply_theme(fig)

    sections.append({
        "heading": "Lifecycle Data Coverage Summary",
        "narrative": (
            "This lifecycle analysis covers 8 stages. Coverage ranges from "
            "<b>FULL</b> (all key metrics available) to <b>NONE</b> (no data). "
            "Stage 1 (Awareness) has no data available in the transaction/ODD files."
        ),
        "figures": [fig], "tables": [("Data Coverage", cov_df)],
    })
    sheets.append({"name": "S9 Coverage", "df": cov_df})


# =============================================================================
# Stage 2: Acquisition
# =============================================================================

def _stage2_acquisition(odd, sections, sheets):
    if "Date Opened" not in odd.columns:
        sections.append({
            "heading": "Stage 2: Acquisition",
            "narrative": "Date Opened not available in ODD; acquisition analysis skipped.",
            "figures": [], "tables": [],
        })
        return

    odd_acq = odd.dropna(subset=["Date Opened"]).copy()
    odd_acq["open_month"] = odd_acq["Date Opened"].dt.to_period("M").astype(str)
    monthly = odd_acq.groupby("open_month").size().reset_index(name="New Accounts")
    monthly = monthly.sort_values("open_month")

    fig = apply_theme(line_trend(
        monthly, "open_month", ["New Accounts"],
        "Monthly New Account Openings",
    ))
    fig.update_layout(title=insight_title(
        "New account acquisition trend",
        f"{monthly['New Accounts'].sum():,} total accounts opened",
    ))

    # Debit card possession rate
    debit_narr = ""
    if "Debit?" in odd.columns:
        debit_yes = (odd["Debit?"].astype(str).str.upper() == "YES").sum()
        debit_pct = (debit_yes / len(odd) * 100) if len(odd) > 0 else 0
        debit_narr = f" Debit card possession rate: <b>{debit_pct:.1f}%</b> ({debit_yes:,} of {len(odd):,})."

    narr = (
        f"<b>{monthly['New Accounts'].sum():,}</b> accounts opened across "
        f"<b>{len(monthly)}</b> months.{debit_narr}"
    )

    sections.append({
        "heading": "Stage 2: Acquisition",
        "narrative": narr,
        "figures": [fig], "tables": [("Monthly Openings", monthly)],
    })
    sheets.append({
        "name": "S9 Acquisition", "df": monthly,
        "number_cols": ["New Accounts"],
    })


# =============================================================================
# Stage 3: Onboarding & Activation
# =============================================================================

def _stage3_onboarding(odd, df, sections, sheets):
    if "Date Opened" not in odd.columns or "transaction_date" not in df.columns:
        sections.append({
            "heading": "Stage 3: Onboarding & Activation",
            "narrative": "Missing Date Opened or transaction_date; activation analysis skipped.",
            "figures": [], "tables": [],
        })
        return

    # Get first transaction per account
    first_txn = df.groupby("primary_account_num")["transaction_date"].min().reset_index()
    first_txn.columns = ["Acct Number", "first_txn_date"]

    # Match to ODD accounts with Date Opened
    accts = odd[["Acct Number", "Date Opened"]].dropna(subset=["Date Opened"]).copy()
    if "Acct Number" not in accts.columns:
        sections.append({
            "heading": "Stage 3: Onboarding & Activation",
            "narrative": "Acct Number not available; activation analysis skipped.",
            "figures": [], "tables": [],
        })
        return

    merged = accts.merge(first_txn, on="Acct Number", how="left")
    merged["days_to_first_txn"] = (
        (merged["first_txn_date"] - merged["Date Opened"]).dt.days
    )

    # 30/60/90-day activation rates
    total = len(merged)
    activated_30 = (merged["days_to_first_txn"].between(0, 30)).sum()
    activated_60 = (merged["days_to_first_txn"].between(0, 60)).sum()
    activated_90 = (merged["days_to_first_txn"].between(0, 90)).sum()
    never = merged["days_to_first_txn"].isna().sum()

    act_df = pd.DataFrame([
        {"Window": "30 days", "Activated": int(activated_30),
         "Rate (%)": round(activated_30 / total * 100, 1) if total else 0},
        {"Window": "60 days", "Activated": int(activated_60),
         "Rate (%)": round(activated_60 / total * 100, 1) if total else 0},
        {"Window": "90 days", "Activated": int(activated_90),
         "Rate (%)": round(activated_90 / total * 100, 1) if total else 0},
        {"Window": "Never", "Activated": int(never),
         "Rate (%)": round(never / total * 100, 1) if total else 0},
    ])

    fig = apply_theme(lollipop_chart(
        act_df[act_df["Window"] != "Never"], "Rate (%)", "Window",
        "Activation Rates by Window",
    ))
    fig.update_layout(title=insight_title(
        f"{round(activated_90 / total * 100, 1) if total else 0:.1f}% activated within 90 days",
        f"{total:,} accounts analyzed",
    ))

    narr = (
        f"Of <b>{total:,}</b> accounts, <b>{activated_30:,}</b> activated within 30 days "
        f"({round(activated_30/total*100,1) if total else 0:.1f}%), "
        f"<b>{activated_90:,}</b> within 90 days "
        f"({round(activated_90/total*100,1) if total else 0:.1f}%). "
        f"<b>{never:,}</b> accounts have no transaction activity."
    )

    sections.append({
        "heading": "Stage 3: Onboarding & Activation",
        "narrative": narr,
        "figures": [fig], "tables": [("Activation Rates", act_df)],
    })
    sheets.append({
        "name": "S9 Onboarding", "df": act_df,
        "pct_cols": ["Rate (%)"], "number_cols": ["Activated"],
    })


# =============================================================================
# Stage 4: Early Engagement (first 90 days)
# =============================================================================

def _stage4_early_engagement(odd, df, ctx, sections, sheets):
    # Date Opened is already on combined_df via _MERGE_COLS; use it directly
    # to avoid column collision from re-merging with ODD.
    if "Date Opened" not in df.columns:
        return

    valid = df.dropna(subset=["Date Opened"]).copy()
    valid["days_since_open"] = (valid["transaction_date"] - valid["Date Opened"]).dt.days
    early = valid[(valid["days_since_open"] >= 0) & (valid["days_since_open"] <= 90)]

    if early.empty:
        return

    # Early engagement metrics
    early_accts = early["primary_account_num"].nunique()
    early_txn = len(early)
    early_spend = early["amount"].sum()
    avg_ticket = early["amount"].mean()
    merch_col = "merchant_consolidated" if "merchant_consolidated" in early.columns else "merchant_name"
    merchant_diversity = early.groupby("primary_account_num")[merch_col].nunique().mean()

    # Portfolio-wide averages for comparison
    port_avg_ticket = df["amount"].mean()
    port_merchant_div = df.groupby("primary_account_num")[merch_col].nunique().mean()

    metrics = pd.DataFrame([
        {"Metric": "Accounts with Early Txns", "Early (0-90d)": early_accts, "Portfolio Avg": df["primary_account_num"].nunique()},
        {"Metric": "Avg Ticket Size ($)", "Early (0-90d)": round(avg_ticket, 2), "Portfolio Avg": round(port_avg_ticket, 2)},
        {"Metric": "Avg Merchant Diversity", "Early (0-90d)": round(merchant_diversity, 1), "Portfolio Avg": round(port_merchant_div, 1)},
        {"Metric": "Total Spend", "Early (0-90d)": round(early_spend, 2), "Portfolio Avg": round(df["amount"].sum(), 2)},
    ])

    narr = (
        f"<b>{early_accts:,}</b> accounts transacted within 90 days of opening. "
        f"Early avg ticket: <b>{format_currency(avg_ticket)}</b> "
        f"(portfolio: {format_currency(port_avg_ticket)}). "
        f"Early merchant diversity: <b>{merchant_diversity:.1f}</b> unique merchants "
        f"(portfolio: {port_merchant_div:.1f})."
    )

    sections.append({
        "heading": "Stage 4: Early Engagement (First 90 Days)",
        "narrative": narr,
        "figures": [], "tables": [("Early Engagement Metrics", metrics)],
    })
    sheets.append({
        "name": "S9 Early Engagement", "df": metrics,
        "currency_cols": [],
        "number_cols": ["Early (0-90d)", "Portfolio Avg"],
    })


# =============================================================================
# Stage 5: Daily Banking (Primary Bank Proxy)
# =============================================================================

def _stage5_daily_banking(odd, df, sections, sheets):
    acct_metrics = df.groupby("primary_account_num").agg(
        total_spend=("amount", "sum"),
        txn_count=("amount", "count"),
        months_active=("year_month", "nunique") if "year_month" in df.columns else ("amount", "count"),
        mcc_diversity=("mcc_code", "nunique") if "mcc_code" in df.columns else ("amount", "count"),
    ).reset_index()

    if "year_month" in df.columns:
        max_months = df["year_month"].nunique()
        acct_metrics["txns_per_month"] = (acct_metrics["txn_count"] / acct_metrics["months_active"]).round(1)
        acct_metrics["spend_per_month"] = (acct_metrics["total_spend"] / acct_metrics["months_active"]).round(2)
    else:
        acct_metrics["txns_per_month"] = acct_metrics["txn_count"]
        acct_metrics["spend_per_month"] = acct_metrics["total_spend"]

    # Payroll detection from ctx
    payroll_accts = set()
    if "s8_payroll_accounts" in df.columns:
        payroll_accts = set(df.loc[df["s8_payroll_accounts"] == True, "primary_account_num"].unique())

    # Check PIN + Sig usage from ODD
    has_pin_sig = "card_present" in df.columns

    # Score: 0-100
    def _score(row):
        s = 0
        if row["primary_account_num"] in payroll_accts:
            s += 30
        if row["txns_per_month"] > 20:
            s += 25
        if "mcc_diversity" in row.index and row["mcc_diversity"] > 5:
            s += 20
        if row["spend_per_month"] > 1000:
            s += 15
        if has_pin_sig:
            s += 10  # simplified: assume both if present
        return min(s, 100)

    acct_metrics["primary_bank_score"] = acct_metrics.apply(_score, axis=1)
    acct_metrics["classification"] = pd.cut(
        acct_metrics["primary_bank_score"],
        bins=[-1, 29, 59, 100],
        labels=["Minimal (<30)", "Secondary (30-59)", "Primary (60+)"],
    )

    class_dist = acct_metrics["classification"].value_counts().reset_index()
    class_dist.columns = ["Classification", "Accounts"]
    class_dist["% of Total"] = (class_dist["Accounts"] / class_dist["Accounts"].sum() * 100).round(1)

    fig = donut_chart(
        class_dist["Classification"], class_dist["Accounts"],
        "Primary Bank Classification",
        colors=[COLORS["positive"], COLORS["accent"], COLORS["negative"]],
    )
    fig.update_layout(title=insight_title(
        "Primary bank relationship proxy",
        "Score: Payroll(30) + Txns(25) + MCCs(20) + Spend(15) + PIN/Sig(10)",
    ))
    fig = apply_theme(fig)

    # Benchmark comparison (PULSE 2024)
    avg_ticket = df["amount"].mean()
    avg_tpac = acct_metrics["txns_per_month"].mean()

    benchmark = pd.DataFrame([
        {"Metric": "Avg Txns per Account/Month", "This CU": round(avg_tpac, 1), "PULSE 2024": 30.7},
        {"Metric": "Avg Ticket Size ($)", "This CU": round(avg_ticket, 2), "PULSE 2024": 46.89},
    ])

    bench_fig = apply_theme(grouped_bar(
        benchmark, "Metric", ["This CU", "PULSE 2024"],
        "Performance vs PULSE 2024 Benchmark",
        colors=[COLORS["primary"], COLORS["accent"]],
    ))

    primary_count = int(class_dist.loc[class_dist["Classification"] == "Primary (60+)", "Accounts"].sum())
    total = class_dist["Accounts"].sum()
    narr = (
        f"<b>{primary_count:,}</b> accounts ({round(primary_count/total*100,1) if total else 0:.1f}%) "
        f"classified as <b>Primary</b> banking relationships. "
        f"Average {avg_tpac:.1f} txns/month (PULSE benchmark: 30.7). "
        f"Average ticket: {format_currency(avg_ticket)} (PULSE: $46.89)."
    )

    sections.append({
        "heading": "Stage 5: Daily Banking (Primary Bank Proxy)",
        "narrative": narr,
        "figures": [fig, bench_fig],
        "tables": [("Primary Bank Classification", class_dist), ("PULSE Benchmark", benchmark)],
    })
    sheets.append({
        "name": "S9 Daily Banking", "df": class_dist,
        "pct_cols": ["% of Total"], "number_cols": ["Accounts"],
    })


# =============================================================================
# Stage 6: Expansion
# =============================================================================

def _stage6_expansion(df, ctx, sections, sheets):
    if "mcc_code" not in df.columns or "year_month" not in df.columns:
        return

    sorted_months = sorted(df["year_month"].unique())
    if len(sorted_months) < 6:
        return

    # MCC diversity: first 90 days vs last 90 days (proxy: first 3 vs last 3 months)
    early_months = sorted_months[:3]
    late_months = sorted_months[-3:]

    early_div = (
        df[df["year_month"].isin(early_months)]
        .groupby("primary_account_num")["mcc_code"].nunique()
        .mean()
    )
    late_div = (
        df[df["year_month"].isin(late_months)]
        .groupby("primary_account_num")["mcc_code"].nunique()
        .mean()
    )
    expansion = ((late_div - early_div) / early_div * 100) if early_div > 0 else 0

    # E-commerce growth (card-not-present proxy)
    ecom_narr = ""
    if "card_present" in df.columns:
        cp_col = df["card_present"].astype(str).str.strip().str.upper()
        early_cnp = (
            df[df["year_month"].isin(early_months)]
            .assign(cnp=cp_col.isin(["N", "NO", "FALSE", "0"]))["cnp"].mean() * 100
        )
        late_cnp = (
            df[df["year_month"].isin(late_months)]
            .assign(cnp=cp_col.isin(["N", "NO", "FALSE", "0"]))["cnp"].mean() * 100
        )
        ecom_narr = (
            f" E-commerce (card-not-present): {early_cnp:.1f}% -> {late_cnp:.1f}% "
            f"({late_cnp - early_cnp:+.1f} pp)."
        )

    exp_df = pd.DataFrame([
        {"Metric": "Avg MCC Categories (Early)", "Value": round(early_div, 1)},
        {"Metric": "Avg MCC Categories (Recent)", "Value": round(late_div, 1)},
        {"Metric": "MCC Expansion (%)", "Value": round(expansion, 1)},
    ])

    narr = (
        f"Merchant category diversity expanded from <b>{early_div:.1f}</b> to "
        f"<b>{late_div:.1f}</b> avg categories per account "
        f"(<b>{expansion:+.1f}%</b>).{ecom_narr}"
    )

    sections.append({
        "heading": "Stage 6: Expansion",
        "narrative": narr,
        "figures": [], "tables": [("Expansion Metrics", exp_df)],
    })
    sheets.append({
        "name": "S9 Expansion", "df": exp_df,
        "number_cols": ["Value"],
    })


# =============================================================================
# Stage 7: Retention
# =============================================================================

def _stage7_retention(odd, df, sections, sheets):
    figs = []

    # Closure rate trending
    closure_df = None
    if "Date Closed" in odd.columns:
        closed = odd.dropna(subset=["Date Closed"]).copy()
        if not closed.empty:
            closed["close_month"] = closed["Date Closed"].dt.to_period("M").astype(str)
            closure_df = closed.groupby("close_month").size().reset_index(name="Closures")
            closure_df = closure_df.sort_values("close_month")
            fig = apply_theme(line_trend(
                closure_df, "close_month", ["Closures"],
                "Monthly Account Closures",
            ))
            figs.append(fig)

    # Dormancy rate: zero txns in last 90 days
    if "year_month" in df.columns:
        sorted_months = sorted(df["year_month"].unique())
        if len(sorted_months) >= 3:
            recent_3 = sorted_months[-3:]
            active_accts = set(df[df["year_month"].isin(recent_3)]["primary_account_num"].unique())
            all_accts = set(odd["Acct Number"].unique()) if "Acct Number" in odd.columns else set()
            dormant = all_accts - active_accts
            dormancy_rate = (len(dormant) / len(all_accts) * 100) if all_accts else 0
        else:
            dormant = set()
            dormancy_rate = 0
    else:
        dormant = set()
        dormancy_rate = 0

    # Retention cohort: opened per quarter, % still open
    retention_df = None
    if "Date Opened" in odd.columns:
        accts = odd[["Acct Number", "Date Opened"]].dropna(subset=["Date Opened"]).copy()
        accts["open_quarter"] = accts["Date Opened"].dt.to_period("Q").astype(str)
        if "Date Closed" in odd.columns:
            accts["is_open"] = odd["Date Closed"].isna()
        else:
            accts["is_open"] = True
        retention_df = accts.groupby("open_quarter").agg(
            opened=("Acct Number", "count"),
            still_open=("is_open", "sum"),
        ).reset_index()
        retention_df["Survival %"] = (retention_df["still_open"] / retention_df["opened"] * 100).round(1)
        retention_df.columns = ["Quarter Opened", "Opened", "Still Open", "Survival %"]
        retention_df = retention_df.sort_values("Quarter Opened")

    narr = (
        f"Dormancy rate (no txns in last 90 days): <b>{dormancy_rate:.1f}%</b> "
        f"({len(dormant):,} accounts)."
    )
    if closure_df is not None and not closure_df.empty:
        narr += f" Total closures tracked: <b>{closure_df['Closures'].sum():,}</b>."

    tables = []
    if retention_df is not None:
        tables.append(("Retention Cohort", retention_df))
    if closure_df is not None:
        tables.append(("Closure Trend", closure_df))

    sections.append({
        "heading": "Stage 7: Retention",
        "narrative": narr,
        "figures": figs, "tables": tables,
    })
    if retention_df is not None:
        sheets.append({
            "name": "S9 Retention", "df": retention_df,
            "pct_cols": ["Survival %"], "number_cols": ["Opened", "Still Open"],
        })


# =============================================================================
# Stage 8: Attrition & Recovery
# =============================================================================

def _stage8_attrition(odd, df, ctx, sections, sheets):
    if "year_month" not in df.columns:
        return

    config = ctx.get("config", {})
    interchange_rate = config.get("interchange_rate", 0.015)

    sorted_months = sorted(df["year_month"].unique())
    if len(sorted_months) < 3:
        return

    recent_3 = sorted_months[-3:]
    prev_3 = sorted_months[-6:-3] if len(sorted_months) >= 6 else sorted_months[:3]

    acct_recent = (
        df[df["year_month"].isin(recent_3)]
        .groupby("primary_account_num")["amount"].sum()
        .rename("recent_spend")
    )
    acct_prev = (
        df[df["year_month"].isin(prev_3)]
        .groupby("primary_account_num")["amount"].sum()
        .rename("prev_spend")
    )

    acct = pd.concat([acct_recent, acct_prev], axis=1).fillna(0)
    acct["change_pct"] = np.where(
        acct["prev_spend"] > 0,
        (acct["recent_spend"] - acct["prev_spend"]) / acct["prev_spend"] * 100,
        np.where(acct["recent_spend"] > 0, 100, 0),
    )

    # Lifecycle classification
    def _classify(row):
        if row["recent_spend"] == 0 and row["prev_spend"] == 0:
            return "Lost"
        if row["recent_spend"] == 0:
            return "Dormant"
        if row["change_pct"] > 10:
            return "Growing"
        if row["change_pct"] < -10:
            return "Declining"
        return "Stable"

    acct["lifecycle"] = acct.apply(_classify, axis=1)

    class_dist = acct["lifecycle"].value_counts().reset_index()
    class_dist.columns = ["Lifecycle Stage", "Accounts"]
    class_dist["% of Total"] = (class_dist["Accounts"] / class_dist["Accounts"].sum() * 100).round(1)

    # Revenue at risk: declining + dormant annual spend projected from prev
    at_risk_accts = acct[acct["lifecycle"].isin(["Declining", "Dormant"])]
    annual_at_risk = at_risk_accts["prev_spend"].sum() * (12 / max(len(prev_3), 1))
    interchange_risk = annual_at_risk * interchange_rate

    # Waterfall chart: lifecycle flow
    labels = ["Growing", "Stable", "Declining", "Dormant", "Lost"]
    values = []
    for l in labels:
        row = class_dist[class_dist["Lifecycle Stage"] == l]
        values.append(int(row["Accounts"].iloc[0]) if not row.empty else 0)

    wf_labels = labels + ["Total"]
    wf_values = values + [sum(values)]
    wf_fig = apply_theme(waterfall_chart(
        wf_labels, wf_values,
        "Lifecycle Classification Waterfall",
    ))

    # Attrition by generation heatmap
    hm_fig = None
    if "generation" in df.columns:
        acct_gen = df.drop_duplicates("primary_account_num")[["primary_account_num", "generation"]]
        acct_with_gen = acct.reset_index().merge(acct_gen, on="primary_account_num", how="left")
        ct = pd.crosstab(acct_with_gen["generation"], acct_with_gen["lifecycle"])
        ct_pct = ct.div(ct.sum(axis=1), axis=0).mul(100).round(1)
        if not ct_pct.empty:
            hm_fig = heatmap(ct_pct, "Attrition by Generation (%)", fmt=".1f")
            hm_fig = apply_theme(hm_fig)

    narr = (
        f"Lifecycle: <b>{values[0]:,}</b> growing, <b>{values[1]:,}</b> stable, "
        f"<b>{values[2]:,}</b> declining, <b>{values[3]:,}</b> dormant, "
        f"<b>{values[4]:,}</b> lost. "
        f"Revenue at risk: <b>{format_currency(annual_at_risk)}</b>/yr "
        f"(est. interchange: {format_currency(interchange_risk)})."
    )

    all_figs = [wf_fig]
    if hm_fig is not None:
        all_figs.append(hm_fig)

    sections.append({
        "heading": "Stage 8: Attrition & Recovery",
        "narrative": narr,
        "figures": all_figs,
        "tables": [("Lifecycle Classification", class_dist)],
    })
    sheets.append({
        "name": "S9 Attrition", "df": class_dist,
        "pct_cols": ["% of Total"], "number_cols": ["Accounts"],
    })

    # --- Enhanced attrition sub-analyses ---
    _attrition_risk_scoring(odd, df, acct, sections, sheets)
    _attrition_competitor_xref(acct, ctx, sections, sheets)
    _attrition_revenue_impact(acct, config, sections, sheets)


# =============================================================================
# Attrition Enhancement: Risk Scoring
# =============================================================================

def _attrition_risk_scoring(odd, df, acct, sections, sheets):
    """Score each account 0-100 based on weighted attrition signals."""
    if acct.empty:
        return

    scores = acct[["recent_spend", "prev_spend", "change_pct", "lifecycle"]].copy()

    # Signal 1: Months since last transaction (weight 25)
    last_txn = df.groupby("primary_account_num")["transaction_date"].max()
    max_date = df["transaction_date"].max()
    months_inactive = ((max_date - last_txn).dt.days / 30).clip(upper=12)
    scores["inactivity_score"] = months_inactive.reindex(scores.index).fillna(12)
    scores["inactivity_score"] = (scores["inactivity_score"] / 12 * 25).round(1)

    # Signal 2: MoM spend decline (weight 25)
    scores["decline_score"] = np.where(
        scores["change_pct"] < 0,
        np.minimum(abs(scores["change_pct"]) / 100, 1.0) * 25,
        0,
    )

    # Signal 3: Below-avg balance (weight 15)
    if "Avg Bal" in odd.columns and "Acct Number" in odd.columns:
        bal = odd.set_index("Acct Number")["Avg Bal"]
        median_bal = bal.median()
        acct_bal = bal.reindex(scores.index).fillna(0)
        scores["balance_score"] = np.where(
            (median_bal > 0) & (acct_bal < median_bal),
            (1 - acct_bal / median_bal).clip(upper=1.0) * 15,
            0,
        )
    else:
        scores["balance_score"] = 0

    # Signal 4: Account age < 12 months (weight 15)
    if "Date Opened" in odd.columns and "Acct Number" in odd.columns:
        opened = odd.set_index("Acct Number")["Date Opened"]
        days_open = (max_date - opened.reindex(scores.index)).dt.days.fillna(9999)
        scores["new_acct_score"] = np.where(
            days_open < 365, (1 - days_open / 365) * 15, 0,
        )
    else:
        scores["new_acct_score"] = 0

    # Signal 5: Competitor activity placeholder (weight 20, filled if S3 data exists)
    scores["competitor_score"] = 0  # populated in _attrition_competitor_xref

    scores["risk_score"] = (
        scores["inactivity_score"]
        + scores["decline_score"]
        + scores["balance_score"]
        + scores["new_acct_score"]
        + scores["competitor_score"]
    ).round(0).astype(int).clip(upper=100)

    # Risk tiers
    scores["risk_tier"] = pd.cut(
        scores["risk_score"],
        bins=[-1, 25, 50, 75, 100],
        labels=["Low", "Medium", "High", "Critical"],
    )

    tier_dist = scores["risk_tier"].value_counts().reindex(
        ["Critical", "High", "Medium", "Low"]
    ).fillna(0).astype(int).reset_index()
    tier_dist.columns = ["Risk Tier", "Accounts"]
    tier_dist["% of Total"] = (
        tier_dist["Accounts"] / max(tier_dist["Accounts"].sum(), 1) * 100
    ).round(1)

    colors = {
        "Critical": COLORS["negative"],
        "High": COLORS["accent"],
        "Medium": COLORS["neutral"],
        "Low": COLORS["positive"],
    }
    bar_colors = [colors.get(t, COLORS["neutral"]) for t in tier_dist["Risk Tier"]]

    fig = go.Figure(go.Bar(
        x=tier_dist["Risk Tier"],
        y=tier_dist["Accounts"],
        marker_color=bar_colors,
        text=tier_dist["Accounts"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="%{x}: %{y:,} accounts<extra></extra>",
    ))
    fig.update_layout(
        title=insight_title(
            "Attrition Risk Distribution",
            "Accounts scored 0-100 based on inactivity, spend decline, balance, and account age",
        ),
        yaxis=dict(title=None), showlegend=False, height=450,
    )
    apply_theme(fig)

    critical = int(tier_dist.loc[tier_dist["Risk Tier"] == "Critical", "Accounts"].sum())
    high = int(tier_dist.loc[tier_dist["Risk Tier"] == "High", "Accounts"].sum())
    narr = (
        f"<b>{critical + high:,}</b> accounts are at high or critical attrition risk. "
        f"<b>{critical:,}</b> critical-risk accounts require immediate outreach."
    )

    sections.append({
        "heading": "Attrition Risk Scoring",
        "narrative": narr,
        "figures": [fig],
        "tables": [("Risk Tier Distribution", tier_dist)],
    })
    sheets.append({
        "name": "S9 Risk Scores", "df": tier_dist,
        "pct_cols": ["% of Total"], "number_cols": ["Accounts"],
    })


# =============================================================================
# Attrition Enhancement: Competitor Cross-Reference
# =============================================================================

def _attrition_competitor_xref(acct, ctx, sections, sheets):
    """Cross-reference at-risk accounts with S3 competitor transaction data."""
    s3_tagged = ctx.get("s3_tagged_df")
    if s3_tagged is None or s3_tagged.empty:
        return

    at_risk_ids = set(
        acct[acct["lifecycle"].isin(["Declining", "Dormant", "Lost"])].index
    )
    if not at_risk_ids:
        return

    comp_col = None
    for col in ["competitor_category", "competitor_name", "competitor"]:
        if col in s3_tagged.columns:
            comp_col = col
            break
    if comp_col is None:
        return

    comp_accts = set(s3_tagged["primary_account_num"].unique())
    overlap = at_risk_ids & comp_accts
    no_overlap = at_risk_ids - comp_accts

    if not overlap:
        return

    overlap_df = s3_tagged[s3_tagged["primary_account_num"].isin(overlap)]

    # Top competitors stealing at-risk accounts
    top_comp = (
        overlap_df.groupby(comp_col)
        .agg(
            accounts=("primary_account_num", "nunique"),
            spend=("amount", "sum"),
        )
        .sort_values("spend", ascending=False)
        .head(10)
        .reset_index()
    )
    top_comp.columns = ["Competitor", "At-Risk Accounts", "Spend to Competitor"]

    fig = donut_chart(
        labels=["With Competitor Activity", "No Competitor Activity"],
        values=[len(overlap), len(no_overlap)],
        title="At-Risk Accounts: Competitor Activity",
        colors=[COLORS["negative"], COLORS["neutral"]],
    )
    apply_theme(fig)

    pct_w_comp = len(overlap) / max(len(at_risk_ids), 1) * 100
    narr = (
        f"<b>{len(overlap):,}</b> of <b>{len(at_risk_ids):,}</b> at-risk accounts "
        f"(<b>{pct_w_comp:.1f}%</b>) are actively transacting with competitors. "
        f"Top competitor: <b>{top_comp.iloc[0]['Competitor']}</b> with "
        f"{top_comp.iloc[0]['At-Risk Accounts']:,} at-risk accounts."
    ) if not top_comp.empty else ""

    sections.append({
        "heading": "Attrition: Competitor Cross-Reference",
        "narrative": narr,
        "figures": [fig],
        "tables": [("Top Competitors (At-Risk Accounts)", top_comp)],
    })
    sheets.append({
        "name": "S9 Attrition Competitors", "df": top_comp,
        "currency_cols": ["Spend to Competitor"],
        "number_cols": ["At-Risk Accounts"],
    })


# =============================================================================
# Attrition Enhancement: Revenue Impact & Winback Sizing
# =============================================================================

def _attrition_revenue_impact(acct, config, sections, sheets):
    """Quantify revenue at risk and winback opportunity by risk tier."""
    if acct.empty:
        return

    interchange_rate = config.get("interchange_rate", 0.015)
    at_risk = acct[acct["lifecycle"].isin(["Declining", "Dormant"])].copy()
    if at_risk.empty:
        return

    # Annualize from 3-month prev_spend window
    at_risk["annual_spend_est"] = at_risk["prev_spend"] * 4

    # Risk tiers based on decline severity
    at_risk["risk_tier"] = pd.cut(
        at_risk["change_pct"],
        bins=[-np.inf, -75, -50, -25, 0],
        labels=["Critical", "High", "Medium", "Low"],
    )

    tier_summary = (
        at_risk.groupby("risk_tier", observed=False)
        .agg(
            accounts=("annual_spend_est", "count"),
            annual_spend=("annual_spend_est", "sum"),
        )
        .reset_index()
    )
    tier_summary["revenue_at_risk"] = (tier_summary["annual_spend"] * interchange_rate).round(2)

    # Winback assumptions: Critical 10%, High 20%, Medium 35%, Low 50%
    winback_rates = {"Critical": 0.10, "High": 0.20, "Medium": 0.35, "Low": 0.50}
    tier_summary["winback_rate"] = tier_summary["risk_tier"].map(winback_rates).fillna(0.25)
    tier_summary["winback_revenue"] = (
        tier_summary["revenue_at_risk"] * tier_summary["winback_rate"]
    ).round(2)

    tier_summary.columns = [
        "Risk Tier", "Accounts", "Annual Spend", "Revenue at Risk",
        "Winback Rate", "Winback Revenue",
    ]
    tier_summary["Winback Rate"] = (tier_summary["Winback Rate"] * 100).round(0).astype(int)

    # Summary bar chart
    fig = grouped_bar(
        tier_summary,
        x_col="Risk Tier",
        y_cols=["Revenue at Risk", "Winback Revenue"],
        title="Revenue at Risk vs Winback Opportunity by Tier",
        colors=[COLORS["negative"], COLORS["positive"]],
    )
    fig.update_layout(
        yaxis=dict(tickprefix="$", tickformat=","),
        height=450,
    )
    apply_theme(fig)

    total_risk = tier_summary["Revenue at Risk"].sum()
    total_winback = tier_summary["Winback Revenue"].sum()
    narr = (
        f"Total interchange revenue at risk: <b>{format_currency(total_risk)}</b>/yr "
        f"across <b>{tier_summary['Accounts'].sum():,}</b> declining/dormant accounts. "
        f"Estimated winback opportunity: <b>{format_currency(total_winback)}</b>/yr "
        f"based on tier-specific recovery rates (10-50%)."
    )

    sections.append({
        "heading": "Attrition: Revenue Impact & Winback Sizing",
        "narrative": narr,
        "figures": [fig],
        "tables": [("Revenue Impact by Risk Tier", tier_summary)],
    })
    sheets.append({
        "name": "S9 Revenue Impact", "df": tier_summary,
        "currency_cols": ["Annual Spend", "Revenue at Risk", "Winback Revenue"],
        "pct_cols": [], "number_cols": ["Accounts", "Winback Rate"],
    })
