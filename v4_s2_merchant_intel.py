# v4_s2_merchant_intel.py
# Storyline 2: Merchant Intelligence
# =============================================================================
# Top merchants, MCC analysis, business/personal splits, rank movement, growth

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from v4_themes import (
    COLORS, CATEGORY_PALETTE, apply_theme, format_currency,
    horizontal_bar, line_trend,
)


def run(ctx: dict) -> dict:
    """
    Run Merchant Intelligence analyses.
    """
    df = ctx["combined_df"]
    biz = ctx["business_df"]
    per = ctx["personal_df"]
    config = ctx["config"]
    top_n = config.get("top_n", 50)

    sections = []
    sheets = []
    merch_col = "merchant_consolidated" if "merchant_consolidated" in df.columns else "merchant_name"

    # --- Top Merchants by Spend ---
    spend_df = _top_merchants(df, merch_col, "amount_sum", top_n)
    spend_fig = _merchant_bar(spend_df, "Total Spend", f"Top {min(25, top_n)} Merchants by Total Spend")
    sections.append({
        "heading": "Top Merchants by Total Spend",
        "narrative": _top_narrative(spend_df, "spend", df),
        "figures": [spend_fig],
        "tables": [("Top Merchants - Spend", spend_df.head(top_n))],
    })
    sheets.append({
        "name": "S2 Top Spend",
        "df": spend_df,
        "currency_cols": ["Total Spend", "Avg Transaction"],
        "number_cols": ["Transactions", "Unique Accounts"],
    })

    # --- Top Merchants by Transaction Count ---
    txn_df = _top_merchants(df, merch_col, "txn_count", top_n)
    txn_fig = _merchant_bar(txn_df, "Transactions", f"Top {min(25, top_n)} Merchants by Transaction Count", color=COLORS["secondary"])
    sections.append({
        "heading": "Top Merchants by Transaction Count",
        "narrative": "",
        "figures": [txn_fig],
        "tables": [("Top Merchants - Transactions", txn_df.head(top_n))],
    })
    sheets.append({
        "name": "S2 Top Txn Count",
        "df": txn_df,
        "currency_cols": ["Total Spend", "Avg Transaction"],
        "number_cols": ["Transactions", "Unique Accounts"],
    })

    # --- Top Merchants by Unique Accounts ---
    acct_df = _top_merchants(df, merch_col, "unique_accounts", top_n)
    acct_fig = _merchant_bar(acct_df, "Unique Accounts", f"Top {min(25, top_n)} Merchants by Account Penetration", color=COLORS["accent"])
    sections.append({
        "heading": "Top Merchants by Unique Accounts",
        "narrative": "",
        "figures": [acct_fig],
        "tables": [],
    })
    sheets.append({
        "name": "S2 Top Accounts",
        "df": acct_df,
        "currency_cols": ["Total Spend", "Avg Transaction"],
        "number_cols": ["Transactions", "Unique Accounts"],
    })

    # --- MCC Category Analysis ---
    if "mcc_code" in df.columns:
        mcc_df = _mcc_analysis(df, top_n)
        mcc_fig = _merchant_bar(mcc_df, "Total Spend", "Top 20 MCC Categories by Spend", y_col="MCC Code", color=COLORS["primary"])
        sections.append({
            "heading": "Merchant Category (MCC) Analysis",
            "narrative": f"Top {top_n} MCC codes analyzed across spend, transaction volume, and account penetration.",
            "figures": [mcc_fig],
            "tables": [("MCC Categories", mcc_df.head(20))],
        })
        sheets.append({
            "name": "S2 MCC Analysis",
            "df": mcc_df,
            "currency_cols": ["Total Spend", "Avg Transaction"],
            "number_cols": ["Transactions", "Unique Accounts", "Merchants"],
        })

    # --- Business Top Merchants ---
    if len(biz) > 0:
        biz_df = _top_merchants(biz, merch_col, "amount_sum", top_n)
        biz_fig = _merchant_bar(biz_df, "Total Spend", "Top 25 Business Merchants by Spend", color="#7B2D8E")
        sections.append({
            "heading": "Business Account - Top Merchants",
            "narrative": f"<b>{len(biz):,}</b> business transactions across <b>{biz['primary_account_num'].nunique():,}</b> accounts.",
            "figures": [biz_fig],
            "tables": [],
        })
        sheets.append({
            "name": "S2 Business Merchants",
            "df": biz_df,
            "currency_cols": ["Total Spend", "Avg Transaction"],
            "number_cols": ["Transactions", "Unique Accounts"],
        })

    # --- Personal Top Merchants ---
    if len(per) > 0:
        per_df = _top_merchants(per, merch_col, "amount_sum", top_n)
        per_fig = _merchant_bar(per_df, "Total Spend", "Top 25 Personal Merchants by Spend", color=COLORS["secondary"])
        sections.append({
            "heading": "Personal Account - Top Merchants",
            "narrative": f"<b>{len(per):,}</b> personal transactions across <b>{per['primary_account_num'].nunique():,}</b> accounts.",
            "figures": [per_fig],
            "tables": [],
        })
        sheets.append({
            "name": "S2 Personal Merchants",
            "df": per_df,
            "currency_cols": ["Total Spend", "Avg Transaction"],
            "number_cols": ["Transactions", "Unique Accounts"],
        })

    # --- Monthly Rank Movement ---
    if "year_month" in df.columns:
        rank_df, rank_fig = _monthly_rank_tracking(df, merch_col)
        if rank_df is not None:
            sections.append({
                "heading": "Monthly Merchant Rank Movement",
                "narrative": "Tracks how top merchants move up and down in spend rankings month-over-month. Stable leaders vs. volatile risers/fallers.",
                "figures": [rank_fig],
                "tables": [],
            })
            sheets.append({
                "name": "S2 Rank Tracking",
                "df": rank_df,
                "number_cols": list(rank_df.columns[1:]),
            })

    # --- Growth Leaders & Decliners ---
    if "year_month" in df.columns:
        growth_df, growth_fig, decline_fig = _growth_analysis(df, merch_col, config)
        if growth_df is not None:
            sections.append({
                "heading": "Growth Leaders & Decliners",
                "narrative": "Merchants with the largest absolute spend changes between the first and second half of the analysis period.",
                "figures": [growth_fig, decline_fig],
                "tables": [("Growth/Decline", growth_df.head(30))],
            })
            sheets.append({
                "name": "S2 Growth Leaders",
                "df": growth_df,
                "currency_cols": ["First Half Spend", "Second Half Spend", "Change"],
                "pct_cols": ["Change %"],
            })

    return {
        "title": "S2: Merchant Intelligence",
        "description": "Top merchants, MCC categories, business/personal splits, rank movement, growth leaders",
        "sections": sections,
        "sheets": sheets,
    }


