# v4_s0_executive.py -- S0: Executive Summary
# Runs AFTER all storylines, reads their results, produces SCR-style synthesis.
from __future__ import annotations

import re

import pandas as pd
from v4_benchmarks import PULSE_2024, compare_to_pulse, METRIC_LABELS
from v4_html_report import build_kpi_html
from v4_themes import format_currency, format_pct


def run(ctx: dict, storyline_results: dict) -> dict:
    """Generate executive summary from completed storyline results.

    Unlike other storylines, this receives the full results dict so it can
    synthesize cross-storyline insights.
    """
    df = ctx["combined_df"]
    odd = ctx["odd_df"]
    config = ctx.get("config", {})
    sections: list[dict] = []
    sheets: list[dict] = []

    _program_health_scorecard(df, odd, config, sections, sheets)
    _key_findings(storyline_results, sections, sheets)
    _competitive_position(storyline_results, sections, sheets)
    _revenue_opportunity_matrix(storyline_results, df, config, sections, sheets)
    _recommended_actions(storyline_results, df, config, sections, sheets)

    return {
        "title": "Executive Summary",
        "description": (
            "Cross-storyline synthesis: program health scorecard, key findings, "
            "competitive position, revenue opportunities, and recommended actions"
        ),
        "sections": sections,
        "sheets": sheets,
    }


# =========================================================================
# Section 1: Program Health Scorecard
# =========================================================================

def _program_health_scorecard(df, odd, config, sections, sheets):
    interchange_rate = config.get("interchange_rate", 0.015)
    recent_months = config.get("recent_months", 12)

    total_accounts = odd["Acct Number"].nunique() if "Acct Number" in odd.columns else 0
    total_spend = df["amount"].sum()
    total_txns = len(df)
    est_interchange = total_spend * interchange_rate

    # Active rate: accounts with >= 1 txn in last month
    active_accounts = 0
    if "year_month" in df.columns:
        latest_month = df["year_month"].max()
        active_accounts = df[df["year_month"] == latest_month]["primary_account_num"].nunique()

    active_rate = (active_accounts / total_accounts * 100) if total_accounts > 0 else 0

    # Monthly txns per active card
    months_in_data = df["year_month"].nunique() if "year_month" in df.columns else 1
    monthly_txns = (total_txns / max(active_accounts, 1) / max(months_in_data, 1))

    # Average ticket
    avg_ticket = (total_spend / total_txns) if total_txns > 0 else 0

    # Annual spend per card
    annual_spend = (total_spend / max(total_accounts, 1) / max(months_in_data, 1) * 12)

    # Build KPI cards with PULSE comparisons
    kpis = [
        {"label": "Total Accounts", "value": f"{total_accounts:,}"},
        {"label": "Active Rate", "value": f"{active_rate:.1f}%",
         "change": active_rate - PULSE_2024["active_rate"]},
        {"label": "Monthly Txns/Card", "value": f"{monthly_txns:.1f}",
         "change": (monthly_txns - PULSE_2024["monthly_txns_per_card"])
                   / PULSE_2024["monthly_txns_per_card"] * 100},
        {"label": "Avg Ticket", "value": f"${avg_ticket:.2f}",
         "change": (avg_ticket - PULSE_2024["avg_ticket"])
                   / PULSE_2024["avg_ticket"] * 100},
        {"label": "Est. Interchange Revenue", "value": format_currency(est_interchange)},
        {"label": "Total Debit Spend", "value": format_currency(total_spend)},
    ]

    kpi_html = build_kpi_html(kpis)

    # Benchmark comparison table
    benchmarks = []
    for metric, actual in [
        ("active_rate", active_rate),
        ("monthly_txns_per_card", monthly_txns),
        ("avg_ticket", avg_ticket),
        ("annual_spend_per_card", annual_spend),
    ]:
        result = compare_to_pulse(metric, actual)
        if result["benchmark"] is not None:
            benchmarks.append({
                "Metric": result["label"],
                "This CU": round(actual, 2),
                "PULSE 2024": result["benchmark"],
                "Delta": result["delta"],
                "Delta %": result["delta_pct"],
                "Status": result["status"].title(),
            })
    bench_df = pd.DataFrame(benchmarks) if benchmarks else pd.DataFrame()

    narr = kpi_html + (
        f"<p>This program spans <b>{total_accounts:,}</b> debit card accounts "
        f"with <b>{format_currency(total_spend)}</b> in total spend across "
        f"<b>{months_in_data}</b> months of data, generating an estimated "
        f"<b>{format_currency(est_interchange)}</b> in interchange revenue "
        f"at a {interchange_rate * 100:.1f}% rate.</p>"
    )

    tables = []
    if not bench_df.empty:
        tables.append(("PULSE 2024 Benchmark Comparison", bench_df))

    sections.append({
        "heading": "Program Health Scorecard",
        "narrative": narr,
        "figures": [],
        "tables": tables,
    })
    if not bench_df.empty:
        sheets.append({
            "name": "S0 Benchmarks", "df": bench_df,
            "pct_cols": ["Delta %"], "number_cols": [],
        })


