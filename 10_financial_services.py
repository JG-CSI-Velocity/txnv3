# 10_financial_services.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 209-228)
# M7: Financial services config, detection, summary, cross-category, viz
# ===========================================================================


# ===========================================================================
# 7 - FInancial Services
# ===========================================================================

# ---- Configuration ----

# ===========================================================================
# CELL 1: CONFIGURATION - Financial Services Patterns
# ===========================================================================
"""
## Financial Services Opportunity - Configuration
"""

# Define financial services categories and merchant patterns
FINANCIAL_SERVICES_PATTERNS = {
    'Auto Loans': [
        'TOYOTA MOTOR CREDIT',
        'TOYOTA FINANCIAL',
        'VW CREDIT',
        'VOLKSWAGEN CREDIT',
        'FORD MOTOR CREDIT',
        'FORD CREDIT',
        'GM FINANCIAL',
        'HONDA FINANCE',
        'HONDA FINANCIAL',
        'NISSAN MOTOR ACCEPTANCE',
        'NISSAN FINANCIAL',
        'ALLY AUTO',
        'CAPITAL ONE AUTO',
        'CHASE AUTO FINANCE',
        'SANTANDER CONSUMER',
        'HYUNDAI MOTOR FINANCE',
        'KIA MOTORS FINANCE',
        'SUBARU MOTOR FINANCE',
        'MAZDA FINANCIAL',
        'BMW FINANCIAL',
        'MERCEDES-BENZ FINANCIAL',
        'TESLA FINANCE'
    ],
    
    'Investment/Brokerage': [
        'MORGAN STANLEY CLIENT',
        'MORGAN STANLEY BROKERAGE',
        'RAYMOND JAMES ASSOC',
        'RAYMOND JAMES & ASSOC',
        'CHARLES SCHWAB',
        'SCHWAB BROKERAGE',
        'FIDELITY INVESTMENTS',
        'FIDELITY BROKERAGE',
        'VANGUARD BROKERAGE',
        'VANGUARD GROUP',
        'E\*TRADE',
        'ETRADE',
        'TD AMERITRADE',
        'MERRILL LYNCH',
        'MERRILL EDGE',
        'RBC CAPITAL MARKETS',
        'LPL FINANCIAL',
        'BETTERMENT LLC',
        'WEALTHFRONT BROKERAGE',
        'ROBINHOOD SECURITIES',
        'WEBULL CORPORATION',
        'INTERACTIVE BROKERS',
        'TASTYTRADE'
    ],
    
    'Treasury/Bonds': [
        'TREASURY DIRECT',
        'TREASURYDIRECT',
        'US TREASURY'
    ],
    
    'Mortgage/HELOC': [
        'ROCKET MORTGAGE',
        'QUICKEN LOANS',
        'PENNYMAC LOAN',
        'PENNYMAC CORP',
        'FREEDOM MORTGAGE',
        'MR COOPER MORTGAGE',
        'CALIBER HOME LOANS',
        'OCWEN LOAN',
        'NEWREZ LLC',
        'FLAGSTAR BANK MORTGAGE',
        'LAKEVIEW LOAN',
        'CARRINGTON MORTGAGE',
        'GUILD MORTGAGE',
        'UNITED WHOLESALE MORTGAGE'
    ],
    
    'Personal Loans': [
        'SOFI LENDING',
        'SOFI LOAN',
        'LENDING CLUB CORP',
        'PROSPER FUNDING',
        'UPSTART NETWORK',
        'MARCUS BY GOLDMAN',
        'MARCUS PERSONAL',
        'DISCOVER PERSONAL LOANS',
        'LIGHTSTREAM',
        'PAYOFF INC',
        'BEST EGG'
    ],
    
    'Credit Cards': [
        'AMEX EPAYMENT',
        'AMERICAN EXPRESS PAYMENT',
        'AMERICAN EXPRESS AUTOPAY',
        'DISCOVER CARD PAYMENT',
        'DISCOVER E-PAYMENT',
        'CAPITAL ONE CREDIT CARD',
        'CAPITAL ONE CC PAYMENT',
        'CITI CARD PAYMENT',
        'CITICARDS PAYMENT',
        'BARCLAYS CREDIT CARD',
        'BARCLAYCARD PAYMENT',
        'SYNCHRONY BANK PAYMENT',
        'SYNCHRONY CREDIT',
        'CHASE CARD SERVICES',
        'CHASE CREDIT CARD PAYMENT'
    ],
    
    'Student Loans': [
        'DEPT OF EDUCATION',
        'DEPARTMENT OF EDUCATION',
        'ED FINANCIAL SERVICES',
        'NAVIENT CORPORATION',
        'NAVIENT PAYMENT',
        'NELNET PAYMENT',
        'NELNET LOAN',
        'GREAT LAKES BORROWER',
        'GREAT LAKES HIGHER ED',
        'MOHELA LOAN',
        'AIDVANTAGE',
        'EARNEST OPERATIONS',
        'COMMONBOND LENDING'
    ],
    
    'Business Loans': [
        'SBA LOAN PAYMENT',
        'SMALL BUSINESS ADMIN',
        'KABBAGE INC',
        'BLUEVINE CAPITAL',
        'FUNDBOX INC',
        'LENDIO FUNDING',
        'AMERICAN EXPRESS BUSINESS LOAN',
        'AMEX BUSINESS FINANCING',
        'PAYPAL WORKING CAPITAL',
        'SQUARE CAPITAL',
        'ONDECK CAPITAL'
    ],
    
    'Other Banks': [
        # National Banks
        'BANK OF AMERICA PAYMENT',
        'BANK OF AMERICA TRANSFER',
        'CHASE BANK PAYMENT',
        'CHASE TRANSFER',
        'WELLS FARGO PAYMENT',
        'WELLS FARGO TRANSFER',
        'US BANK PAYMENT',
        'PNC BANK PAYMENT',
        'CITIBANK PAYMENT',
        
        # Regional Banks (IL/WI/IN)
        'BMO HARRIS PAYMENT',
        'BMO HARRIS TRANSFER',
        'FIFTH THIRD PAYMENT',
        '5/3 BANK PAYMENT',
        'HUNTINGTON BANK PAYMENT',
        'OLD NATIONAL BANK PAYMENT',
        'FIRST MIDWEST PAYMENT',
        'WINTRUST PAYMENT',
        
        # Other Credit Unions (Potential competitors)
        'ALLIANT CREDIT UNION PAYMENT',
        'BAXTER CREDIT UNION PAYMENT',
        'CONSUMERS CREDIT UNION PAYMENT',
        'CREDIT UNION 1 PAYMENT',
        
        # Digital Banks
        'ALLY BANK PAYMENT',
        'DISCOVER BANK PAYMENT',
        'CAPITAL ONE 360 PAYMENT',
        'MARCUS BY GOLDMAN PAYMENT',
        'CHIME TRANSFER'
    ]
}

