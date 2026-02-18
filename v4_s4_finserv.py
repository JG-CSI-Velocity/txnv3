# v4_s4_finserv.py
# Storyline 4: Financial Services Intelligence
# =============================================================================
# FinServ detection, category summary, top providers, generational profile,
# cross-category overlap analysis

import numpy as np
import plotly.graph_objects as go
from v4_themes import (
    CATEGORY_PALETTE,
    COLORS,
    apply_theme,
    donut_chart,
    format_currency,
    grouped_bar,
    horizontal_bar,
    insight_title,
    stacked_bar,
)

# Display-friendly names for config keys
_CATEGORY_LABELS = {
    "auto_loans": "Auto Loans",
    "investment_brokerage": "Investment/Brokerage",
    "mortgage_heloc": "Mortgage/HELOC",
    "personal_loans": "Personal Loans",
    "credit_cards": "Credit Cards",
    "student_loans": "Student Loans",
    "business_loans": "Business Loans",
    "treasury_bonds": "Treasury/Bonds",
}


def run(ctx: dict) -> dict:
    """Run Financial Services Intelligence analyses."""
    df = ctx["combined_df"].copy()
    config = ctx["config"]
    finserv_config = config.get("financial_services", {})

    sections = []
    sheets = []
    merch_col = (
        "merchant_consolidated" if "merchant_consolidated" in df.columns else "merchant_name"
    )

    # --- 1. Detection ---
    df = _detect_finserv(df, merch_col, finserv_config)
    fs_df = df[df["finserv_category"].notna()].copy()

    if fs_df.empty:
        sections.append(
            {
                "heading": "Financial Services Detection",
                "narrative": (
                    "No financial services transactions were detected in this dataset. "
                    "This may indicate that the institution's members are not using "
                    "external financial service providers through their debit cards, "
                    "or that the configured patterns did not match any merchants."
                ),
                "figures": [],
                "tables": [],
            }
        )
        return {
            "title": "S4: Financial Services Intelligence",
            "description": "No financial services transactions detected",
            "sections": sections,
            "sheets": sheets,
        }

    # --- 2. Summary ---
    summary_section, summary_sheet = _finserv_summary(df, fs_df, merch_col)
    sections.append(summary_section)
    sheets.append(summary_sheet)

    # --- 3. Top Providers ---
    provider_section, provider_sheet = _top_providers(fs_df, merch_col)
    sections.append(provider_section)
    sheets.append(provider_sheet)

    # --- 4. Category Deep Dive ---
    category_section, category_sheet = _category_deep_dive(fs_df, merch_col)
    sections.append(category_section)
    sheets.append(category_sheet)

    # --- 5. Generation Profile ---
    if "generation" in df.columns:
        gen_section = _generation_profile(fs_df)
        if gen_section is not None:
            sections.append(gen_section)

    # --- 6. Cross-Category Analysis ---
    cross_section, cross_sheet = _cross_category_analysis(fs_df)
    sections.append(cross_section)
    if cross_sheet is not None:
        sheets.append(cross_sheet)

    return {
        "title": "S4: Financial Services Intelligence",
        "description": (
            "External financial service usage: detection, category breakdown, "
            "top providers, generational profile, cross-category overlap"
        ),
        "sections": sections,
        "sheets": sheets,
    }


# =============================================================================
# Detection
# =============================================================================


def _detect_finserv(df, merch_col, finserv_config):
    """Tag each transaction with its financial services category (if any).

    Uses substring matching against uppercased merchant names.
    First match wins; rows with no match get NaN.
    """
    df["finserv_category"] = np.nan
    merchant_upper = df[merch_col].str.upper().fillna("")

    for config_key, patterns in finserv_config.items():
        if not patterns:
            continue
        label = _CATEGORY_LABELS.get(config_key, config_key.replace("_", " ").title())
        mask = merchant_upper.apply(
            lambda m: any(p in m for p in (pat.upper() for pat in patterns))
        )
        # Only tag rows not already tagged (first match wins)
        assign_mask = mask & df["finserv_category"].isna()
        df.loc[assign_mask, "finserv_category"] = label

    return df


# =============================================================================
# Analysis 2: Financial Services Summary
# =============================================================================


