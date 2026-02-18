# v4_s5_demographics.py
# Storyline 5: Demographics & Branch Performance
# =============================================================================
# Generation mix, tenure analysis, branch performance, age-spend patterns

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from v4_themes import (
    COLORS, CATEGORY_PALETTE, GENERATION_COLORS,
    apply_theme, format_currency, format_pct,
    horizontal_bar, donut_chart, grouped_bar, scatter_plot, heatmap,
)

# Named constants for tenure bucket boundaries
TENURE_BINS = [0, 1, 3, 5, 10, float("inf")]
TENURE_LABELS = ["0-1 yr", "1-3 yrs", "3-5 yrs", "5-10 yrs", "10+ yrs"]
TOP_BRANCHES = 20
HEATMAP_BRANCHES = 15


def run(ctx: dict) -> dict:
    """Run Demographics & Branch Performance analyses."""
    df = ctx["combined_df"]
    odd = ctx["odd_df"]

    sections = []
    sheets = []

    # --- 1. Generation Distribution ---
    if "generation" in odd.columns:
        gen_dist, gen_spend, figs = _generation_distribution(odd, df)
        sections.append({
            "heading": "Generation Distribution",
            "narrative": _generation_narrative(gen_dist, gen_spend),
            "figures": figs,
            "tables": [("Generation Distribution", gen_dist)],
        })
        sheets.append({
            "name": "S5 Gen Distribution",
            "df": gen_dist,
            "currency_cols": [],
            "pct_cols": ["% of Accounts"],
            "number_cols": ["Accounts"],
        })

    # --- 2. Generation Spend Profiles ---
    if "generation" in df.columns:
        profile_df, profile_fig = _generation_spend_profiles(df)
        sections.append({
            "heading": "Generation Spend Profiles",
            "narrative": _spend_profile_narrative(profile_df),
            "figures": [profile_fig],
            "tables": [("Generation Spend Profiles", profile_df)],
        })
        sheets.append({
            "name": "S5 Gen Spend Profiles",
            "df": profile_df,
            "currency_cols": ["Total Spend", "Avg Transaction"],
            "pct_cols": [],
            "number_cols": ["Transactions", "Unique Merchants"],
        })

    # --- 3. Account Tenure Analysis ---
    if "tenure_years" in odd.columns:
        tenure_df, tenure_figs = _tenure_analysis(odd, df)
        sections.append({
            "heading": "Account Tenure Analysis",
            "narrative": _tenure_narrative(tenure_df),
            "figures": tenure_figs,
            "tables": [("Tenure Buckets", tenure_df)],
        })
        sheets.append({
            "name": "S5 Tenure Analysis",
            "df": tenure_df,
            "currency_cols": ["Avg Spend per Account"],
            "pct_cols": ["% of Accounts"],
            "number_cols": ["Accounts"],
        })

    # --- 4. Branch Performance Dashboard ---
    if "Branch" in df.columns:
        branch_df, branch_fig = _branch_performance(df, odd)
        if branch_df is not None:
            sections.append({
                "heading": "Branch Performance Dashboard",
                "narrative": _branch_narrative(branch_df),
                "figures": [branch_fig],
                "tables": [("Top Branches", branch_df.head(TOP_BRANCHES))],
            })
            sheets.append({
                "name": "S5 Branch Performance",
                "df": branch_df,
                "currency_cols": ["Total Spend", "Avg Spend/Acct", "Avg Balance"],
                "pct_cols": [],
                "number_cols": ["Accounts", "Transactions"],
            })

    # --- 5. Branch-Generation Heatmap ---
    if "Branch" in df.columns and "generation" in df.columns:
        hm_df, hm_fig = _branch_generation_heatmap(df)
        if hm_df is not None:
            sections.append({
                "heading": "Branch-Generation Heatmap",
                "narrative": (
                    "Cross-tabulation of total spend by branch and generation. "
                    "Darker cells indicate higher concentration of spend, revealing "
                    "which branches serve which demographic segments."
                ),
                "figures": [hm_fig],
                "tables": [("Branch x Generation Spend", hm_df.reset_index())],
            })
            sheets.append({
                "name": "S5 Branch Gen Heatmap",
                "df": hm_df.reset_index(),
                "currency_cols": list(hm_df.columns),
                "pct_cols": [],
                "number_cols": [],
            })

    # --- 6. Age vs Spend Scatter ---
    if "Account Holder Age" in df.columns:
        scatter_df, scatter_fig = _age_spend_scatter(df)
        if scatter_df is not None:
            sections.append({
                "heading": "Age vs Spend Analysis",
                "narrative": _age_spend_narrative(scatter_df),
                "figures": [scatter_fig],
                "tables": [],
            })

    # --- 7. Product Mix ---
    if "Prod Desc" in odd.columns:
        prod_df, prod_figs = _product_mix(odd, df)
        if prod_df is not None:
            sections.append({
                "heading": "Product Mix",
                "narrative": _product_narrative(prod_df),
                "figures": prod_figs,
                "tables": [("Product Mix", prod_df)],
            })
            sheets.append({
                "name": "S5 Product Mix",
                "df": prod_df,
                "currency_cols": ["Avg Spend/Acct"],
                "pct_cols": ["% of Accounts"],
                "number_cols": ["Accounts"],
            })

    return {
        "title": "S5: Demographics & Branch Performance",
        "description": (
            "Generation mix, tenure analysis, branch performance, "
            "age-spend patterns, product mix"
        ),
        "sections": sections,
        "sheets": sheets,
    }


