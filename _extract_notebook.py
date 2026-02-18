"""
One-time script to split CH- Transaction Analysis.ipynb into 13 separate .py files.
Run: python _extract_notebook.py
"""
import json
from pathlib import Path

NOTEBOOK = Path(__file__).parent / "CH- Transaction Analysis.ipynb"
OUT_DIR = Path(__file__).parent

# Define the file splits: (filename, start_cell, end_cell, description)
FILE_SPLITS = [
    ("00_setup.py",              0,  18, "Setup: imports, config, file discovery, data loading, combine"),
    ("01_data_prep.py",         19,  23, "Data Prep: merchant name consolidation"),
    ("02_odd_import.py",        24,  28, "ODD Import: load ODD file, P/B merge, business/personal split"),
    ("03_general.py",           29,  39, "General Analysis: monthly summary, transaction distribution, variance"),
    ("04_merchant_analysis.py", 40,  51, "M1: Top 50 merchants by spend, transactions, unique accounts"),
    ("05_mcc_code.py",          52,  62, "M2: MCC code analysis by accounts, transactions, spend"),
    ("06_business.py",          63,  75, "M3: Business merchant analysis by spend, transactions, accounts"),
    ("07_personal.py",          76,  90, "M4: Personal merchant analysis by spend, transactions, accounts"),
    ("08_monthly_merchant.py",  91, 122, "M5: Monthly rank tracking, growth/decline, consistency, cohort, movers"),
    ("09_competition.py",      123, 208, "M6: Competition config, detection, metrics, risk assessment, account-level"),
    ("10_financial_services.py",209, 228, "M7: Financial services config, detection, summary, cross-category, viz"),
    ("11_payroll.py",          229, 262, "Payroll: circular economy, MoM growth trends"),
    ("12_campaigns.py",        263, 324, "Campaigns: mail campaigns, spend campaigns, ladder movement"),
]

def extract():
    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb["cells"]
    print(f"Loaded notebook: {len(cells)} cells")

    for filename, start, end, description in FILE_SPLITS:
        lines = []
        lines.append(f'# {filename}')
        lines.append(f'# Extracted from: CH- Transaction Analysis.ipynb (cells {start}-{end})')
        lines.append(f'# {description}')
        lines.append(f'# {"=" * 75}')
        lines.append("")

        code_count = 0
        for i in range(start, end + 1):
            cell = cells[i]

            # Add markdown headings as section comments
            if cell["cell_type"] == "markdown":
                md_text = "".join(cell["source"]).strip()
                # Extract heading lines
                for md_line in md_text.split("\n"):
                    stripped = md_line.strip()
                    if stripped.startswith("#"):
                        # Convert markdown heading to comment
                        heading = stripped.lstrip("#").strip()
                        level = len(md_line) - len(md_line.lstrip("#"))
                        if level <= 2:
                            lines.append("")
                            lines.append(f"# {'=' * 75}")
                            lines.append(f"# {heading}")
                            lines.append(f"# {'=' * 75}")
                        elif level == 3:
                            lines.append("")
                            lines.append(f"# ---- {heading} ----")
                        else:
                            lines.append("")
                            lines.append(f"# {heading}")
                continue

            if cell["cell_type"] == "code":
                source = "".join(cell["source"]).strip()
                if not source:
                    continue
                code_count += 1
                lines.append("")
                lines.append(source)
                lines.append("")

        out_path = OUT_DIR / filename
        content = "\n".join(lines)

        # Light cleanup: replace display() with print() for standalone scripts
        # (keep both - comment out display, add print equivalent)
        # Actually, just leave display() as-is since they may run in Jupyter

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  {filename:35s} cells {start:3d}-{end:3d}  ({code_count} code cells, {len(lines)} lines)")

    print(f"\nDone! {len(FILE_SPLITS)} files written to {OUT_DIR}")


if __name__ == "__main__":
    extract()