# =========================================================================
# Section 2: Key Findings (SCR Framework)
# =========================================================================

def _key_findings(storyline_results, sections, sheets):
    findings: list[dict] = []

    # S1: Portfolio health
    _extract_finding(
        storyline_results, "s1_portfolio", findings,
        "Portfolio Health",
        _find_metric_in_narrative,
    )

    # S3: Competition
    _extract_finding(
        storyline_results, "s3_competition", findings,
        "Competitive Landscape",
        _find_metric_in_narrative,
    )

    # S5: Demographics
    _extract_finding(
        storyline_results, "s5_demographics", findings,
        "Demographics & Branches",
        _find_metric_in_narrative,
    )

    # S8: Payroll
    _extract_finding(
        storyline_results, "s8_payroll", findings,
        "Payroll & Circular Economy",
        _find_metric_in_narrative,
    )

    # S9: Lifecycle
    _extract_finding(
        storyline_results, "s9_lifecycle", findings,
        "Lifecycle Management",
        _find_metric_in_narrative,
    )

    if not findings:
        return

    findings_df = pd.DataFrame(findings)

    # Build narrative from findings
    narr_parts = ["<p><b>Key findings across all storylines:</b></p><ul>"]
    for _, row in findings_df.iterrows():
        narr_parts.append(
            f"<li><b>{row['Storyline']}</b>: {row['Finding']}</li>"
        )
    narr_parts.append("</ul>")

    sections.append({
        "heading": "Key Findings",
        "narrative": "\n".join(narr_parts),
        "figures": [],
        "tables": [("Key Findings Summary", findings_df)],
    })
    sheets.append({
        "name": "S0 Key Findings", "df": findings_df,
    })


def _extract_finding(results, key, findings, label, extractor):
    """Safely extract the first meaningful narrative from a storyline result."""
    result = results.get(key)
    if not result:
        return
    for section in result.get("sections", []):
        narr = section.get("narrative", "")
        if narr and "Error" not in narr and "No data" not in narr:
            # Strip HTML tags for the summary
            clean = re.sub(r"<[^>]+>", "", narr)
            # Take first two sentences
            sentences = re.split(r"(?<=[.!])\s+", clean)
            finding = " ".join(sentences[:2]).strip()
            if len(finding) > 20:
                findings.append({
                    "Storyline": label,
                    "Finding": finding[:300],
                })
                return


def _find_metric_in_narrative(narr: str) -> str:
    """Extract key metric from narrative HTML."""
    clean = re.sub(r"<[^>]+>", "", narr)
    return clean[:200]


# =========================================================================
# Section 3: Competitive Position Summary
# =========================================================================

def _competitive_position(storyline_results, sections, sheets):
    s3 = storyline_results.get("s3_competition")
    if not s3:
        return

    # Find competition-related sheets with spend data
    comp_sheets = s3.get("sheets", [])
    comp_narrative = ""
    for section in s3.get("sections", []):
        narr = section.get("narrative", "")
        if narr and "Error" not in narr:
            comp_narrative = narr
            break

    if not comp_narrative:
        return

    sections.append({
        "heading": "Competitive Position",
        "narrative": (
            "<p><b>From S3 Competitive Landscape analysis:</b></p>"
            f"<p>{comp_narrative}</p>"
        ),
        "figures": [],
        "tables": [],
    })


# =========================================================================
# Section 4: Revenue Opportunity Matrix
# =========================================================================