# =============================================================================
# 1. Generation Distribution
# =============================================================================

def _generation_distribution(odd, df):
    gen_counts = odd["generation"].value_counts().reset_index()
    gen_counts.columns = ["Generation", "Accounts"]
    total = gen_counts["Accounts"].sum()
    gen_counts["% of Accounts"] = (
        (gen_counts["Accounts"] / total * 100).round(1) if total > 0 else 0
    )

    gen_colors = [GENERATION_COLORS.get(g, COLORS["neutral"]) for g in gen_counts["Generation"]]
    donut_fig = donut_chart(
        gen_counts["Generation"], gen_counts["Accounts"],
        "Account Distribution by Generation", colors=gen_colors,
    )

    # Avg spend per account by generation
    acct_spend = df.groupby("generation").agg(
        total=("amount", "sum"),
        accounts=("primary_account_num", "nunique"),
    )
    acct_spend["Avg Spend/Acct"] = np.where(
        acct_spend["accounts"] > 0,
        acct_spend["total"] / acct_spend["accounts"],
        0,
    )
    acct_spend = acct_spend.reset_index().sort_values("Avg Spend/Acct", ascending=False)

    bar_colors = [GENERATION_COLORS.get(g, COLORS["neutral"]) for g in acct_spend["generation"]]
    bar_fig = go.Figure(go.Bar(
        x=acct_spend["generation"],
        y=acct_spend["Avg Spend/Acct"],
        marker_color=bar_colors,
        text=acct_spend["Avg Spend/Acct"].apply(format_currency),
        textposition="outside",
    ))
    bar_fig.update_layout(
        title="Average Spend per Account by Generation",
        xaxis_title="Generation",
        yaxis_title="Avg Spend ($)",
        yaxis_tickprefix="$", yaxis_tickformat=",",
        showlegend=False,
    )
    bar_fig = apply_theme(bar_fig)

    return gen_counts, acct_spend, [donut_fig, bar_fig]


def _generation_narrative(gen_dist, gen_spend):
    if gen_dist.empty:
        return ""
    top_acct = gen_dist.iloc[0]
    top_spend = gen_spend.iloc[0]
    return (
        f"<b>{top_acct['Generation']}</b> dominates account counts with "
        f"{int(top_acct['Accounts']):,} accounts ({top_acct['% of Accounts']}%). "
        f"However, <b>{top_spend['generation']}</b> leads in average spend per account "
        f"at {format_currency(top_spend['Avg Spend/Acct'])}."
    )


# =============================================================================
# 2. Generation Spend Profiles
# =============================================================================