# =============================================================================
# Core Analysis Functions
# =============================================================================

def _top_merchants(df, merch_col, sort_by, top_n):
    agg = df.groupby(merch_col).agg({
        "amount": ["sum", "count", "mean"],
        "primary_account_num": "nunique",
    }).round(2)
    agg.columns = ["Total Spend", "Transactions", "Avg Transaction", "Unique Accounts"]

    sort_map = {
        "amount_sum": "Total Spend",
        "txn_count": "Transactions",
        "unique_accounts": "Unique Accounts",
    }
    agg = agg.sort_values(sort_map.get(sort_by, "Total Spend"), ascending=False).head(top_n)
    agg = agg.reset_index().rename(columns={merch_col: "Merchant"})
    return agg


def _merchant_bar(df, value_col, title, y_col="Merchant", color=None, top_n=25):
    top = df.head(top_n).iloc[::-1]
    color = color or COLORS["primary"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top[value_col],
        y=top[y_col].str[:40],
        orientation="h",
        marker_color=color,
        text=top[value_col].apply(
            lambda v: format_currency(v) if value_col in ("Total Spend", "Avg Transaction") else f"{v:,.0f}"
        ),
        textposition="outside",
        textfont=dict(size=10),
    ))
    fig.update_layout(
        title=title,
        xaxis_title=value_col,
        yaxis=dict(automargin=True),
        height=max(500, top_n * 22),
        margin=dict(l=10),
    )
    if value_col in ("Total Spend", "Avg Transaction"):
        fig.update_xaxes(tickprefix="$", tickformat=",")
    else:
        fig.update_xaxes(tickformat=",")
    fig = apply_theme(fig)
    return fig


def _mcc_analysis(df, top_n):
    agg = df.groupby("mcc_code").agg({
        "amount": ["sum", "count", "mean"],
        "primary_account_num": "nunique",
        "merchant_name": "nunique",
    }).round(2)
    agg.columns = ["Total Spend", "Transactions", "Avg Transaction", "Unique Accounts", "Merchants"]
    agg = agg.sort_values("Total Spend", ascending=False).head(top_n)
    agg = agg.reset_index().rename(columns={"mcc_code": "MCC Code"})
    return agg


def _top_narrative(spend_df, metric_type, df):
    if spend_df.empty:
        return ""
    top = spend_df.iloc[0]
    total = df["amount"].sum()
    top_pct = (top["Total Spend"] / total * 100) if total > 0 else 0
    top_50_pct = (spend_df["Total Spend"].sum() / total * 100) if total > 0 else 0
    return (
        f"The #1 merchant is <b>{top['Merchant']}</b> with "
        f"{format_currency(top['Total Spend'])} in spend ({top_pct:.1f}% of total). "
        f"The top {len(spend_df)} merchants account for <b>{top_50_pct:.1f}%</b> of all spend "
        f"({format_currency(spend_df['Total Spend'].sum())} of {format_currency(total)})."
    )