def _finserv_summary(df, fs_df, merch_col):
    """Overall FinServ summary with donut chart by category."""
    total_spend = df["amount"].sum()
    fs_spend = fs_df["amount"].sum()
    fs_pct = (fs_spend / total_spend * 100) if total_spend > 0 else 0
    fs_accounts = fs_df["primary_account_num"].nunique()
    fs_txns = len(fs_df)
    total_accounts = df["primary_account_num"].nunique()
    acct_pct = (fs_accounts / total_accounts * 100) if total_accounts > 0 else 0

    # Category breakdown
    cat_agg = (
        fs_df.groupby("finserv_category")
        .agg(
            Total_Spend=("amount", "sum"),
            Transactions=("amount", "count"),
            Unique_Accounts=("primary_account_num", "nunique"),
        )
        .sort_values("Total_Spend", ascending=False)
        .reset_index()
        .rename(
            columns={
                "finserv_category": "Category",
                "Total_Spend": "Total Spend",
                "Unique_Accounts": "Unique Accounts",
            }
        )
    )
    cat_agg["Avg Transaction"] = (cat_agg["Total Spend"] / cat_agg["Transactions"]).round(2)
    cat_agg["% of FinServ Spend"] = (cat_agg["Total Spend"] / fs_spend * 100).round(1)

    # Donut chart
    fig = donut_chart(
        labels=cat_agg["Category"].tolist(),
        values=cat_agg["Total Spend"].tolist(),
        title="Financial Services Spend by Category",
    )
    fig.update_layout(
        title=insight_title(
            "Financial Services Spend by Category",
            f"{format_currency(fs_spend)} total across {len(cat_agg)} categories",
        )
    )
    fig = apply_theme(fig)

    # Narrative
    top_cat = cat_agg.iloc[0] if not cat_agg.empty else None
    top_cat_text = (
        f"The largest category is <b>{top_cat['Category']}</b> at "
        f"{format_currency(top_cat['Total Spend'])} "
        f"({top_cat['% of FinServ Spend']:.1f}% of FinServ spend). "
        if top_cat is not None
        else ""
    )
    narrative = (
        f"Detected <b>{format_currency(fs_spend)}</b> in external financial services "
        f"spend ({fs_pct:.1f}% of total portfolio spend) across "
        f"<b>{fs_accounts:,}</b> accounts ({acct_pct:.1f}% of all accounts) "
        f"and <b>{fs_txns:,}</b> transactions. {top_cat_text}"
    )

    section = {
        "heading": "Financial Services Summary",
        "narrative": narrative,
        "figures": [fig],
        "tables": [("FinServ Category Summary", cat_agg)],
    }
    sheet = {
        "name": "S4 FinServ Summary",
        "df": cat_agg,
        "currency_cols": ["Total Spend", "Avg Transaction"],
        "pct_cols": ["% of FinServ Spend"],
        "number_cols": ["Transactions", "Unique Accounts"],
    }
    return section, sheet


# =============================================================================
# Analysis 3: Top Financial Service Providers
# =============================================================================


def _top_providers(fs_df, merch_col):
    """Top 20 individual FinServ merchants by spend."""
    top_n = 20
    provider_agg = (
        fs_df.groupby([merch_col, "finserv_category"])
        .agg(
            Total_Spend=("amount", "sum"),
            Transactions=("amount", "count"),
            Unique_Accounts=("primary_account_num", "nunique"),
        )
        .sort_values("Total_Spend", ascending=False)
        .head(top_n)
        .reset_index()
        .rename(
            columns={
                merch_col: "Merchant",
                "finserv_category": "Category",
                "Total_Spend": "Total Spend",
                "Unique_Accounts": "Unique Accounts",
            }
        )
    )
    provider_agg["Avg Transaction"] = (
        provider_agg["Total Spend"] / provider_agg["Transactions"]
    ).round(2)

    fig = horizontal_bar(
        provider_agg,
        x_col="Total Spend",
        y_col="Merchant",
        title="Top 20 Financial Service Providers by Spend",
        top_n=top_n,
        value_format="${:,.0f}",
        color=COLORS["secondary"],
    )
    fig.update_layout(
        title=insight_title(
            "Top Financial Service Providers",
            f"Top {min(top_n, len(provider_agg))} by total spend",
        )
    )

    top = provider_agg.iloc[0] if not provider_agg.empty else None
    narrative = ""
    if top is not None:
        narrative = (
            f"The top financial service provider is <b>{top['Merchant']}</b> "
            f"({top['Category']}) with {format_currency(top['Total Spend'])} "
            f"across <b>{int(top['Unique Accounts']):,}</b> accounts."
        )

    section = {
        "heading": "Top Financial Service Providers",
        "narrative": narrative,
        "figures": [fig],
        "tables": [("Top FinServ Providers", provider_agg)],
    }
    sheet = {
        "name": "S4 Top Providers",
        "df": provider_agg,
        "currency_cols": ["Total Spend", "Avg Transaction"],
        "pct_cols": [],
        "number_cols": ["Transactions", "Unique Accounts"],
    }
    return section, sheet


