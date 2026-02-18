# V4 Transaction Analysis - Quick Start

## Requirements

- Python 3.10+
- Install dependencies:

```
pip install pandas numpy plotly openpyxl pyyaml kaleido==0.2.1 streamlit
```

## Setup

1. Clone the repo and `cd` into the `V3` directory:

```
git clone https://github.com/JG-CSI-Velocity/txnv3.git
cd txnv3
```

2. Copy and edit the config file for your client:

```
cp v4_config.yaml my_client.yaml
```

3. Edit `my_client.yaml` -- update these fields:

```yaml
client_id: "1453"
client_name: "Connex Credit Union"
client_state: "CT"

transaction_dir: "C:/path/to/transaction/files"
file_extension: "csv"           # or "txt"
odd_file: "C:/path/to/ODD.xlsx"
output_dir: "output/1453_Connex"
```

- `transaction_dir` -- folder containing monthly CSV/TXT transaction files
- `odd_file` -- the ODD Excel file with account-level data (Acct Number, Date Opened, Avg Bal, etc.)
- `output_dir` -- where the Excel and HTML reports will be written (created automatically)

## Run via CLI

```
python v4_run.py my_client.yaml
```

Or use the default config:

```
python v4_run.py
```

This runs all 11 storylines and generates two output files:
- `output/<client>/...V4_Analysis.xlsx` -- multi-tab Excel workbook
- `output/<client>/...V4_Dashboard.html` -- interactive HTML dashboard (open in browser)

## Run via Streamlit App

```
streamlit run v4_app.py
```

This opens a browser UI where you can:
- Paste file paths for transaction dir and ODD file
- Select which storylines to run
- Click "Run Analysis" and download the output files

## Storylines

| Key | Storyline | What It Covers |
|-----|-----------|----------------|
| S0 | Executive Summary | Cross-storyline synthesis, PULSE benchmarks, recommendations |
| S1 | Portfolio Health | KPIs, monthly trends, balance distribution, activation |
| S2 | Merchant Intelligence | Top merchants, growth/decline, rank movers, consistency |
| S3 | Competitive Landscape | Competitor spend, category breakdown, generation penetration |
| S3B | Threat Intelligence | Threat scoring, fastest growing competitors, nonbank threats |
| S3C | Account Segmentation | Risk segments, competitor overlap, marketing lists |
| S4 | Financial Services | Auto loans, investments, mortgages, credit cards, student loans |
| S5 | Demographics & Branches | Generation profiles, branch performance, tenure analysis |
| S6 | Risk & Balance | Balance tiers, inactive accounts, Reg E, OD limits |
| S7 | Campaign Effectiveness | Requires campaign columns in ODD (# of Offers, Mail dates) |
| S8 | Payroll & Circular Economy | Payroll processor detection, employer analysis, recapture rate |
| S9 | Lifecycle Management | Acquisition through attrition, risk scoring, revenue impact |

## Notes

- S7 requires campaign columns in the ODD file (`# of Offers`, `MmmYY Mail`). If absent, the section shows a data availability message.
- S8 detects payroll via processor keywords (ADP, PAYCHEX, INTUIT, etc.). Transaction data is debit card purchases -- payroll deposits appear in credit/deposit data.
- S0 (Executive Summary) runs automatically after all other storylines and appears first in the output.
- The HTML dashboard is a single self-contained file -- share it directly, no server needed.