# =============================================================================
# Monthly Rank Tracking
# =============================================================================

def _monthly_rank_tracking(df, merch_col):
    sorted_months = sorted(df["year_month"].unique())
    if len(sorted_months) < 3:
        return None, None

    monthly_ranks = {}
    for month in sorted_months:
        month_data = df[df["year_month"] == month]
        rankings = month_data.groupby(merch_col)["amount"].sum().sort_values(ascending=False)
        for rank, merchant in enumerate(rankings.index, 1):
            if merchant not in monthly_ranks:
                monthly_ranks[merchant] = {}
            monthly_ranks[merchant][str(month)] = rank

    # Get merchants in top 10 across most months
    rows = []
    for merchant, ranks in monthly_ranks.items():
        avg_rank = np.mean(list(ranks.values()))
        months_top_10 = sum(1 for r in ranks.values() if r <= 10)
        if months_top_10 >= len(sorted_months) // 2:
            row = {"Merchant": merchant, "Avg Rank": round(avg_rank, 1)}
            for month in sorted_months:
                row[str(month)] = ranks.get(str(month), None)
            rows.append(row)

    if not rows:
        return None, None

    rank_df = pd.DataFrame(rows).sort_values("Avg Rank").head(15)

    # Chart: line chart of rank trajectory (inverted y-axis)
    fig = go.Figure()
    month_strs = [str(m) for m in sorted_months]
    for _, row in rank_df.iterrows():
        ranks = [row.get(m) for m in month_strs]
        fig.add_trace(go.Scatter(
            x=month_strs,
            y=ranks,
            mode="lines+markers",
            name=str(row["Merchant"])[:30],
            line=dict(width=2),
            marker=dict(size=6),
        ))

    fig.update_layout(
        title="Top Merchant Rank Movement (Lower = Better)",
        yaxis=dict(title="Rank", autorange="reversed", dtick=1),
        xaxis_title="Month",
        height=600,
        legend=dict(font=dict(size=10)),
        hovermode="x unified",
    )
    fig = apply_theme(fig)

    return rank_df, fig


# =============================================================================
# Growth Leaders & Decliners
# =============================================================================

def _growth_analysis(df, merch_col, config):
    sorted_months = sorted(df["year_month"].unique())
    if len(sorted_months) < 4:
        return None, None, None

    mid = len(sorted_months) // 2
    first_half = sorted_months[:mid]
    second_half = sorted_months[mid:]

    h1 = df[df["year_month"].isin(first_half)].groupby(merch_col)["amount"].sum()
    h2 = df[df["year_month"].isin(second_half)].groupby(merch_col)["amount"].sum()

    growth = pd.DataFrame({"First Half Spend": h1, "Second Half Spend": h2}).fillna(0)
    growth["Change"] = growth["Second Half Spend"] - growth["First Half Spend"]
    growth["Change %"] = np.where(
        growth["First Half Spend"] > 0,
        (growth["Change"] / growth["First Half Spend"] * 100).round(1),
        0,
    )

    min_threshold = config.get("growth_min_threshold", 1000)
    growth = growth[
        (growth["First Half Spend"] >= min_threshold) | (growth["Second Half Spend"] >= min_threshold)
    ]
    growth = growth.sort_values("Change", ascending=False)
    growth = growth.reset_index().rename(columns={merch_col: "Merchant"})

    # Growth chart (top 15)
    top_growth = growth.head(15).iloc[::-1]
    growth_fig = go.Figure()
    growth_fig.add_trace(go.Bar(
        x=top_growth["Change"],
        y=top_growth["Merchant"].str[:35],
        orientation="h",
        marker_color=COLORS["positive"],
        text=top_growth["Change"].apply(lambda v: f"+{format_currency(v)}"),
        textposition="outside",
    ))
    growth_fig.update_layout(
        title="Top 15 Growth Leaders (Absolute Spend Increase)",
        xaxis_title="Spend Change ($)",
        xaxis_tickprefix="$",
        xaxis_tickformat=",",
        height=500,
    )
    growth_fig = apply_theme(growth_fig)

    # Decline chart (bottom 15)
    top_decline = growth.tail(15)
    decline_fig = go.Figure()
    decline_fig.add_trace(go.Bar(
        x=top_decline["Change"],
        y=top_decline["Merchant"].str[:35],
        orientation="h",
        marker_color=COLORS["negative"],
        text=top_decline["Change"].apply(lambda v: format_currency(v)),
        textposition="outside",
    ))
    decline_fig.update_layout(
        title="Top 15 Decliners (Absolute Spend Decrease)",
        xaxis_title="Spend Change ($)",
        xaxis_tickprefix="$",
        xaxis_tickformat=",",
        height=500,
    )
    decline_fig = apply_theme(decline_fig)

    return growth, growth_fig, decline_fig