print("✓ Financial services patterns configured")
print(f"Tracking {len(FINANCIAL_SERVICES_PATTERNS)} categories:")
for category, patterns in FINANCIAL_SERVICES_PATTERNS.items():
    print(f"  • {category}: {len(patterns)} patterns")

print("\n💡 Note: Patterns are more specific now to avoid false matches")
print("   (e.g., 'TRADER JOE' won't match investment patterns anymore)")


# ---- Identify FInServ Transaction ----

# ===========================================================================
# CELL 2: IDENTIFY FINANCIAL SERVICES TRANSACTIONS (IMPROVED)
# ===========================================================================
"""
## Financial Services Opportunity - Find Transactions
Uses consolidated merchant names for cleaner results
"""

financial_services_data = {}

print("Scanning for financial services transactions...\n")

for category, patterns in FINANCIAL_SERVICES_PATTERNS.items():
    print(f"{'='*100}")
    print(f"Category: {category}")
    print(f"{'='*100}")
    
    # Create mask for any pattern in this category
    # Use merchant_consolidated if available, otherwise merchant_name
    search_column = 'merchant_consolidated' if 'merchant_consolidated' in combined_df.columns else 'merchant_name'
    
    category_mask = combined_df[search_column].str.contains(
        '|'.join(patterns), 
        case=False, 
        na=False,
        regex=True
    )
    
    category_trans = combined_df[category_mask].copy()
    
    if len(category_trans) == 0:
        print(f"  No transactions found\n")
        continue
    
    # FILTER OUT FALSE POSITIVES
    # Remove common false matches
    false_positive_patterns = [
        'TOWING',
        'TOW SERVICE',
        'BODY SHOP',
        'AUTO REPAIR',
        'AUTO PARTS',
        'AUTOZONE',
        'AUTO TRADER',
        'TRADER JOE',
        "TRADER JOE'S"
    ]
    
    for false_pattern in false_positive_patterns:
        false_mask = category_trans[search_column].str.contains(false_pattern, case=False, na=False)
        if false_mask.any():
            removed_count = false_mask.sum()
            category_trans = category_trans[~false_mask]
            print(f"  Filtered out {removed_count} '{false_pattern}' transactions (false positive)")
    
    if len(category_trans) == 0:
        print(f"  No valid transactions after filtering\n")
        continue
    
    # Show merchant variations found (using consolidated names)
    merchant_summary = category_trans.groupby(search_column).agg({
        'amount': ['sum', 'count'],
        'primary_account_num': 'nunique'
    }).round(2)
    
    merchant_summary.columns = ['Total Spend', 'Transactions', 'Unique Accounts']
    merchant_summary = merchant_summary.sort_values('Total Spend', ascending=False)
    
    print(f"\nMerchants Found: {len(merchant_summary)}")
    print(f"Total Transactions: {len(category_trans):,}")
    print(f"Unique Accounts: {category_trans['primary_account_num'].nunique():,}")
    print(f"Total Spend: ${category_trans['amount'].sum():,.2f}\n")
    
    # Display top merchants in this category
    display_merchants = merchant_summary.head(15).reset_index()
    display_merchants.columns = ['Merchant', 'Total Spend', 'Transactions', 'Unique Accounts']
    
    # Format after renaming columns
    display_merchants['Total Spend'] = display_merchants['Total Spend'].apply(lambda x: f"${x:,.2f}")
    display_merchants['Transactions'] = display_merchants['Transactions'].apply(lambda x: f"{int(x):,}")
    display_merchants['Unique Accounts'] = display_merchants['Unique Accounts'].apply(lambda x: f"{int(x):,}")
    
    display(display_merchants.style.hide(axis='index'))
    
    # Store for analysis
    financial_services_data[category] = {
        'transactions': category_trans,
        'merchant_summary': merchant_summary
    }
    
    print()

