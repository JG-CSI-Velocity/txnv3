# 00_setup.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 0-18)
# Setup: imports, config, file discovery, data loading, combine
# ===========================================================================


# ---- Musings ----

# 

# ===========================================================================
# Setup
# ===========================================================================

# ===========================================================================
# 1 - Import
# ===========================================================================

import pandas as pd
import numpy as np
import os
from pathlib import Path
import glob
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
from dateutil.relativedelta import relativedelta
import re

# For visualization (if needed later)
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')


# ===========================================================================
# 2 - File Configuration
# ===========================================================================

# Configuration
CLIENT_ID = '1453'
CLIENT_NAME = 'Connex'
FILE_EXTENSION = 'csv'  # Change to 'txt' or 'csv' as needed

# Base paths
BASE_PATH = Path(r"C:\Users\james.gilmore\OneDrive - Computer Services, Inc\Desktop\ARS\ARS Analysis")
RAW_DATA_PATH = BASE_PATH / "Raw Data" / "Transaction Files"
CLIENT_PATH = RAW_DATA_PATH / f"{CLIENT_ID} - {CLIENT_NAME}"
RECENT_MONTHS = 12


# ------------------------------------------------------------
# Auto-discover and split files by parsed date
# ------------------------------------------------------------
def is_year_folder(path: Path) -> bool:
    return path.is_dir() and path.name.isdigit() and len(path.name) == 4

def parse_file_date(filepath: Path) -> datetime | None:
    """Extract the MMDDYYYY date from filenames ending in trans-MMDDYYYY"""
    match = re.search(r'trans-(\d{8})$', filepath.stem)
    if match:
        return datetime.strptime(match.group(1), '%m%d%Y')
    return None

if not CLIENT_PATH.exists():
    raise FileNotFoundError(f"Client root path not found: {CLIENT_PATH}")

year_folders = [p for p in CLIENT_PATH.iterdir() if is_year_folder(p)]

# 1) Gather all CSVs across all year folders
year_folders = [p for p in CLIENT_PATH.iterdir() if is_year_folder(p)]
all_files = []
for year_path in year_folders:
    all_files.extend(year_path.glob("*.csv"))

# 2) Define the 12-month window (last 12 completed months)
now = datetime.now()
first_of_current_month = datetime(now.year, now.month, 1)
start_12 = first_of_current_month - relativedelta(months=RECENT_MONTHS)
end_12 = first_of_current_month - relativedelta(days=1)

# 3) Split: most recent 12 files = recent, everything else = older
dated_files = []
unparsed_files = []

for f in all_files:
    file_date = parse_file_date(f)
    if file_date is None:
        unparsed_files.append(f)
    else:
        dated_files.append((f, file_date))

# Sort by date descending, take top 12
dated_files.sort(key=lambda x: x[1], reverse=True)
recent_files = [f for f, _ in dated_files[:RECENT_MONTHS]]
older_files = [f for f, _ in dated_files[RECENT_MONTHS:]]



# 4) Quick summary
print(f"Year folders found: {sorted([p.name for p in year_folders])}")
print(f"Total files:        {len(all_files)}")
print(f"Recent ({RECENT_MONTHS}mo):     {len(recent_files)}  ({start_12:%Y-%m-%d} to {end_12:%Y-%m-%d})")
print(f"Older:              {len(older_files)}")
if unparsed_files:
    print(f"⚠ Unparsed:         {len(unparsed_files)}")
    for u in unparsed_files:
        print(f"  {u.name}")


# ===========================================================================
# 3 - Discover all files in the client folder
# ===========================================================================

# Discover all files in the client folder
all_files = list(CLIENT_PATH.glob(f'**/*.{FILE_EXTENSION}'))
print(f"Found {len(all_files)} files:\n")
for file in sorted(all_files):
    file_size = file.stat().st_size / 1024  # Size in KB
    print(f"  • {file.name} ({file_size:.1f} KB)")

# Identify file extensions
extensions = set([f.suffix.lower() for f in all_files if f.is_file()])
print(f"\nFile types found: {extensions}")


# ===========================================================================
# 4 - Define Data Loading Functions
# ===========================================================================

def load_transaction_file(filepath):
    """
    Load a debit card transaction file
    """
    filepath = Path(filepath)
    
    # Skip the metadata header line, read tab-delimited data
    df = pd.read_csv(filepath, sep='\t', skiprows=1, header=None, low_memory=False)
    
    # Assign column names based on the file definition document
    df.columns = [
        'transaction_date',      # Date of Transaction (MM/DD/YYYY)
        'primary_account_num',   # Primary account number (hashed)
        'transaction_type',      # PIN, SIG, ACH, CHK
        'amount',               # Transaction amount
        'mcc_code',             # Merchant Category Code
        'merchant_name',        # Merchant name
        'terminal_location_1',  # Terminal location/address
        'terminal_location_2',  # Additional location info
        'terminal_id',          # Terminal ID
        'merchant_id',          # Merchant ID  
        'institution',          # Institution number
        'card_present',         # Y/N indicator
        'transaction_code'      # Transaction code
    ][:len(df.columns)]  # Only use as many names as there are columns
    
    # Add metadata
    df['source_file'] = filepath.name
    
    return df

# Load all transaction files
transaction_files = []
files_to_load = sorted(CLIENT_PATH.glob(f'**/*.{FILE_EXTENSION}'))
print(f"Loading {len(files_to_load)} transaction files...\n")

for file_path in files_to_load:
    df = load_transaction_file(file_path)
    transaction_files.append(df)
    print(f"✓ Loaded: {file_path.name} ({len(df):,} rows)")

print(f"\n{'='*50}")
print(f"Total transactions loaded: {sum(len(df) for df in transaction_files):,}")


# ===========================================================================
# 5 - Combine
# ===========================================================================

# Combine all dataframes
combined_df = pd.concat(transaction_files, ignore_index=True)

# Convert data types
combined_df['amount'] = combined_df['amount'].astype(float)
if combined_df['amount'].median() < 0:
    combined_df['amount'] = combined_df['amount'].abs()


# Dataset overview
print(f"Combined Dataset Overview:")
print(f"{'='*50}")
print(f"Total Shape: {combined_df.shape}")
print(f"Total Transactions: {len(combined_df):,}")
print(f"Total Columns: {combined_df.shape[1]}")
print(f"Memory Usage: {combined_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print(f"\nDate Range: {combined_df['transaction_date'].min()} to {combined_df['transaction_date'].max()}")
print(f"Unique Accounts: {combined_df['primary_account_num'].nunique():,}")
print(f"Unique Merchants: {combined_df['merchant_name'].nunique():,}")
print(f"Total Transaction Value: ${combined_df['amount'].sum():,.2f}")


# Check what columns we actually have in the combined dataframe
print("Current columns in combined_df:")
print(combined_df.columns.tolist())
