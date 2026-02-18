# 11_payroll.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 229-262)
# Payroll: circular economy, MoM growth trends
# ===========================================================================


# ===========================================================================
# Payroll Circular Economy
# ===========================================================================

# =============================================================================
# CLIENT PARAMETERS - CHANGE THESE FOR EACH CLIENT
# =============================================================================

# Analysis parameters
TOP_N = 50  # Top N merchants to analyze
MIN_PAYROLL_SPEND = 10000  # Minimum payroll spend to consider
MAX_MATCH_COUNT = 1000  # Max matches before considering too generic

# Payroll processor names (add more as you discover them)
PAYROLL_PROCESSORS = [
    'PAYROLL-BAMBOOHR', 'INTUIT PAYROLL S', 'INTUIT PAYROLL', 
    'ADP PAYROLL', 'ACCOUNTANTSWORLD', 'CAPITAL PAYROLL',
    'PAYROLL SERVICE', 'PAYROLLDBT', 'NATPAY-', 'PAYCHEX'
]

# Generic terms to skip in matching
GENERIC_SKIP_TERMS = [
    'CAPITAL', 'CONSTRUCTION', 'GREATER', 'ASSOCIATION',
    'SERVICES', 'MANAGEMENT', 'MERCEDE'  # Add terms that cause bad matches
]

# Noise patterns to remove from business names
NOISE_PATTERNS = [
    r'QUICKBOOKS', r'XXXXX\d+', r'IC[A-Z]{2}\d+',
    r'DIR DEP', r'DEPOSIT', r'REIMBURSEM', r'TAXIMPOUND',
    r'DBA', r'FEES', r'\d{8,}'
]

print(f"Analysis configured for: {CLIENT_ID} - {CLIENT_NAME}")
print(f"Parameters: Top {TOP_N} | Min Payroll: ${MIN_PAYROLL_SPEND:,} | Max Matches: {MAX_MATCH_COUNT:,}")


# =============================================================================
# REUSABLE FUNCTION: EXTRACT BUSINESS NAME
# =============================================================================

def extract_business_name_clean(payroll_string):
    """Extract business name from payroll string using configured parameters"""
    import re
    
    cleaned = str(payroll_string).upper()
    
    # Remove payroll processors
    for processor in PAYROLL_PROCESSORS:
        cleaned = cleaned.replace(processor, '')
    
    cleaned = cleaned.replace('PAYROLL', '')
    
    # Remove noise patterns
    for pattern in NOISE_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned)
    
    # Clean special characters
    cleaned = re.sub(r'[^A-Z\s&\'-]', ' ', cleaned)
    
    # Extract words
    words = [w.strip() for w in cleaned.split() if len(w.strip()) > 2]
    noise_words = {'THE', 'INC', 'LLC', 'CO', 'AND', 'FOR', 'TAX', 'DIR', 'DEP'}
    words = [w for w in words if w not in noise_words and len(w) > 1]
    
    if len(words) >= 2:
        return ' '.join(words[:3]).strip()
    elif len(words) == 1:
        return words[0].strip()
    
    return None


# =============================================================================
# M2C-5: PAYROLL CIRCULAR ECONOMY ANALYSIS (CLEAN REUSABLE VERSION)
# =============================================================================

print("\n" + "="*100)
print(f" " * 20 + f"PAYROLL CIRCULAR ECONOMY: {CLIENT_NAME}")
print("="*100)

# Step 1: Get payroll transactions
print("\n📋 STEP 1: Analyzing Payroll Transactions...")
print("-"*100)

payroll_df = business_df[
    business_df['merchant_name'].str.contains('PAYROLL', case=False, na=False)
].copy()

payroll_summary = payroll_df.groupby('merchant_name').agg({
    'amount': 'sum',
    'primary_account_num': 'nunique',
    'transaction_date': 'count'
}).round(2)

payroll_summary.columns = ['total_payroll_spend', 'unique_accounts', 'transaction_count']
payroll_summary = payroll_summary.sort_values('total_payroll_spend', ascending=False)

print(f"\nTop 30 Payroll Businesses:")
print(f"{'Rank':<6} {'Payroll Merchant':<55} {'Payroll Spend':>15}")
print("-"*100)
for rank, (merchant, row) in enumerate(payroll_summary.head(30).iterrows(), 1):
    print(f"{rank:<6} {merchant[:54]:<55} ${row['total_payroll_spend']:>13,.0f}")

# Step 2: Extract business names
print("\n\n📊 STEP 2: Extracting Business Names...")
print("-"*100)

businesses = {}
for merchant in payroll_summary.head(100).index:
    extracted = extract_business_name_clean(merchant)
    
    if not extracted or len(extracted) < 5:
        continue
    
    if extracted.endswith('O') or extracted.endswith('I'):
        continue
    
    if extracted not in businesses:
        businesses[extracted] = {
            'payroll_total': 0,
            'payroll_entries': []
        }
    
    businesses[extracted]['payroll_total'] += payroll_summary.loc[merchant, 'total_payroll_spend']
    businesses[extracted]['payroll_entries'].append(merchant)

sorted_businesses = sorted(businesses.items(), key=lambda x: x[1]['payroll_total'], reverse=True)

print(f"\nExtracted {len(sorted_businesses)} unique businesses:")
print(f"{'Business Name':<45} {'Payroll Spend':>15} {'Entries':>8}")
print("-"*100)
for business, data in sorted_businesses[:30]:
    print(f"{business[:44]:<45} ${data['payroll_total']:>13,.0f} {len(data['payroll_entries']):>8}")

# Step 3: Match with personal spending
print("\n\n🔍 STEP 3: Finding Circular Economy Opportunities...")
print("-"*100)

circular_opportunities = []