def _generation_spend_profiles(df):
    profile = df.groupby("generation").agg(
        total_spend=("amount", "sum"),
        avg_txn=("amount", "mean"),
        txn_count=("amount", "count"),
        unique_merchants=("merchant_consolidated", "nunique"),
    ).round(2).reset_index()
    profile.columns = [
        "Generation", "Total Spend", "Avg Transaction",
        "Transactions", "Unique Merchants",
    ]

    # Normalize for grouped bar: index by generation
    fig = grouped_bar(
        profile, "Generation",
        ["Total Spend", "Transactions"],
        "Generation Spend Comparison",
        colors=[COLORS["primary"], COLORS["secondary"]],
    )
    return profile, fig


def _spend_profile_narrative(profile_df):
    if profile_df.empty:
        return ""
    top_spender = profile_df.loc[profile_df["Total Spend"].idxmax()]
    top_txn = profile_df.loc[profile_df["Avg Transaction"].idxmax()]
    return (
        f"<b>{top_spender['Generation']}</b> accounts for the most total spend "
        f"({format_currency(top_spender['Total Spend'])}), while "
        f"<b>{top_txn['Generation']}</b> has the highest average transaction "
        f"({format_currency(top_txn['Avg Transaction'])})."
    )


# =============================================================================
# 3. Account Tenure Analysis
# =============================================================================

def _tenure_analysis(odd, df):
    odd = odd.copy()
    tenure = odd["tenure_years"].dropna()
    if tenure.empty:
        return pd.DataFrame(), []

    odd["Tenure Bucket"] = pd.cut(
        odd["tenure_years"], bins=TENURE_BINS, labels=TENURE_LABELS, right=False,
    )

    bucket_stats = odd.groupby("Tenure Bucket", observed=True).agg(
        accounts=("primary_account_num", "nunique"),
    ).reset_index()
    total_accts = bucket_stats["accounts"].sum()
    bucket_stats["% of Accounts"] = np.where(
        total_accts > 0,
        (bucket_stats["accounts"] / total_accts * 100).round(1),
        0,
    )
    bucket_stats.columns = ["Tenure Bucket", "Accounts", "% of Accounts"]

    # Avg spend per account by tenure bucket
    df_t = df.copy()
    if "tenure_years" in df_t.columns:
        df_t["Tenure Bucket"] = pd.cut(
            df_t["tenure_years"], bins=TENURE_BINS, labels=TENURE_LABELS, right=False,
        )
        spend_by_bucket = df_t.groupby("Tenure Bucket", observed=True).agg(
            total=("amount", "sum"),
            accts=("primary_account_num", "nunique"),
        ).reset_index()
        spend_by_bucket["Avg Spend per Account"] = np.where(
            spend_by_bucket["accts"] > 0,
            (spend_by_bucket["total"] / spend_by_bucket["accts"]).round(2),
            0,
        )
        bucket_stats = bucket_stats.merge(
            spend_by_bucket[["Tenure Bucket", "Avg Spend per Account"]],
            on="Tenure Bucket", how="left",
        )
    else:
        bucket_stats["Avg Spend per Account"] = 0

    # Distribution bar chart
    dist_fig = go.Figure(go.Bar(
        x=bucket_stats["Tenure Bucket"].astype(str),
        y=bucket_stats["Accounts"],
        marker_color=COLORS["primary"],
        text=[f"{a:,}" for a in bucket_stats["Accounts"]],
        textposition="outside",
    ))
    dist_fig.update_layout(
        title="Account Distribution by Tenure",
        xaxis_title="Tenure", yaxis_title="Accounts",
        yaxis_tickformat=",", showlegend=False,
    )
    dist_fig = apply_theme(dist_fig)

    # Spend by tenure bar
    spend_fig = go.Figure(go.Bar(
        x=bucket_stats["Tenure Bucket"].astype(str),
        y=bucket_stats["Avg Spend per Account"],
        marker_color=COLORS["secondary"],
        text=bucket_stats["Avg Spend per Account"].apply(format_currency),
        textposition="outside",
    ))
    spend_fig.update_layout(
        title="Average Spend per Account by Tenure",
        xaxis_title="Tenure", yaxis_title="Avg Spend ($)",
        yaxis_tickprefix="$", yaxis_tickformat=",", showlegend=False,
    )
    spend_fig = apply_theme(spend_fig)

    return bucket_stats, [dist_fig, spend_fig]


