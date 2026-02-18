# v4_benchmarks.py -- PULSE 2024 Debit Issuer Study benchmarks
# Centralized benchmark data for debit card program comparisons.
# Source: PULSE 2024 Debit Issuer Study (Discover Financial Services)
from __future__ import annotations


PULSE_2024: dict[str, float] = {
    "penetration_rate": 80.5,
    "active_rate": 66.3,
    "monthly_txns_per_card": 35.2,
    "avg_ticket": 46.89,
    "annual_spend_per_card": 19_834,
    "interchange_per_txn": 0.46,
    "signature_pct": 62.0,
    "contactless_pct": 24.0,
    "ecommerce_pct": 38.0,
}

METRIC_LABELS: dict[str, str] = {
    "penetration_rate": "Card Penetration Rate (%)",
    "active_rate": "Active Card Rate (%)",
    "monthly_txns_per_card": "Monthly Txns per Card",
    "avg_ticket": "Average Ticket ($)",
    "annual_spend_per_card": "Annual Spend per Card ($)",
    "interchange_per_txn": "Interchange per Txn ($)",
    "signature_pct": "Signature Txns (%)",
    "contactless_pct": "Contactless Txns (%)",
    "ecommerce_pct": "E-Commerce Txns (%)",
}


def compare_to_pulse(metric_name: str, actual_value: float) -> dict:
    """Compare an actual metric to PULSE 2024 benchmark.

    Returns
    -------
    dict with keys: benchmark, actual, delta, delta_pct, status, label
        status is 'above' (>= -10%), 'at' (-10% to -25%), or 'below' (< -25%)
    """
    benchmark = PULSE_2024.get(metric_name)
    if benchmark is None or benchmark == 0:
        return {"benchmark": None, "status": "unknown"}
    delta = actual_value - benchmark
    delta_pct = delta / benchmark * 100
    if delta_pct >= -10:
        status = "above"
    elif delta_pct >= -25:
        status = "at"
    else:
        status = "below"
    return {
        "benchmark": benchmark,
        "actual": round(actual_value, 2),
        "delta": round(delta, 2),
        "delta_pct": round(delta_pct, 1),
        "status": status,
        "label": METRIC_LABELS.get(metric_name, metric_name),
    }