for business_name, payroll_data in sorted_businesses[:30]:
    # Skip if below minimum
    if payroll_data['payroll_total'] < MIN_PAYROLL_SPEND:
        continue
    
    words = business_name.split()
    
    if len(words) >= 2:
        search_pattern = ' '.join(words[:2])
    else:
        search_pattern = words[0]
    
    # Skip generic terms
    if search_pattern in GENERIC_SKIP_TERMS:
        continue
    
    # Find matches
    matches = personal_df[
        personal_df['merchant_name'].str.contains(search_pattern, case=False, na=False, regex=False)
    ]
    
    if len(matches) > 0 and len(matches) < MAX_MATCH_COUNT:
        unique_merchants = matches['merchant_name'].unique()
        
        print(f"\n💼 {business_name}")
        print(f"   Payroll Spend: ${payroll_data['payroll_total']:,.0f}")
        print(f"   Found {len(unique_merchants)} consumer merchant variations:")
        
        for merchant in unique_merchants[:5]:
            merchant_data = matches[matches['merchant_name'] == merchant]
            spend = merchant_data['amount'].sum()
            accounts = merchant_data['primary_account_num'].nunique()
            
            print(f"      → {merchant[:65]}")
            print(f"         Personal Spend: ${spend:,.0f} | Accounts: {accounts}")
            
            circular_opportunities.append({
                'business_name': business_name,
                'payroll_spend': payroll_data['payroll_total'],
                'consumer_merchant': merchant,
                'consumer_spend': spend,
                'consumer_accounts': accounts
            })
        
        if len(unique_merchants) > 5:
            print(f"      ... and {len(unique_merchants) - 5} more variations")

print("\n" + "="*100)

# Summary
if circular_opportunities:
    circ_df = pd.DataFrame(circular_opportunities)
    
    # Consolidate by business
    business_summary = circ_df.groupby('business_name').agg({
        'payroll_spend': 'first',
        'consumer_spend': 'sum',
        'consumer_accounts': 'sum'
    }).sort_values('consumer_spend', ascending=False)
    
    print("\n📊 CIRCULAR ECONOMY SUMMARY:")
    print(f"{'Business':<40} {'Payroll $':>15} {'Consumer $':>15} {'Recapture %':>12}")
    print("-"*85)
    for biz, row in business_summary.head(15).iterrows():
        recapture = (row['consumer_spend'] / row['payroll_spend'] * 100) if row['payroll_spend'] > 0 else 0
        print(f"{biz[:39]:<40} ${row['payroll_spend']:>13,.0f} ${row['consumer_spend']:>13,.0f} {recapture:>11.1f}%")
    
    print("-"*85)
    print(f"{'TOTAL':<40} ${business_summary['payroll_spend'].sum():>13,.0f} ${business_summary['consumer_spend'].sum():>13,.0f}")
    
    overall_recapture = (business_summary['consumer_spend'].sum() / business_summary['payroll_spend'].sum() * 100)
    print(f"\nOverall Recapture Rate: {overall_recapture:.2f}%")
else:
    print("\n⚠️  No clear matches found")

print("\n" + "="*100)


# Track top 15 merchants' ranking changes month-to-month
print("\n" + "="*100)
print(" " * 30 + "TOP 15 MERCHANT RANKING CHANGES OVER TIME")
print("="*100)

# Get top 15 merchants for each month and their rankings
monthly_rankings = {}
for month in sorted(combined_df['year_month'].unique()):
    month_data = combined_df[combined_df['year_month'] == month]
    top_monthly = month_data.groupby('merchant_name')['amount'].sum().nlargest(15)
    monthly_rankings[str(month)] = {merchant: rank+1 for rank, merchant in enumerate(top_monthly.index)}

# Convert to DataFrame for analysis
ranking_df = pd.DataFrame(monthly_rankings).T

# Get merchants that appear in top 15 at least 3 times
merchant_appearances = ranking_df.notna().sum()
consistent_merchants = merchant_appearances[merchant_appearances >= 3].index[:15]  # Changed to 15

print(f"Tracking {len(consistent_merchants)} merchants that appear in top 15 at least 3 times")

# Create slope chart
fig, ax = plt.subplots(figsize=(14, 10))

months = list(monthly_rankings.keys())
x_positions = np.arange(len(months))

# Color palette - expanded for 15 merchants
colors = plt.cm.tab20(np.linspace(0, 1, len(consistent_merchants)))

for i, merchant in enumerate(consistent_merchants):
    rankings = []
    x_points = []
    
    for j, month in enumerate(months):
        if merchant in monthly_rankings[month]:
            rankings.append(monthly_rankings[month][merchant])
            x_points.append(j)
    
    if len(rankings) > 1:  # Only plot if merchant appears in multiple months
        ax.plot(x_points, rankings, 'o-', color=colors[i], linewidth=2, markersize=8, alpha=0.7)
        
        # Add merchant name at the end
        if len(x_points) > 0:
            last_x = x_points[-1]
            last_y = rankings[-1]
            merchant_label = merchant[:20] + '...' if len(merchant) > 20 else merchant
            ax.text(last_x + 0.1, last_y, merchant_label, fontsize=8, va='center')

# Customize plot
ax.set_xticks(x_positions)
ax.set_xticklabels(months, rotation=45, ha='right')
ax.set_ylabel('Ranking Position', fontsize=12, fontweight='bold')
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Merchant Ranking Changes by Month', fontsize=14, fontweight='bold', pad=20)

# Invert y-axis so rank 1 is at top
ax.invert_yaxis()
ax.set_ylim(16, 0.5)  # Adjusted for 15 positions

# Add grid
ax.grid(True, linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

# Add ranking labels on y-axis
ax.set_yticks(range(1, 16))
ax.set_yticklabels([f"#{i}" for i in range(1, 16)])

plt.tight_layout()
plt.show()

# Show how many merchants are being tracked
print(f"\nDisplaying {len(consistent_merchants)} merchants on chart")
print("Merchants tracked:")
for i, m in enumerate(consistent_merchants, 1):
    print(f"  {i:2}. {m}")


# Get top MCC codes
mcc_analysis = combined_df.groupby('mcc_code').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique',
    'merchant_name': 'nunique'
}).round(2)

