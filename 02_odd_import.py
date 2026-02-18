# 02_odd_import.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 24-28)
# ODD Import: load ODD file, P/B merge, business/personal split
# ===========================================================================


# ===========================================================================
# ODD Import
# ===========================================================================

# ===========================================================================
# Add ODD from month
# ===========================================================================

# Load ODDD
odd_file = Path(r"C:\Users\james.gilmore\OneDrive - Computer Services, Inc\Desktop\ARS\ARS Analysis\Raw Data\Ready for Analysis\2026.02\1453\1453-2026-02-Connex CU-ODD.xlsx")

print("Loading rewards file...")
rewards_df = pd.read_excel(odd_file)
print(f"Loaded: {len(rewards_df):,} rows, {len(rewards_df.columns)} columns")

# ODD Columns
print("\nColumns:")
for col in rewards_df.columns:
    print(f"  {col}")


# ===========================================================================
# Identify P/B in OD
# ===========================================================================

# ===========================================================================
# SECTION 3B: MERGE ODD DATA & CREATE BUSINESS/PERSONAL SPLITS
# ===========================================================================

# Clean up column names (remove leading/trailing spaces)
rewards_df.columns = rewards_df.columns.str.strip()

# Check business flag distribution
print(f"Business account distribution:")
print(rewards_df['Business?'].value_counts())

# Create a clean subset for merging
odd_subset = rewards_df[['Acct Number', 'Business?']].copy()
odd_subset.columns = ['account_number', 'business_flag']  # Rename to avoid issues

# Merge with transaction data
combined_df = combined_df.merge(
    odd_subset, 
    left_on='primary_account_num', 
    right_on='account_number',
    how='left'
)

# Drop the redundant account_number column
combined_df.drop('account_number', axis=1, inplace=True)

# Check merge results
print(f"\nMerge results:")
print(f"  Total transactions: {len(combined_df):,}")
print(f"  Matched to ODD: {combined_df['business_flag'].notna().sum():,}")
print(f"  Unmatched: {combined_df['business_flag'].isna().sum():,}")

# Check what the actual values are
print("\nBusiness flag unique values in merged data:")
print(combined_df['business_flag'].value_counts())

# Split into business and personal
business_df = combined_df[combined_df['business_flag'] == 'Yes'].copy()
personal_df = combined_df[combined_df['business_flag'] == 'No'].copy()

print(f"\nTransaction split:")
print(f"  Business transactions: {len(business_df):,} (${business_df['amount'].sum():,.2f})")
print(f"  Personal transactions: {len(personal_df):,} (${personal_df['amount'].sum():,.2f})")
print(f"  Unmatched transactions: {combined_df['business_flag'].isna().sum():,}")

# ===========================================================================
# CREATE YEAR_MONTH COLUMN FOR TIME-BASED ANALYSIS
# ===========================================================================

combined_df['transaction_date'] = pd.to_datetime(combined_df['transaction_date'])
business_df['transaction_date'] = pd.to_datetime(business_df['transaction_date'])
personal_df['transaction_date'] = pd.to_datetime(personal_df['transaction_date'])

# Create year_month column in all dataframes
if 'year_month' not in combined_df.columns:
    combined_df['year_month'] = combined_df['transaction_date'].dt.to_period('M')
    business_df['year_month'] = business_df['transaction_date'].dt.to_period('M')
    personal_df['year_month'] = personal_df['transaction_date'].dt.to_period('M')
    print(f"\n✓ Created year_month column for time-based analysis")

# ===========================================================================
# FINAL VERIFICATION
# ===========================================================================

print(f"\n✓ Verification:")
print(f"  combined_df has 'merchant_consolidated': {'merchant_consolidated' in combined_df.columns}")
print(f"  business_df has 'merchant_consolidated': {'merchant_consolidated' in business_df.columns}")
print(f"  personal_df has 'merchant_consolidated': {'merchant_consolidated' in personal_df.columns}")
print(f"  combined_df has 'year_month': {'year_month' in combined_df.columns}")
print(f"  business_df has 'year_month': {'year_month' in business_df.columns}")
print(f"  personal_df has 'year_month': {'year_month' in personal_df.columns}")

if 'merchant_consolidated' not in business_df.columns:
    print("\n⚠️ WARNING: merchant_consolidated column missing!")
    print("   Make sure Section 2 (Data Prep) ran before Section 3!")
elif 'year_month' not in business_df.columns:
    print("\n⚠️ WARNING: year_month column missing!")
    print("   This should not happen - check the code above!")
else:
    print(f"\n✓ Ready for analysis!")
    print(f"  Business unique merchants (consolidated): {business_df['merchant_consolidated'].nunique():,}")
    print(f"  Personal unique merchants (consolidated): {personal_df['merchant_consolidated'].nunique():,}")
    print(f"  Total months in dataset: {combined_df['year_month'].nunique()}")