def _tenure_narrative(tenure_df):
    if tenure_df.empty:
        return ""
    top_bucket = tenure_df.loc[tenure_df["Accounts"].idxmax()]
    if "Avg Spend per Account" in tenure_df.columns:
        top_spend = tenure_df.loc[tenure_df["Avg Spend per Account"].idxmax()]
        return (
            f"The largest tenure cohort is <b>{top_bucket['Tenure Bucket']}</b> "
            f"with {int(top_bucket['Accounts']):,} accounts "
            f"({top_bucket['% of Accounts']}%). "
            f"The <b>{top_spend['Tenure Bucket']}</b> cohort shows the highest "
            f"average spend per account at "
            f"{format_currency(top_spend['Avg Spend per Account'])}."
        )
    return (
        f"The largest tenure cohort is <b>{top_bucket['Tenure Bucket']}</b> "
        f"with {int(top_bucket['Accounts']):,} accounts."
    )


# =============================================================================
# 4. Branch Performance Dashboard
# =============================================================================

def _branch_performance(df, odd):
    branch_agg = df.groupby("Branch").agg(
        total_spend=("amount", "sum"),
        txn_count=("amount", "count"),
        accounts=("primary_account_num", "nunique"),
    ).reset_index()
    branch_agg["Avg Spend/Acct"] = np.where(
        branch_agg["accounts"] > 0,
        (branch_agg["total_spend"] / branch_agg["accounts"]).round(2),
        0,
    )

    # Merge average balance from ODD if available
    if odd is not None and "Branch" in odd.columns and "Avg Bal" in odd.columns:
        bal = odd.groupby("Branch")["Avg Bal"].mean().reset_index()
        bal.columns = ["Branch", "Avg Balance"]
        branch_agg = branch_agg.merge(bal, on="Branch", how="left")
    else:
        branch_agg["Avg Balance"] = np.nan

    branch_agg.columns = [
        "Branch", "Total Spend", "Transactions",
        "Accounts", "Avg Spend/Acct", "Avg Balance",
    ]
    branch_agg = branch_agg.sort_values("Total Spend", ascending=False)
    branch_agg = branch_agg.reset_index(drop=True)

    if branch_agg.empty:
        return None, None

    fig = horizontal_bar(
        branch_agg.head(TOP_BRANCHES), "Total Spend", "Branch",
        f"Top {TOP_BRANCHES} Branches by Total Spend",
    )
    return branch_agg, fig


def _branch_narrative(branch_df):
    if branch_df.empty:
        return ""
    top = branch_df.iloc[0]
    total_spend = branch_df["Total Spend"].sum()
    top_pct = (top["Total Spend"] / total_spend * 100) if total_spend > 0 else 0
    bottom = branch_df.iloc[-1] if len(branch_df) > 1 else top
    return (
        f"The top-performing branch is <b>{top['Branch']}</b> with "
        f"{format_currency(top['Total Spend'])} in spend ({top_pct:.1f}% of total) "
        f"across {int(top['Accounts']):,} accounts. "
        f"The lowest-volume branch is <b>{bottom['Branch']}</b> with "
        f"{format_currency(bottom['Total Spend'])}."
    )


# =============================================================================
# 5. Branch-Generation Heatmap
# =============================================================================

def _branch_generation_heatmap(df):
    top_branches = (
        df.groupby("Branch")["amount"].sum()
        .nlargest(HEATMAP_BRANCHES).index
    )
    subset = df[df["Branch"].isin(top_branches)]
    if subset.empty:
        return None, None

    pivot = subset.pivot_table(
        values="amount", index="Branch", columns="generation",
        aggfunc="sum", fill_value=0,
    ).round(0)

    # Order generations consistently
    gen_order = [g for g in GENERATION_COLORS if g in pivot.columns]
    extra = [c for c in pivot.columns if c not in gen_order]
    pivot = pivot[gen_order + extra]

    fig = heatmap(pivot, "Branch x Generation Spend Heatmap", fmt=",.0f")
    return pivot, fig