mcc_analysis.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts', 'unique_merchants']
mcc_analysis = mcc_analysis.sort_values('total_amount', ascending=False).head(20)

# Format and display table
print("\n" + "="*110)
print(" " * 35 + "TOP 20 MERCHANT CATEGORY CODES BY SPEND")
print("="*110)
print(f"{'Rank':<6} {'MCC':>6} {'Total Spend':>15} {'Transactions':>12} {'Avg Trans':>10} {'Accounts':>10} {'Merchants':>12}")
print("-"*110)

for rank, (mcc, row) in enumerate(mcc_analysis.iterrows(), 1):
    print(f"{rank:<6} {mcc:>6} ${row['total_amount']:>13,.0f} {row['transaction_count']:>12,.0f} ${row['avg_transaction']:>9.2f} {row['unique_accounts']:>10,.0f} {row['unique_merchants']:>12,.0f}")

print("-"*110)
totals = mcc_analysis.sum()
print(f"{'TOTAL':<6} {'':<6} ${totals['total_amount']:>13,.0f} {totals['transaction_count']:>12,.0f}")
print("="*110)

# Create bar chart
fig, ax = plt.subplots(figsize=(14, 7))

mcc_codes = mcc_analysis.index[:15].astype(str)
values = mcc_analysis['total_amount'].values[:15]

colors = plt.cm.viridis(np.linspace(0.3, 0.9, 15))
bars = ax.bar(range(15), values, color=colors, edgecolor='black', linewidth=0.5)

ax.set_xticks(range(15))
ax.set_xticklabels(mcc_codes, rotation=45, ha='right')
ax.set_xlabel('MCC Code', fontsize=12, fontweight='bold')
ax.set_ylabel('Total Spend ($)', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Merchant Category Codes by Total Spend', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
            f'${value/1e6:.1f}M', ha='center', va='bottom', fontsize=9)

# Format y-axis
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))

ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

plt.tight_layout()
plt.show()


# Analyze account activity patterns BY MONTH
print("\n" + "="*100)
print(" " * 35 + "MONTHLY ACCOUNT ACTIVITY ANALYSIS")
print("="*100)

for month in sorted(combined_df['year_month'].unique()):
    month_data = combined_df[combined_df['year_month'] == month]
    
    # Calculate account stats for this month
    month_accounts = month_data.groupby('primary_account_num').agg({
        'amount': ['sum', 'count', 'mean'],
        'merchant_name': 'nunique'
    })
    
    month_accounts.columns = ['total_spend', 'transactions', 'avg_trans', 'merchants']
    
    # Create spending tiers for this month
    spending_tiers = [0, 100, 500, 1000, 5000, 10000, float('inf')]
    tier_labels = ['<$100', '$100-500', '$500-1K', '$1K-5K', '$5K-10K', '$10K+']
    month_accounts['tier'] = pd.cut(month_accounts['total_spend'], bins=spending_tiers, labels=tier_labels)
    
    # Summarize
    tier_counts = month_accounts['tier'].value_counts().sort_index()
    
    print(f"\n{str(month)}")
    print("-"*80)
    print(f"Total Active Accounts: {len(month_accounts):,}")
    print(f"Total Spend: ${month_accounts['total_spend'].sum():,.0f}")
    print(f"Average per Account: ${month_accounts['total_spend'].mean():.2f}")
    
    print(f"\nAccount Distribution by Spending:")
    for tier, count in tier_counts.items():
        pct = (count / len(month_accounts)) * 100
        tier_spend = month_accounts[month_accounts['tier'] == tier]['total_spend'].sum()
        print(f"  {tier:<12} {count:>6,} accounts ({pct:>5.1f}%)  Total: ${tier_spend:>12,.0f}")

print("\n" + "="*100)

# Create a stacked bar chart showing account distribution changes over time
fig, ax = plt.subplots(figsize=(14, 7))

# Prepare data for stacked bar chart
monthly_tier_data = {}
for month in sorted(combined_df['year_month'].unique()):
    month_data = combined_df[combined_df['year_month'] == month]
    month_accounts = month_data.groupby('primary_account_num')['amount'].sum()
    month_tiers = pd.cut(month_accounts, bins=spending_tiers, labels=tier_labels)
    monthly_tier_data[str(month)] = month_tiers.value_counts().sort_index()

tier_df = pd.DataFrame(monthly_tier_data).T.fillna(0)

# Create stacked bar chart
x = np.arange(len(tier_df.index))
width = 0.8
colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(tier_labels)))