print("="*100)
print("✓ Financial services scan complete")
print("="*100)

# Summary across all categories
print("\n📊 SUMMARY ACROSS ALL CATEGORIES:")
print("-"*100)

total_summary = []
for category, data in financial_services_data.items():
    total_summary.append({
        'Category': category,
        'Unique Accounts': data['transactions']['primary_account_num'].nunique(),
        'Total Transactions': len(data['transactions']),
        'Total Spend': data['transactions']['amount'].sum(),
        'Unique Merchants': len(data['merchant_summary'])
    })

if len(total_summary) > 0:
    summary_df = pd.DataFrame(total_summary)
    summary_df = summary_df.sort_values('Total Spend', ascending=False)
    
    display_summary = summary_df.copy()
    display_summary['Unique Accounts'] = display_summary['Unique Accounts'].apply(lambda x: f"{x:,}")
    display_summary['Total Transactions'] = display_summary['Total Transactions'].apply(lambda x: f"{x:,}")
    display_summary['Total Spend'] = display_summary['Total Spend'].apply(lambda x: f"${x:,.0f}")
    display_summary['Unique Merchants'] = display_summary['Unique Merchants'].apply(lambda x: f"{x:,}")
    
    display(display_summary.style.hide(axis='index'))  # Hide row numbers only
    
    print(f"\n💰 Grand Total Spend: ${summary_df['Total Spend'].sum():,.2f}")
    print(f"👥 Total Unique Accounts: {summary_df['Unique Accounts'].sum():,}")
    print(f"📝 Total Transactions: {summary_df['Total Transactions'].sum():,}")


# ---- FinServ Account-level Summary ----