# =============================================================================
# Analysis 4: Category Deep Dive
# =============================================================================


def _category_deep_dive(fs_df, merch_col):
    """Grouped bar showing spend and unique accounts by category."""
    cat_agg = (
        fs_df.groupby("finserv_category")
        .agg(
            Total_Spend=("amount", "sum"),
            Transactions=("amount", "count"),
            Unique_Accounts=("primary_account_num", "nunique"),
            Unique_Merchants=(merch_col, "nunique"),
        )
        .sort_values("Total_Spend", ascending=False)
        .reset_index()
        .rename(
            columns={
                "finserv_category": "Category",
                "Total_Spend": "Total Spend",
                "Unique_Accounts": "Unique Accounts",
                "Unique_Merchants": "Unique Merchants",
            }
        )
    )
    cat_agg["Avg Spend/Account"] = np.where(
        cat_agg["Unique Accounts"] > 0,
        (cat_agg["Total Spend"] / cat_agg["Unique Accounts"]).round(2),
        0,
    )

    fig = grouped_bar(
        cat_agg,
        x_col="Category",
        y_cols=["Total Spend", "Unique Accounts"],
        title="Financial Services: Spend vs Account Penetration",
        colors=[COLORS["primary"], COLORS["accent"]],
    )
    fig.update_layout(
        title=insight_title(
            "Spend vs Account Penetration by Category",
            "Which categories drive volume vs breadth?",
        )
    )

    # Identify highest avg spend category
    if not cat_agg.empty:
        top_avg = cat_agg.loc[cat_agg["Avg Spend/Account"].idxmax()]
        top_pen = cat_agg.loc[cat_agg["Unique Accounts"].idxmax()]
        narrative = (
            f"<b>{top_pen['Category']}</b> has the widest account penetration "
            f"({int(top_pen['Unique Accounts']):,} accounts), while "
            f"<b>{top_avg['Category']}</b> has the highest average spend per "
            f"account ({format_currency(top_avg['Avg Spend/Account'])})."
        )
    else:
        narrative = ""

    section = {
        "heading": "Category Deep Dive",
        "narrative": narrative,
        "figures": [fig],
        "tables": [("Category Detail", cat_agg)],
    }
    sheet = {
        "name": "S4 Category Detail",
        "df": cat_agg,
        "currency_cols": ["Total Spend", "Avg Spend/Account"],
        "pct_cols": [],
        "number_cols": ["Transactions", "Unique Accounts", "Unique Merchants"],
    }
    return section, sheet


# =============================================================================
# Analysis 5: Generation Profile
# =============================================================================


def _generation_profile(fs_df):
    """Stacked bar (percentage mode) of FinServ categories by generation."""
    gen_cat = (
        fs_df.groupby(["generation", "finserv_category"])["amount"].sum().unstack(fill_value=0)
    )

    if gen_cat.empty or len(gen_cat) < 2:
        return None

    # Order generations consistently
    gen_order = ["Gen Z", "Millennial", "Gen X", "Boomer", "Silent"]
    gen_cat = gen_cat.reindex([g for g in gen_order if g in gen_cat.index])

    if gen_cat.empty:
        return None

    gen_cat = gen_cat.reset_index().rename(columns={"generation": "Generation"})
    category_cols = [c for c in gen_cat.columns if c != "Generation"]

    # Build color list aligned with category columns
    chart_colors = CATEGORY_PALETTE[: len(category_cols)]

    fig = stacked_bar(
        gen_cat,
        x_col="Generation",
        y_cols=category_cols,
        title="Financial Services Mix by Generation",
        colors=chart_colors,
        as_percentage=True,
    )
    fig.update_layout(
        title=insight_title(
            "Financial Services Mix by Generation",
            "How do FinServ preferences differ across age cohorts?",
        )
    )

    # Build narrative from the data
    narratives = []
    for gen in gen_cat["Generation"]:
        row = gen_cat[gen_cat["Generation"] == gen][category_cols]
        if row.empty:
            continue
        row_vals = row.iloc[0]
        total = row_vals.sum()
        if total <= 0:
            continue
        top_cat = row_vals.idxmax()
        top_pct = row_vals.max() / total * 100
        narratives.append(f"{gen}: {top_cat} ({top_pct:.0f}%)")

    narrative = (
        "Dominant FinServ category by generation -- " + "; ".join(narratives) + "."
        if narratives
        else ""
    )

    return {
        "heading": "Generational FinServ Profile",
        "narrative": narrative,
        "figures": [fig],
        "tables": [],
    }