bottom = np.zeros(len(tier_df.index))
for i, tier in enumerate(tier_labels):
    if tier in tier_df.columns:
        values = tier_df[tier].values
        ax.bar(x, values, width, label=tier, bottom=bottom, color=colors[i])
        bottom += values

ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Accounts', fontsize=12, fontweight='bold')
ax.set_title('Monthly Account Distribution by Spending Tier', fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(tier_df.index, rotation=45, ha='right')
ax.legend(title='Spending Tier', bbox_to_anchor=(1.05, 1), loc='upper left')

ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

plt.tight_layout()
plt.show()


# Analyze transaction frequency patterns
account_frequency = combined_df.groupby(['year_month', 'primary_account_num']).size().reset_index(name='monthly_transactions')

# Create frequency buckets
freq_bins = [0, 1, 5, 10, 25, 50, 100, float('inf')]
freq_labels = ['1 trans', '2-5 trans', '6-10 trans', '11-25 trans', '26-50 trans', '51-100 trans', '100+ trans']

# Monthly frequency distribution
print("\n" + "="*100)
print(" " * 30 + "MONTHLY TRANSACTION FREQUENCY DISTRIBUTION")
print("="*100)

for month in sorted(combined_df['year_month'].unique()):
    month_freq = account_frequency[account_frequency['year_month'] == month]
    month_freq['freq_bucket'] = pd.cut(month_freq['monthly_transactions'], bins=freq_bins, labels=freq_labels)
    
    freq_dist = month_freq['freq_bucket'].value_counts().sort_index()
    
    print(f"\n{str(month)}")
    print("-"*60)
    
    for bucket, count in freq_dist.items():
        pct = (count / len(month_freq)) * 100
        # Get total transactions in this bucket
        bucket_accounts = month_freq[month_freq['freq_bucket'] == bucket]['primary_account_num'].values
        bucket_trans = combined_df[(combined_df['year_month'] == month) & 
                                   (combined_df['primary_account_num'].isin(bucket_accounts))]['amount'].sum()
        print(f"  {bucket:<15} {count:>6,} accounts ({pct:>5.1f}%)  Spend: ${bucket_trans:>12,.0f}")

# Create visualization
fig, ax = plt.subplots(figsize=(14, 7))

# Get the last month's data for the chart
last_month = sorted(combined_df['year_month'].unique())[-1]
last_month_freq = account_frequency[account_frequency['year_month'] == last_month]
last_month_freq['freq_bucket'] = pd.cut(last_month_freq['monthly_transactions'], bins=freq_bins, labels=freq_labels)
freq_dist_chart = last_month_freq['freq_bucket'].value_counts().sort_index()

colors = plt.cm.coolwarm(np.linspace(0.2, 0.9, len(freq_labels)))
bars = ax.bar(range(len(freq_dist_chart)), freq_dist_chart.values, color=colors, edgecolor='black', linewidth=0.5)

ax.set_xticks(range(len(freq_dist_chart)))
ax.set_xticklabels(freq_dist_chart.index, rotation=45, ha='right')
ax.set_xlabel('Transaction Frequency', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Accounts', fontsize=12, fontweight='bold')
ax.set_title(f'Account Distribution by Transaction Frequency - {last_month}', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for bar, value in zip(bars, freq_dist_chart.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + max(freq_dist_chart.values)*0.01,
            f'{value:,}', ha='center', va='bottom', fontsize=10)

ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

plt.tight_layout()
plt.show()


# Analyze PIN vs SIG transaction patterns
trans_type_analysis = combined_df.groupby(['year_month', 'transaction_type']).agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique'
}).round(2)

trans_type_analysis.columns = ['total_amount', 'count', 'avg_amount', 'unique_accounts']
trans_type_analysis = trans_type_analysis.reset_index()

# Create pivot tables for easier analysis
amount_pivot = trans_type_analysis.pivot(index='year_month', columns='transaction_type', values='total_amount').fillna(0)
count_pivot = trans_type_analysis.pivot(index='year_month', columns='transaction_type', values='count').fillna(0)

# Format and display
print("\n" + "="*100)
print(" " * 30 + "PIN vs SIGNATURE TRANSACTION ANALYSIS")
print("="*100)

for month in amount_pivot.index:
    print(f"\n{str(month)}")
    print("-"*80)
    
    month_total = amount_pivot.loc[month].sum()
    
    for trans_type in amount_pivot.columns:
        if trans_type in ['PIN', 'SIG']:  # Focus on main types
            amount = amount_pivot.loc[month, trans_type]
            count = count_pivot.loc[month, trans_type]
            pct_amount = (amount / month_total) * 100 if month_total > 0 else 0
            avg_trans = amount / count if count > 0 else 0
            
            print(f"  {trans_type:4} Transactions: {count:>8,.0f} ({pct_amount:>5.1f}% of spend)  "
                  f"Total: ${amount:>12,.0f}  Avg: ${avg_trans:>7.2f}")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Stacked bar chart for transaction volume
months = [str(m) for m in amount_pivot.index]
x_pos = np.arange(len(months))

if 'PIN' in amount_pivot.columns and 'SIG' in amount_pivot.columns:
    pin_values = amount_pivot['PIN'].values / 1e6  # Convert to millions
    sig_values = amount_pivot['SIG'].values / 1e6
    
    ax1.bar(x_pos, pin_values, label='PIN', color='#FF6B6B', alpha=0.8)
    ax1.bar(x_pos, sig_values, bottom=pin_values, label='Signature', color='#4ECDC4', alpha=0.8)
    
    ax1.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Transaction Volume ($M)', fontsize=11, fontweight='bold')
    ax1.set_title('Monthly Transaction Volume by Type', fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(months, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

# Line chart for average transaction size
if 'PIN' in amount_pivot.columns and 'SIG' in amount_pivot.columns:
    pin_avg = (amount_pivot['PIN'] / count_pivot['PIN']).values
    sig_avg = (amount_pivot['SIG'] / count_pivot['SIG']).values
    
    ax2.plot(x_pos, pin_avg, 'o-', label='PIN', color='#FF6B6B', linewidth=2, markersize=8)
    ax2.plot(x_pos, sig_avg, 's-', label='Signature', color='#4ECDC4', linewidth=2, markersize=8)
    
    ax2.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Average Transaction Size ($)', fontsize=11, fontweight='bold')
    ax2.set_title('Average Transaction Size by Type', fontsize=12, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(months, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.3)

plt.tight_layout()
plt.show()

# Summary statistics
print("\n" + "="*100)
print("OVERALL STATISTICS:")
print("-"*80)
total_pin = amount_pivot['PIN'].sum() if 'PIN' in amount_pivot.columns else 0
total_sig = amount_pivot['SIG'].sum() if 'SIG' in amount_pivot.columns else 0
total_all = total_pin + total_sig

print(f"PIN Transactions:  ${total_pin:>12,.0f} ({(total_pin/total_all)*100:>5.1f}%)")
print(f"SIG Transactions:  ${total_sig:>12,.0f} ({(total_sig/total_all)*100:>5.1f}%)")
print(f"Total:             ${total_all:>12,.0f}")


# Analyze card present vs not present patterns
card_present_analysis = combined_df.groupby(['year_month', 'card_present']).agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique',
    'merchant_name': 'nunique'
}).round(2)

card_present_analysis.columns = ['total_amount', 'count', 'avg_amount', 'unique_accounts', 'unique_merchants']
card_present_analysis = card_present_analysis.reset_index()

# Format and display
print("\n" + "="*100)
print(" " * 35 + "CARD PRESENT ANALYSIS")
print("="*100)

for month in sorted(combined_df['year_month'].unique()):
    month_data = card_present_analysis[card_present_analysis['year_month'] == month]
    month_total = month_data['total_amount'].sum()
    
    print(f"\n{str(month)}")
    print("-"*80)
    
    for _, row in month_data.iterrows():
        status = "Card Present" if row['card_present'] == 'Y' else "Card Not Present"
        pct = (row['total_amount'] / month_total) * 100
        
        print(f"  {status:<20} {row['count']:>8,.0f} trans  ${row['total_amount']:>12,.0f} ({pct:>5.1f}%)  "
              f"Avg: ${row['avg_amount']:>7.2f}  Merchants: {row['unique_merchants']:>6,.0f}")

# Create visualization
fig, ax = plt.subplots(figsize=(12, 6))

# Prepare data for grouped bar chart
months = sorted(combined_df['year_month'].unique())
card_present_values = []
card_not_present_values = []

for month in months:
    month_data = card_present_analysis[card_present_analysis['year_month'] == month]
    cp_amount = month_data[month_data['card_present'] == 'Y']['total_amount'].sum() if len(month_data[month_data['card_present'] == 'Y']) > 0 else 0
    cnp_amount = month_data[month_data['card_present'] != 'Y']['total_amount'].sum() if len(month_data[month_data['card_present'] != 'Y']) > 0 else 0
    card_present_values.append(cp_amount / 1e6)  # Convert to millions
    card_not_present_values.append(cnp_amount / 1e6)

x = np.arange(len(months))
width = 0.35

bars1 = ax.bar(x - width/2, card_present_values, width, label='Card Present', color='#2E86AB', alpha=0.8)
bars2 = ax.bar(x + width/2, card_not_present_values, width, label='Card Not Present', color='#A23B72', alpha=0.8)

ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Transaction Volume ($M)', fontsize=12, fontweight='bold')
ax.set_title('Card Present vs Not Present Transaction Volume', fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels([str(m) for m in months], rotation=45, ha='right')
ax.legend()

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'${height:.1f}M', ha='center', va='bottom', fontsize=8)

ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

plt.tight_layout()
plt.show()

# Risk analysis
print("\n" + "="*100)
print("RISK INDICATORS:")
print("-"*80)
total_cnp = card_present_analysis[card_present_analysis['card_present'] != 'Y']['total_amount'].sum()
total_cp = card_present_analysis[card_present_analysis['card_present'] == 'Y']['total_amount'].sum()
cnp_rate = (total_cnp / (total_cnp + total_cp)) * 100

print(f"Card Not Present Rate: {cnp_rate:.1f}% of total transaction volume")
print(f"Total CNP Volume: ${total_cnp:,.0f}")
print(f"Total CP Volume: ${total_cp:,.0f}")


# Create comprehensive summary metrics
print("\n" + "="*100)
print(" " * 40 + "EXECUTIVE SUMMARY")
print("="*100)

# Overall metrics
total_transactions = len(combined_df)
total_spend = combined_df['amount'].sum()
unique_accounts = combined_df['primary_account_num'].nunique()
unique_merchants = combined_df['merchant_name'].nunique()
avg_transaction = combined_df['amount'].mean()
median_transaction = combined_df['amount'].median()

print("\nOVERALL METRICS:")
print("-"*80)
print(f"  Total Transactions:        {total_transactions:>15,}")
print(f"  Total Spend:              ${total_spend:>15,.2f}")
print(f"  Unique Accounts:           {unique_accounts:>15,}")
print(f"  Unique Merchants:          {unique_merchants:>15,}")
print(f"  Average Transaction:      ${avg_transaction:>15.2f}")
print(f"  Median Transaction:       ${median_transaction:>15.2f}")

# Monthly trends
print("\nMONTHLY TRENDS:")
print("-"*80)
monthly_totals = combined_df.groupby('year_month')['amount'].sum()
avg_monthly = monthly_totals.mean()
best_month = monthly_totals.idxmax()
worst_month = monthly_totals.idxmin()

print(f"  Average Monthly Spend:    ${avg_monthly:>15,.2f}")
print(f"  Best Month:                {str(best_month):>15} (${monthly_totals[best_month]:,.2f})")
print(f"  Worst Month:               {str(worst_month):>15} (${monthly_totals[worst_month]:,.2f})")
print(f"  Growth (First to Last):    {((monthly_totals.iloc[-1] / monthly_totals.iloc[0]) - 1) * 100:>14.1f}%")

# Key risk metrics
print("\nRISK METRICS:")
print("-"*80)
high_value_trans = combined_df[combined_df['amount'] >= 500]
small_trans = combined_df[combined_df['amount'] < 5]

print(f"  High Value Trans (>$500):  {len(high_value_trans):>15,} ({(len(high_value_trans)/total_transactions)*100:.2f}%)")
print(f"  Small Trans (<$5):         {len(small_trans):>15,} ({(len(small_trans)/total_transactions)*100:.2f}%)")
print(f"  CNP Transaction Rate:      {(combined_df['card_present'] != 'Y').sum():>15,} ({((combined_df['card_present'] != 'Y').sum()/total_transactions)*100:.2f}%)")

# Create visual dashboard
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# 1. Monthly trend line
months = [str(m) for m in monthly_totals.index]
ax1.plot(months, monthly_totals.values / 1e6, 'o-', color='#2E86AB', linewidth=2, markersize=8)
ax1.set_title('Monthly Spend Trend', fontsize=12, fontweight='bold')
ax1.set_ylabel('Spend ($M)', fontsize=10)
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, linestyle='--', alpha=0.3)
ax1.axhline(y=avg_monthly/1e6, color='red', linestyle='--', alpha=0.5, label='Average')
ax1.legend()

# 2. Transaction type pie
trans_type_dist = combined_df['transaction_type'].value_counts()
ax2.pie(trans_type_dist.values, labels=trans_type_dist.index, autopct='%1.1f%%', 
        colors=['#4ECDC4', '#FF6B6B', '#F7DC6F', '#DDA0DD'])
ax2.set_title('Transaction Type Distribution', fontsize=12, fontweight='bold')

# 3. Top 5 merchants bar
top5_merchants = combined_df.groupby('merchant_name')['amount'].sum().nlargest(5)
merchants_short = [m[:15] + '...' if len(m) > 15 else m for m in top5_merchants.index]
ax3.barh(merchants_short, top5_merchants.values / 1e6, color='#A23B72', alpha=0.8)
ax3.set_title('Top 5 Merchants by Spend', fontsize=12, fontweight='bold')
ax3.set_xlabel('Spend ($M)', fontsize=10)

# 4. Account activity distribution
account_monthly_trans = combined_df.groupby('primary_account_num').size()
activity_bins = [0, 10, 50, 100, 500, float('inf')]
activity_labels = ['<10', '10-50', '50-100', '100-500', '500+']
activity_dist = pd.cut(account_monthly_trans, bins=activity_bins, labels=activity_labels).value_counts()
ax4.bar(activity_dist.index, activity_dist.values, color='#6A994E', alpha=0.8)
ax4.set_title('Account Activity Distribution', fontsize=12, fontweight='bold')
ax4.set_xlabel('Transactions per Account', fontsize=10)
ax4.set_ylabel('Number of Accounts', fontsize=10)

plt.suptitle('TRANSACTION ANALYSIS DASHBOARD', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

print("\n" + "="*100)


# Export all analysis results to Excel for presentation
from datetime import datetime

output_filename = f"Transaction_Analysis_{CLIENT_NAME}_{datetime.now().strftime('%Y%m%d')}.xlsx"

with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    
    # 1. Monthly Summary
    monthly_summary.to_excel(writer, sheet_name='Monthly Summary')
    
    # 2. Transaction Distribution by Amount
    bracket_summary_export = bracket_summary.copy()
    bracket_summary_export['Transactions'] = bracket_summary_export['Transactions'].apply(lambda x: f"{x:,}")
    bracket_summary_export['Trans %'] = bracket_summary_export['Trans %'].apply(lambda x: f"{x:.1f}%")
    bracket_summary_export['Total Value'] = bracket_summary_export['Total Value'].apply(lambda x: f"${x:,.0f}")
    bracket_summary_export['Value %'] = bracket_summary_export['Value %'].apply(lambda x: f"{x:.1f}%")
    bracket_summary_export.to_excel(writer, sheet_name='Amount Distribution', index=False)
    
    # 3. Top 20 Merchants
    top_merchants_export = top_merchants_overall.copy()
    top_merchants_export.reset_index(inplace=True)
    top_merchants_export.columns = ['Merchant', 'Total Spend', 'Transactions', 'Avg Transaction', 'Unique Accounts']
    top_merchants_export.to_excel(writer, sheet_name='Top Merchants', index=False)
    
    # 4. Top MCC Codes
    mcc_export = mcc_analysis.copy()
    mcc_export.reset_index(inplace=True)
    mcc_export.columns = ['MCC Code', 'Total Amount', 'Transactions', 'Avg Transaction', 'Unique Accounts', 'Unique Merchants']
    mcc_export.to_excel(writer, sheet_name='Top MCC Codes', index=False)
    
    # 5. PIN vs SIG Analysis
    trans_type_export = combined_df.groupby(['year_month', 'transaction_type']).agg({
        'amount': ['sum', 'count', 'mean']
    }).round(2)
    trans_type_export.to_excel(writer, sheet_name='Transaction Types')
    
    # 6. Executive Summary
    summary_data = {
        'Metric': [
            'Total Transactions',
            'Total Spend',
            'Unique Accounts', 
            'Unique Merchants',
            'Average Transaction',
            'Median Transaction',
            'Date Range',
            'Months Analyzed'
        ],
        'Value': [
            f"{total_transactions:,}",
            f"${total_spend:,.2f}",
            f"{unique_accounts:,}",
            f"{unique_merchants:,}",
            f"${avg_transaction:.2f}",
            f"${median_transaction:.2f}",
            f"{combined_df['transaction_date'].min().date()} to {combined_df['transaction_date'].max().date()}",
            f"{combined_df['year_month'].nunique()}"
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)

print(f"\n{'='*80}")
print(f"✓ Analysis complete!")
print(f"✓ Results exported to: {output_filename}")
print(f"{'='*80}")

# Display file location
import os
full_path = os.path.abspath(output_filename)
print(f"\nFull path: {full_path}")

# Summary of what was exported
print("\nExported sheets:")
print("  1. Executive Summary - Key metrics overview")
print("  2. Monthly Summary - Month-by-month analysis")
print("  3. Amount Distribution - Transaction brackets")
print("  4. Top Merchants - Top 20 merchants by spend")
print("  5. Top MCC Codes - Top merchant categories")
print("  6. Transaction Types - PIN vs SIG analysis")


# ===========================================================================
# PAYROLL ANALYSIS #1: MONTH-OVER-MONTH GROWTH TRENDS
# ===========================================================================

# =============================================================================
# PAYROLL ANALYSIS #1 (SIMPLIFIED): BUSINESS PAYROLL SPEND TRENDS
# =============================================================================

print("\n" + "="*100)
print(" " * 25 + "PAYROLL SPEND TRENDS BY BUSINESS ACCOUNT")
print("="*100)

# Get payroll transactions
payroll_txns = business_df[
    business_df['merchant_name'].str.contains('PAYROLL', case=False, na=False)
].copy()

# Group by account and month - JUST FOCUS ON SPEND
account_monthly = payroll_txns.groupby(['primary_account_num', 'year_month']).agg({
    'amount': 'sum',
    'merchant_name': lambda x: x.iloc[0]
}).reset_index()

account_monthly.columns = ['account', 'month', 'monthly_spend', 'sample_merchant']

# Only keep accounts in 6+ months with avg >$10K/month
account_summary = account_monthly.groupby('account').agg({
    'monthly_spend': ['sum', 'mean', 'count'],
    'sample_merchant': 'first'
})

account_summary.columns = ['total_spend', 'avg_monthly', 'months_present', 'sample_merchant']
account_summary = account_summary[
    (account_summary['months_present'] >= 6) & 
    (account_summary['avg_monthly'] >= MIN_PAYROLL_SPEND)
]

print(f"\nAnalyzing {len(account_summary)} business accounts with 6+ months and >${MIN_PAYROLL_SPEND:,}/month avg\n")

# Calculate growth for each account
growth_list = []

for account in account_summary.index:
    account_data = account_monthly[account_monthly['account'] == account].sort_values('month')
    
    months_present = len(account_data)
    total_spend = account_data['monthly_spend'].sum()
    avg_monthly = account_data['monthly_spend'].mean()
    sample_merchant = account_data['sample_merchant'].iloc[0]
    
    # First and last month
    first_month_spend = account_data['monthly_spend'].iloc[0]
    last_month_spend = account_data['monthly_spend'].iloc[-1]
    
    # Calculate change
    change_dollars = last_month_spend - first_month_spend
    change_pct = (change_dollars / first_month_spend * 100) if first_month_spend > 0 else 0
    
    # Trend: compare first 3 vs last 3 months average
    if months_present >= 6:
        first_3_avg = account_data['monthly_spend'].iloc[:3].mean()
        last_3_avg = account_data['monthly_spend'].iloc[-3:].mean()
        trend_change = last_3_avg - first_3_avg
        trend_pct = (trend_change / first_3_avg * 100) if first_3_avg > 0 else 0
    else:
        first_3_avg = first_month_spend
        last_3_avg = last_month_spend
        trend_change = change_dollars
        trend_pct = change_pct
    
    # Volatility
    std_dev = account_data['monthly_spend'].std()
    cv = (std_dev / avg_monthly * 100) if avg_monthly > 0 else 0
    
    growth_list.append({
        'account': account[:20] + '...',  # Shorten for display
        'merchant': sample_merchant[:45],
        'months': months_present,
        'total_spend': total_spend,
        'avg_monthly': avg_monthly,
        'first_3_avg': first_3_avg,
        'last_3_avg': last_3_avg,
        'trend_change': trend_change,
        'trend_pct': trend_pct,
        'std_dev': std_dev,
        'cv': cv
    })

growth_df = pd.DataFrame(growth_list)

# Format currency columns
for col in ['total_spend', 'avg_monthly', 'first_3_avg', 'last_3_avg', 'trend_change', 'std_dev']:
    growth_df[col] = growth_df[col].round(0)

# TOP GROWING (3-month trend)
print("\n📈 TOP 15 GROWING BUSINESSES (3-month avg comparison):")
growing = growth_df[growth_df['trend_pct'] > 20].sort_values('trend_change', ascending=False).head(15)
display(growing[['merchant', 'months', 'avg_monthly', 'first_3_avg', 'last_3_avg', 'trend_pct']])

# TOP DECLINING
print("\n📉 TOP 15 DECLINING BUSINESSES (3-month avg comparison):")
declining = growth_df[growth_df['trend_pct'] < -20].sort_values('trend_change').head(15)
display(declining[['merchant', 'months', 'avg_monthly', 'first_3_avg', 'last_3_avg', 'trend_pct']])

# LARGEST
print("\n🎯 TOP 15 LARGEST BUSINESSES (by total payroll spend):")
largest = growth_df.sort_values('total_spend', ascending=False).head(15)
display(largest[['merchant', 'months', 'total_spend', 'avg_monthly', 'cv']])

# Summary
print("\n📊 SUMMARY:")
summary_stats = pd.DataFrame({
    'Metric': [
        'Total Businesses Analyzed',
        'Growing (>20% 3mo trend)',
        'Declining (<-20% 3mo trend)',
        'Stable (-20% to +20%)',
        'Total Payroll Spend',
        'Avg Monthly Payroll/Business',
        'Median Monthly Payroll/Business'
    ],
    'Value': [
        len(growth_df),
        len(growth_df[growth_df['trend_pct'] > 20]),
        len(growth_df[growth_df['trend_pct'] < -20]),
        len(growth_df[(growth_df['trend_pct'] >= -20) & (growth_df['trend_pct'] <= 20)]),
        f"${growth_df['total_spend'].sum():,.0f}",
        f"${growth_df['avg_monthly'].mean():,.0f}",
        f"${growth_df['avg_monthly'].median():,.0f}"
    ]
})
display(summary_stats)


# =============================================================================
# PAYROLL ANALYSIS #1: BUSINESS PAYROLL SPEND TRENDS
# =============================================================================

print("\n" + "="*100)
print(" " * 25 + "PAYROLL SPEND TRENDS BY BUSINESS ACCOUNT")
print("="*100)

# Get payroll transactions
payroll_txns = business_df[
    business_df['merchant_name'].str.contains('PAYROLL', case=False, na=False)
].copy()

# Group by account and month
account_monthly = payroll_txns.groupby(['primary_account_num', 'year_month']).agg({
    'amount': 'sum',
    'transaction_date': 'count',
    'merchant_name': lambda x: x.iloc[0]
}).reset_index()

account_monthly.columns = ['account', 'month', 'monthly_spend', 'num_txns', 'sample_merchant']

# Only keep accounts in 6+ months with avg >$10K/month
account_summary = account_monthly.groupby('account').agg({
    'monthly_spend': ['sum', 'mean', 'count'],
    'num_txns': 'sum',
    'sample_merchant': 'first'
})

account_summary.columns = ['total_spend', 'avg_monthly', 'months_present', 'total_txns', 'sample_merchant']
account_summary = account_summary[
    (account_summary['months_present'] >= 6) & 
    (account_summary['avg_monthly'] >= MIN_PAYROLL_SPEND)
]

print(f"\nAnalyzing {len(account_summary)} business accounts with 6+ months and >${MIN_PAYROLL_SPEND:,}/month avg\n")

# Calculate growth for each account
growth_analysis = []

for account in account_summary.index:
    account_data = account_monthly[account_monthly['account'] == account].sort_values('month')
    
    months_present = len(account_data)
    total_spend = account_data['monthly_spend'].sum()
    total_txns = account_data['num_txns'].sum()
    avg_monthly = account_data['monthly_spend'].mean()
    avg_txns_per_month = account_data['num_txns'].mean()
    sample_merchant = account_data['sample_merchant'].iloc[0]
    
    # Get ALL monthly values
    monthly_values = account_data.set_index('month')['monthly_spend'].to_dict()
    
    # First and last month
    first_month_spend = account_data['monthly_spend'].iloc[0]
    last_month_spend = account_data['monthly_spend'].iloc[-1]
    
    # Calculate change
    change_dollars = last_month_spend - first_month_spend
    change_pct = (change_dollars / first_month_spend * 100) if first_month_spend > 0 else 0
    
    # Volatility
    std_dev = account_data['monthly_spend'].std()
    cv = (std_dev / avg_monthly * 100) if avg_monthly > 0 else 0
    
    growth_analysis.append({
        'account': account,
        'sample_merchant': sample_merchant,
        'months': months_present,
        'total_spend': total_spend,
        'total_txns': total_txns,
        'avg_monthly': avg_monthly,
        'avg_txns_per_month': avg_txns_per_month,
        'monthly_values': monthly_values,
        'first_month_spend': first_month_spend,
        'last_month_spend': last_month_spend,
        'change_dollars': change_dollars,
        'change_pct': change_pct,
        'std_dev': std_dev,
        'cv': cv
    })

growth_df = pd.DataFrame(growth_analysis)

# Reset index so account shows as column
growth_df = growth_df.reset_index(drop=True)

# TOP GROWING
print("\n📈 TOP 15 GROWING BUSINESSES:")
growing = growth_df[growth_df['change_pct'] > 20].sort_values('change_dollars', ascending=False).head(15).copy()
growing['account_short'] = growing['account'].str[:16] + '...'
display(growing[['account_short', 'sample_merchant', 'months', 'total_txns', 'avg_monthly', 'change_dollars', 'change_pct']])

# TOP DECLINING
print("\n📉 TOP 15 DECLINING BUSINESSES:")
declining = growth_df[growth_df['change_pct'] < -20].sort_values('change_dollars').head(15).copy()
declining['account_short'] = declining['account'].str[:16] + '...'
display(declining[['account_short', 'sample_merchant', 'months', 'total_txns', 'avg_monthly', 'change_dollars', 'change_pct']])

# LARGEST
print("\n🎯 TOP 15 LARGEST BUSINESSES:")
largest = growth_df.sort_values('total_spend', ascending=False).head(15).copy()
largest['account_short'] = largest['account'].str[:16] + '...'
display(largest[['account_short', 'sample_merchant', 'months', 'total_spend', 'avg_monthly', 'avg_txns_per_month', 'cv']])

# Summary stats
print("\n📊 SUMMARY:")
summary_stats = pd.DataFrame({
    'Metric': [
        'Total Accounts',
        'Growing (>20%)',
        'Declining (<-20%)',
        'Stable',
        'Total Payroll Spend',
        'Avg Monthly/Business',
        'Median Monthly/Business',
        'Total Transactions',
        'Avg Txns/Month/Business',
        'Avg Transaction Size'
    ],
    'Value': [
        len(growth_df),
        len(growth_df[growth_df['change_pct'] > 20]),
        len(growth_df[growth_df['change_pct'] < -20]),
        len(growth_df[(growth_df['change_pct'] >= -20) & (growth_df['change_pct'] <= 20)]),
        f"${growth_df['total_spend'].sum():,.0f}",
        f"${growth_df['avg_monthly'].mean():,.0f}",
        f"${growth_df['avg_monthly'].median():,.0f}",
        f"{growth_df['total_txns'].sum():,.0f}",
        f"{growth_df['avg_txns_per_month'].mean():.1f}",
        f"${(growth_df['total_spend'].sum() / growth_df['total_txns'].sum()):,.2f}"
    ]
})
display(summary_stats)


# Check terminal location data
print("TERMINAL LOCATION ANALYSIS")
print("="*100)

# Sample of terminal location data
print("\nSample of terminal_location_1 and terminal_location_2:")
sample = personal_df[['merchant_name', 'terminal_location_1', 'terminal_location_2', 'amount']].head(50)
display(sample)

# Check how many transactions have location data
print("\nLocation Data Availability:")
print(f"Total personal transactions: {len(personal_df):,}")
print(f"Has terminal_location_1: {personal_df['terminal_location_1'].notna().sum():,} ({personal_df['terminal_location_1'].notna().sum()/len(personal_df)*100:.1f}%)")
print(f"Has terminal_location_2: {personal_df['terminal_location_2'].notna().sum():,} ({personal_df['terminal_location_2'].notna().sum()/len(personal_df)*100:.1f}%)")

# Look for patterns in location data
print("\nSample terminal_location_1 values:")
print(personal_df['terminal_location_1'].value_counts().head(20))

print("\nSample terminal_location_2 values:")
print(personal_df['terminal_location_2'].value_counts().head(20))

# Check if we can identify Massachusetts/Cape Cod businesses
print("\nChecking for local geographic indicators:")
ma_keywords = ['MA', 'MASS', 'MASSACHUSETTS', 'CAPE COD', 'YARMOUTH', 'DENNIS', 'BARNSTABLE', 'HYANNIS']
for keyword in ma_keywords:
    count_loc1 = personal_df['terminal_location_1'].astype(str).str.contains(keyword, case=False, na=False).sum()
    count_loc2 = personal_df['terminal_location_2'].astype(str).str.contains(keyword, case=False, na=False).sum()
    if count_loc1 > 0 or count_loc2 > 0:
        print(f"  '{keyword}': {count_loc1:,} in location_1, {count_loc2:,} in location_2")