# =============================================================================
# 6. Age vs Spend Scatter
# =============================================================================

def _age_spend_scatter(df):
    acct_agg = df.groupby("primary_account_num").agg(
        total_spend=("amount", "sum"),
        age=("Account Holder Age", "first"),
        tier=("balance_tier", "first"),
    ).reset_index()
    acct_agg = acct_agg.dropna(subset=["age", "total_spend"])
    acct_agg = acct_agg[acct_agg["age"] > 0]
    if acct_agg.empty:
        return None, None

    acct_agg.columns = ["Account", "Total Spend", "Account Holder Age", "Balance Tier"]
    fig = scatter_plot(
        acct_agg, "Account Holder Age", "Total Spend",
        "Account Holder Age vs Total Spend",
        color_col="Balance Tier",
    )
    return acct_agg, fig


def _age_spend_narrative(scatter_df):
    if scatter_df.empty:
        return ""
    median_age = scatter_df["Account Holder Age"].median()
    median_spend = scatter_df["Total Spend"].median()
    return (
        f"The median account holder age is <b>{median_age:.0f}</b> with a median "
        f"total spend of <b>{format_currency(median_spend)}</b>. "
        f"The scatter reveals how spending intensity varies across the age spectrum, "
        f"with color encoding by balance tier."
    )


# =============================================================================
# 7. Product Mix
# =============================================================================

def _product_mix(odd, df):
    prod_counts = odd["Prod Desc"].value_counts().reset_index()
    prod_counts.columns = ["Product", "Accounts"]
    if prod_counts.empty:
        return None, []

    total = prod_counts["Accounts"].sum()
    prod_counts["% of Accounts"] = (
        (prod_counts["Accounts"] / total * 100).round(1) if total > 0 else 0
    )

    donut_fig = donut_chart(
        prod_counts["Product"], prod_counts["Accounts"],
        "Account Distribution by Product Type",
    )

    # Avg spend per account by product
    if "Prod Desc" in df.columns:
        prod_spend = df.groupby("Prod Desc").agg(
            total=("amount", "sum"),
            accts=("primary_account_num", "nunique"),
        ).reset_index()
        prod_spend["Avg Spend/Acct"] = np.where(
            prod_spend["accts"] > 0,
            (prod_spend["total"] / prod_spend["accts"]).round(2),
            0,
        )
        prod_spend = prod_spend.sort_values("Avg Spend/Acct", ascending=False)

        bar_fig = go.Figure(go.Bar(
            x=prod_spend["Prod Desc"].str[:30],
            y=prod_spend["Avg Spend/Acct"],
            marker_color=COLORS["accent"],
            text=prod_spend["Avg Spend/Acct"].apply(format_currency),
            textposition="outside",
        ))
        bar_fig.update_layout(
            title="Average Spend per Account by Product",
            xaxis_title="Product", yaxis_title="Avg Spend ($)",
            yaxis_tickprefix="$", yaxis_tickformat=",", showlegend=False,
        )
        bar_fig = apply_theme(bar_fig)

        prod_counts = prod_counts.merge(
            prod_spend[["Prod Desc", "Avg Spend/Acct"]].rename(
                columns={"Prod Desc": "Product"}
            ),
            on="Product", how="left",
        )
        return prod_counts, [donut_fig, bar_fig]

    return prod_counts, [donut_fig]


def _product_narrative(prod_df):
    if prod_df.empty:
        return ""
    top = prod_df.iloc[0]
    narrative = (
        f"The most common product is <b>{top['Product']}</b> with "
        f"{int(top['Accounts']):,} accounts ({top['% of Accounts']}%)."
    )
    if "Avg Spend/Acct" in prod_df.columns:
        top_spend = prod_df.loc[prod_df["Avg Spend/Acct"].idxmax()]
        narrative += (
            f" <b>{top_spend['Product']}</b> drives the highest average spend "
            f"per account at {format_currency(top_spend['Avg Spend/Acct'])}."
        )
    return narrative
