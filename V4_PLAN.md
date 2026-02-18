# V4: Consultative Transaction Analysis Platform

## Architecture
- Standalone scripts in V3/ (prefix: `v4_`)
- Client config via YAML (no code changes per client)
- Outputs: Excel (data tables) + Interactive HTML (Plotly dashboards)
- Inputs: Transaction CSV files + ODD Excel file

## File Structure
```
V3/
  v4_config.yaml            # Client config + paths + competitor list
  v4_run.py                 # Main entry point: load config, run all, export
  v4_data_loader.py         # Load txn CSV + ODD Excel, merge, prep
  v4_merchant_rules.py      # Merchant name consolidation (frozen rules)
  v4_themes.py              # Chart theme + color palettes + shared builders
  v4_html_report.py         # HTML dashboard generator (Plotly to_html)
  v4_excel_report.py        # Excel writer (openpyxl, multi-tab)
  v4_s1_portfolio_health.py # Storyline 1: Portfolio overview
  v4_s2_merchant_intel.py   # Storyline 2: Merchant intelligence
  v4_s3_competition.py      # Storyline 3: Competitive landscape
  v4_s4_finserv.py          # Storyline 4: Financial services opportunity
  v4_s5_demographics.py     # Storyline 5: Member demographics
  v4_s6_risk.py             # Storyline 6: Risk & balance correlation
  v4_s7_campaigns.py        # Storyline 7: Campaign effectiveness
  v4_s8_payroll.py          # Storyline 8: Payroll circular economy
```

## Execution Order
1. Load config.yaml
2. Load + merge data (txn + ODD)
3. Run storylines S1-S8 (each returns dict of DataFrames + Plotly figures)
4. Write Excel workbook (one tab per analysis table)
5. Write HTML dashboard (one page per storyline, nav sidebar)

## Storylines

### S1: Portfolio Health Dashboard
- Monthly spend/swipes/active accounts trend
- Transaction distribution by amount bracket
- PIN vs Signature mix over time
- Account activation rate (Debit? flag)
- Avg balance distribution

### S2: Merchant Intelligence
- Top merchants by spend/txn/accounts (all, business, personal)
- MCC category analysis
- Monthly merchant rank movement
- Growth leaders & decliners
- Spending consistency & volatility

### S3: Competitive Landscape (YAML-driven)
- Competitor detection from client YAML
- Competitor spend by category (nationals, regionals, CUs, digital, BNPL)
- Age-based competitor segmentation ("Gen Z → Cash App, Boomers → Chase")
- Branch-level competitor penetration
- Competitor threat assessment + momentum
- Account-level competitor segmentation

### S4: Financial Services Opportunity
- Auto loans, mortgages, investments, personal loans, credit cards, student loans
- Account-level summary per category
- Cross-category multi-product analysis
- Age-based financial service usage
- High-value opportunity identification

### S5: Member Demographics & Segmentation
- Age distribution (Account Holder Age)
- Account tenure distribution (Account Age)
- Branch distribution + branch performance
- Balance tier segmentation
- Swipe category distribution (SwipeCat12/3)
- Generation-based spending profiles

### S6: Risk & Balance Correlation
- OD limit trends over time
- Reg E opt-in status tracking
- Balance vs spending patterns
- OD limit utilization
- Risk tier segmentation (balance + OD + spending)

### S7: Campaign Effectiveness
- Mail campaign response rates over time
- Response rate by offer type / segmentation
- Responder vs non-responder spend lift
- Swipe lift analysis
- Campaign ROI measurement
- Ladder movement tracking

### S8: Payroll Circular Economy
- Payroll processor detection
- Business name extraction from payroll descriptions
- Payroll-to-consumer recapture analysis
- Top businesses by recapture potential
- MoM growth trends

## Build Phases
- [ ] Phase 1: Foundation (config, data loader, themes, report shells)
- [ ] Phase 2: S1 Portfolio Health + S2 Merchant Intel
- [ ] Phase 3: S3 Competition + S4 FinServ
- [ ] Phase 4: S5 Demographics + S6 Risk
- [ ] Phase 5: S7 Campaigns + S8 Payroll
- [ ] Phase 6: Polish HTML dashboard, cross-link storylines