def _revenue_opportunity_matrix(storyline_results, df, config, sections, sheets):
    interchange_rate = config.get("interchange_rate", 0.015)
    opportunities: list[dict] = []

    # Opportunity 1: Inactive card reactivation (from S1)
    s1 = storyline_results.get("s1_portfolio")
    if s1:
        inactive_count = _extract_number_from_sections(s1, "inactive|dormant")
        if inactive_count and inactive_count > 0:
            avg_active_spend = df.groupby("primary_account_num")["amount"].sum().median()
            est_revenue = inactive_count * avg_active_spend * 0.25 * interchange_rate
            opportunities.append({
                "Opportunity": "Inactive Card Reactivation",
                "Target Accounts": int(inactive_count),
                "Est. Annual Revenue": round(est_revenue, 2),
                "Timeline": "Quick Win (0-3 months)",
            })

    # Opportunity 2: Competitor winback (from S3)
    s3 = storyline_results.get("s3_competition")
    if s3:
        comp_spend = _extract_dollar_from_sections(s3)
        if comp_spend and comp_spend > 0:
            winback_revenue = comp_spend * 0.15 * interchange_rate
            opportunities.append({
                "Opportunity": "Competitor Spend Recapture",
                "Target Accounts": 0,  # unknown without deeper analysis
                "Est. Annual Revenue": round(winback_revenue, 2),
                "Timeline": "Medium (3-6 months)",
            })

    # Opportunity 3: Attrition prevention (from S9)
    s9 = storyline_results.get("s9_lifecycle")
    if s9:
        risk_revenue = _extract_dollar_from_sections(s9, "revenue at risk|interchange")
        if risk_revenue and risk_revenue > 0:
            prevention_revenue = risk_revenue * 0.30
            opportunities.append({
                "Opportunity": "Attrition Prevention",
                "Target Accounts": 0,
                "Est. Annual Revenue": round(prevention_revenue, 2),
                "Timeline": "Strategic (6-12 months)",
            })

    if not opportunities:
        return

    opp_df = pd.DataFrame(opportunities)
    total_opp = opp_df["Est. Annual Revenue"].sum()

    narr = (
        f"<p>Three addressable revenue opportunities totaling an estimated "
        f"<b>{format_currency(total_opp)}</b> in annual interchange:</p>"
    )

    sections.append({
        "heading": "Revenue Opportunity Matrix",
        "narrative": narr,
        "figures": [],
        "tables": [("Revenue Opportunities", opp_df)],
    })
    sheets.append({
        "name": "S0 Revenue Opportunities", "df": opp_df,
        "currency_cols": ["Est. Annual Revenue"],
        "number_cols": ["Target Accounts"],
    })


def _extract_number_from_sections(result, pattern):
    """Extract a number from section narratives matching a keyword pattern."""
    for section in result.get("sections", []):
        narr = section.get("narrative", "")
        if re.search(pattern, narr, re.IGNORECASE):
            numbers = re.findall(r"<b>([\d,]+)</b>", narr)
            if numbers:
                try:
                    return int(numbers[0].replace(",", ""))
                except ValueError:
                    pass
    return None


def _extract_dollar_from_sections(result, pattern=None):
    """Extract a dollar amount from section narratives."""
    for section in result.get("sections", []):
        narr = section.get("narrative", "")
        if pattern and not re.search(pattern, narr, re.IGNORECASE):
            continue
        amounts = re.findall(r"\$[\d,]+(?:\.\d{2})?[KMB]?", narr)
        if amounts:
            raw = amounts[0].replace("$", "").replace(",", "")
            multiplier = 1
            if raw.endswith("K"):
                multiplier = 1_000
                raw = raw[:-1]
            elif raw.endswith("M"):
                multiplier = 1_000_000
                raw = raw[:-1]
            elif raw.endswith("B"):
                multiplier = 1_000_000_000
                raw = raw[:-1]
            try:
                return float(raw) * multiplier
            except ValueError:
                pass
    return None


# =========================================================================
# Section 5: Recommended Actions
# =========================================================================

def _recommended_actions(storyline_results, df, config, sections, sheets):
    actions: list[dict] = []

    # Check what data is available
    has_s1 = "s1_portfolio" in storyline_results
    has_s3 = "s3_competition" in storyline_results
    has_s5 = "s5_demographics" in storyline_results
    has_s8 = "s8_payroll" in storyline_results
    has_s9 = "s9_lifecycle" in storyline_results

    if has_s9:
        actions.append({
            "Priority": 1,
            "Action": "Launch early-warning outreach for critical-risk accounts",
            "Target Segment": "Declining & dormant cardholders",
            "Timeline": "Quick Win",
        })

    if has_s1:
        actions.append({
            "Priority": 2,
            "Action": "Run reactivation campaign for inactive debit cards",
            "Target Segment": "Cards with zero txns in 90+ days",
            "Timeline": "Quick Win",
        })

    if has_s3:
        actions.append({
            "Priority": 3,
            "Action": "Develop competitive rate-match or rewards program",
            "Target Segment": "Members with competitor institution outflow",
            "Timeline": "Medium Term",
        })

    if has_s8:
        actions.append({
            "Priority": 4,
            "Action": "Expand payroll direct deposit capture",
            "Target Segment": "Payroll recipients with low recapture rates",
            "Timeline": "Medium Term",
        })

    if has_s5:
        actions.append({
            "Priority": 5,
            "Action": "Target digital-first products for Gen Z/Millennial growth",
            "Target Segment": "Under-30 members with low engagement",
            "Timeline": "Strategic",
        })

    if not actions:
        return

    action_df = pd.DataFrame(actions)

    narr = (
        "<p><b>Prioritized recommendations</b> based on estimated revenue impact "
        "and implementation complexity:</p>"
    )

    sections.append({
        "heading": "Recommended Actions",
        "narrative": narr,
        "figures": [],
        "tables": [("Recommended Actions", action_df)],
    })
    sheets.append({
        "name": "S0 Recommendations", "df": action_df,
    })