# ===========================================================================
# CELL 3: ACCOUNT-LEVEL SUMMARY BY CATEGORY
# ===========================================================================
"""
## Financial Services Opportunity - Account Analysis
"""

all_financial_accounts = {}

for category, data in financial_services_data.items():
    print(f"\n{'='*100}")
    print(f"ACCOUNT ANALYSIS: {category}")
    print(f"{'='*100}\n")
    
    category_trans = data['transactions']
    
    # Account-level summary
    account_summary = category_trans.groupby('primary_account_num').agg({
        'amount': ['sum', 'count', 'mean'],
        'transaction_date': ['min', 'max'],
        'merchant_name': lambda x: ' | '.join(x.unique()[:3])
    }).round(2)
    
    account_summary.columns = [
        'Total Spend',
        'Transaction Count',
        'Avg Transaction',
        'First Transaction',
        'Last Transaction',
        'Merchants'
    ]
    
    account_summary = account_summary.sort_values('Total Spend', ascending=False)
    
    # Add recency
    account_summary['Recency (Days)'] = (
        pd.Timestamp.now() - account_summary['Last Transaction']
    ).dt.days
    
    # Display top 20
    display_summary = account_summary.head(20).copy()
    display_summary['Total Spend'] = display_summary['Total Spend'].apply(lambda x: f"${x:,.2f}")
    display_summary['Avg Transaction'] = display_summary['Avg Transaction'].apply(lambda x: f"${x:,.2f}")
    display_summary['First Transaction'] = display_summary['First Transaction'].dt.strftime('%Y-%m-%d')
    display_summary['Last Transaction'] = display_summary['Last Transaction'].dt.strftime('%Y-%m-%d')
    
    print(f"Top 20 Accounts by Spend:")
    display(display_summary[['Total Spend', 'Transaction Count', 'Avg Transaction', 
                            'Last Transaction', 'Recency (Days)', 'Merchants']])
    
    # Summary stats
    stats = pd.DataFrame({
        'Metric': [
            'Total Accounts',
            'High Value (>$10k)',
            'Medium Value ($1k-$10k)',
            'Lower Value (<$1k)',
            '',
            'Active (last 30 days)',
            'Active (last 90 days)',
            'Inactive (90+ days)'
        ],
        'Count': [
            len(account_summary),
            len(account_summary[account_summary['Total Spend'] > 10000]),
            len(account_summary[(account_summary['Total Spend'] >= 1000) & (account_summary['Total Spend'] <= 10000)]),
            len(account_summary[account_summary['Total Spend'] < 1000]),
            '',
            len(account_summary[account_summary['Recency (Days)'] <= 30]),
            len(account_summary[account_summary['Recency (Days)'] <= 90]),
            len(account_summary[account_summary['Recency (Days)'] > 90])
        ]
    })
    
    print(f"\nAccount Segmentation:")
    display(stats)
    
    # Store for export
    all_financial_accounts[category] = account_summary


# ---- FinServ - Cross-Category ----

# ===========================================================================
# CELL 4: CROSS-CATEGORY ANALYSIS
# ===========================================================================
"""
## Financial Services Opportunity - Multi-Product Accounts
"""

print("Analyzing accounts using multiple external financial services...\n")

# Get all unique accounts across all categories
all_accounts = set()
for category, accounts in all_financial_accounts.items():
    all_accounts.update(accounts.index)

# For each account, count how many categories they use
account_category_count = {}
account_categories = {}

for account in all_accounts:
    categories_used = []
    for category, account_summary in all_financial_accounts.items():
        if account in account_summary.index:
            categories_used.append(category)
    
    account_category_count[account] = len(categories_used)
    account_categories[account] = ', '.join(categories_used)

# Create summary DataFrame
multi_product = pd.DataFrame({
    'Account': list(account_category_count.keys()),
    'Category_Count': list(account_category_count.values()),
    'Categories': [account_categories[acc] for acc in account_category_count.keys()]
})

# Add total spend across all financial services
multi_product['Total_Financial_Spend'] = multi_product['Account'].apply(
    lambda acc: sum([
        all_financial_accounts[cat].loc[acc, 'Total Spend'] 
        for cat in all_financial_accounts.keys() 
        if acc in all_financial_accounts[cat].index
    ])
)