# =============================================================================
# Analysis 6: Cross-Category Analysis
# =============================================================================


def _cross_category_analysis(fs_df):
    """How many accounts use multiple FinServ categories?"""
    acct_cats = (
        fs_df.groupby("primary_account_num")["finserv_category"]
        .nunique()
        .reset_index()
        .rename(columns={"finserv_category": "Categories Used"})
    )

    dist = acct_cats["Categories Used"].value_counts().sort_index().reset_index()
    dist.columns = ["Categories Used", "Accounts"]
    dist["% of FinServ Accounts"] = (dist["Accounts"] / dist["Accounts"].sum() * 100).round(1)

    multi_count = int(acct_cats[acct_cats["Categories Used"] >= 2].shape[0])
    total_fs_accounts = int(acct_cats.shape[0])
    multi_pct = (multi_count / total_fs_accounts * 100) if total_fs_accounts > 0 else 0

    # Build a bar chart of distribution
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=dist["Categories Used"],
            y=dist["Accounts"],
            marker_color=COLORS["accent"],
            text=[
                f"{a:,}<br>({p}%)" for a, p in zip(dist["Accounts"], dist["% of FinServ Accounts"])
            ],
            textposition="outside",
            textfont=dict(size=11),
        )
    )
    fig.update_layout(
        xaxis_title="Number of FinServ Categories Used",
        yaxis_title="Accounts",
        yaxis_tickformat=",",
        showlegend=False,
        height=450,
    )
    fig.update_layout(
        title=insight_title(
            f"{multi_count:,} accounts use 2+ FinServ categories",
            f"{multi_pct:.1f}% of FinServ-active accounts are multi-product users",
        )
    )
    fig = apply_theme(fig)

    # Top multi-product accounts detail
    multi_detail = None
    sheet = None
    if multi_count > 0:
        multi_accts = acct_cats[acct_cats["Categories Used"] >= 2].copy()
        # Get spend and category list per account
        acct_spend = fs_df.groupby("primary_account_num").agg(
            Total_FinServ_Spend=("amount", "sum"),
            FinServ_Txns=("amount", "count"),
            Categories=("finserv_category", lambda x: ", ".join(sorted(x.unique()))),
        )
        multi_detail = (
            multi_accts.merge(acct_spend, on="primary_account_num", how="left")
            .sort_values("Categories Used", ascending=False)
            .head(50)
            .rename(
                columns={
                    "primary_account_num": "Account",
                    "Total_FinServ_Spend": "Total FinServ Spend",
                    "FinServ_Txns": "Transactions",
                }
            )
        )

        sheet = {
            "name": "S4 Cross-Category",
            "df": multi_detail,
            "currency_cols": ["Total FinServ Spend"],
            "pct_cols": [],
            "number_cols": ["Categories Used", "Transactions"],
        }

    narrative = (
        f"Of <b>{total_fs_accounts:,}</b> accounts with financial services activity, "
        f"<b>{multi_count:,}</b> ({multi_pct:.1f}%) use products across "
        f"<b>2 or more</b> FinServ categories. "
        f"These multi-product users represent a higher wallet-share opportunity "
        f"and may be candidates for bundled financial solutions."
    )

    tables = [("Cross-Category Distribution", dist)]
    if multi_detail is not None:
        tables.append(("Multi-Product Accounts (Top 50)", multi_detail))

    section = {
        "heading": "Cross-Category Analysis",
        "narrative": narrative,
        "figures": [fig],
        "tables": tables,
    }
    return section, sheet