multi_product = multi_product.sort_values('Category_Count', ascending=False)

# Display multi-product users
multi_users = multi_product[multi_product['Category_Count'] >= 2].copy()
multi_users['Total_Financial_Spend'] = multi_users['Total_Financial_Spend'].apply(lambda x: f"${x:,.2f}")

print(f"Accounts Using Multiple External Financial Services: {len(multi_users):,}")
print(f"\nTop 25 Multi-Product Accounts:")
display(multi_users.head(25))

# Category combination analysis
print(f"\nDistribution by Number of Categories:")
category_dist = multi_product['Category_Count'].value_counts().sort_index(ascending=False)
dist_df = pd.DataFrame({
    'Number of Categories': category_dist.index,
    'Account Count': category_dist.values
})
display(dist_df)

# Store for export
multi_product_accounts = multi_product


# ---- Viz - Accounts by Category ----

# ===========================================================================
# CELL 5: VISUALIZATION - Accounts by Category
# ===========================================================================
"""
## Financial Services Opportunity - Accounts by Category
"""

fig, ax = plt.subplots(figsize=(12, 8))

category_counts = {cat: len(accounts) for cat, accounts in all_financial_accounts.items()}
category_counts = dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))

bars = ax.barh(list(category_counts.keys()), list(category_counts.values()), color='#4ECDC4', edgecolor='black')
ax.set_xlabel('Number of Accounts', fontsize=12)
ax.set_title('Accounts by Financial Service Category', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (cat, val) in enumerate(category_counts.items()):
    ax.text(val, i, f' {val:,}', va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.show()


# ---- Viz - Spend by Category ----

# ===========================================================================
# CELL 6: VISUALIZATION - Total Spend by Category
# ===========================================================================
"""
## Financial Services Opportunity - Total Spend by Category
"""

fig, ax = plt.subplots(figsize=(12, 8))

category_spend = {}
for cat, data in financial_services_data.items():
    category_spend[cat] = data['transactions']['amount'].sum()

category_spend = dict(sorted(category_spend.items(), key=lambda x: x[1], reverse=True))

bars = ax.barh(list(category_spend.keys()), list(category_spend.values()), color='#FF6B6B', edgecolor='black')
ax.set_xlabel('Total Spend ($)', fontsize=12)
ax.set_title('Total Spend by Financial Service Category', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (cat, val) in enumerate(category_spend.items()):
    ax.text(val, i, f' ${val:,.0f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()


# ---- Viz - FinServ - Multi-Product DIstribution ----

# ===========================================================================
# CELL 7: VISUALIZATION - Multi-Product Distribution
# ===========================================================================
"""
## Financial Services Opportunity - Multi-Product Usage
"""

fig, ax = plt.subplots(figsize=(12, 7))

multi_dist = multi_product_accounts['Category_Count'].value_counts().sort_index()

bars = ax.bar(multi_dist.index, multi_dist.values, color='#FFA500', edgecolor='black', linewidth=2, alpha=0.8)
ax.set_xlabel('Number of Financial Service Categories Used', fontsize=12)
ax.set_ylabel('Number of Accounts', fontsize=12)
ax.set_title('Multi-Product Usage Distribution', fontsize=14, fontweight='bold')
ax.set_xticks(multi_dist.index)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar, (cat_count, acc_count) in zip(bars, zip(multi_dist.index, multi_dist.values)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{acc_count:,}\naccounts',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# Highlight multi-product users
multi_users_count = multi_dist[multi_dist.index >= 2].sum()
ax.text(0.98, 0.97, f'{multi_users_count:,} accounts using\n2+ external services\n(HIGH PRIORITY)',
        transform=ax.transAxes, ha='right', va='top',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
        fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()


# ---- VIz - Avg Spend by Category ----

# ===========================================================================
# CELL 8: VISUALIZATION - Average Spend by Category
# ===========================================================================
"""
## Financial Services Opportunity - Average Spend per Account
"""

fig, ax = plt.subplots(figsize=(12, 8))

avg_spend = {}
for cat, accounts in all_financial_accounts.items():
    avg_spend[cat] = accounts['Total Spend'].mean()

avg_spend = dict(sorted(avg_spend.items(), key=lambda x: x[1], reverse=True))

bars = ax.barh(list(avg_spend.keys()), list(avg_spend.values()), color='#9B59B6', edgecolor='black')
ax.set_xlabel('Average Spend per Account ($)', fontsize=12)
ax.set_title('Average Spend per Account by Category', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (cat, val) in enumerate(avg_spend.items()):
    ax.text(val, i, f' ${val:,.0f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()


# ===========================================================================
# Export LIsts
# ===========================================================================

# ===========================================================================
# CELL 9: EXPORT FINANCIAL SERVICES OPPORTUNITIES
# ===========================================================================
"""
## Financial Services Opportunity - Export Account Lists
"""

# Create output directory
fin_output_dir = BASE_PATH / "Analysis Outputs" / f"{CLIENT_ID} - {CLIENT_NAME}" / "Financial Services Opportunities"
fin_output_dir.mkdir(parents=True, exist_ok=True)

export_summary = []

# Export by category
for category, account_summary in all_financial_accounts.items():
    category_clean = category.replace('/', '_').replace(' ', '_')
    
    # Create export DataFrame
    export_df = account_summary.reset_index()
    export_df.columns = ['Account_Number', 'Total_Spend', 'Transaction_Count', 
                         'Avg_Transaction', 'First_Date', 'Last_Date', 
                         'Merchants', 'Recency_Days']
    
    export_df['First_Date'] = export_df['First_Date'].dt.strftime('%Y-%m-%d')
    export_df['Last_Date'] = export_df['Last_Date'].dt.strftime('%Y-%m-%d')
    
    output_file = fin_output_dir / f"FinServ_{category_clean}_Accounts.csv"
    export_df.to_csv(output_file, index=False)
    
    export_summary.append([category, output_file.name, len(export_df)])

# Export multi-product accounts
multi_export = multi_product_accounts.copy()
multi_export.columns = ['Account_Number', 'Category_Count', 'Categories', 'Total_Financial_Spend']

output_multi = fin_output_dir / "FinServ_Multi_Product_Accounts.csv"
multi_export.to_csv(output_multi, index=False)
export_summary.append(['Multi-Product Users', output_multi.name, len(multi_export)])

# Export high-value opportunities (>$10k in any category)
high_value_accounts = []
for category, account_summary in all_financial_accounts.items():
    high_value = account_summary[account_summary['Total Spend'] > 10000].copy()
    for account in high_value.index:
        high_value_accounts.append({
            'Account_Number': account,
            'Category': category,
            'Total_Spend': high_value.loc[account, 'Total Spend'],
            'Transaction_Count': high_value.loc[account, 'Transaction Count'],
            'Last_Transaction': high_value.loc[account, 'Last Transaction'].strftime('%Y-%m-%d'),
            'Recency_Days': high_value.loc[account, 'Recency (Days)']
        })

if high_value_accounts:
    high_value_df = pd.DataFrame(high_value_accounts)
    high_value_df = high_value_df.sort_values('Total_Spend', ascending=False)
    
    output_hv = fin_output_dir / "FinServ_HIGH_VALUE_Opportunities.csv"
    high_value_df.to_csv(output_hv, index=False)
    export_summary.append(['High Value (>$10k)', output_hv.name, len(high_value_df)])

# Display export summary
export_df = pd.DataFrame(export_summary, columns=['Category', 'Filename', 'Account Count'])
print(f"\n✓ All financial services exports complete!")
print(f"Files saved to: {fin_output_dir}\n")
display(export_df)

print(f"\n{'='*100}")
print(f"SUMMARY: Financial Services Opportunity")
print(f"{'='*100}")
print(f"Total Unique Accounts: {len(all_accounts):,}")
print(f"Total Categories Tracked: {len(FINANCIAL_SERVICES_PATTERNS)}")
print(f"Multi-Product Accounts: {len(multi_users):,}")
print(f"High-Value Opportunities (>$10k): {len(high_value_accounts):,}")
print(f"{'='*100}")
