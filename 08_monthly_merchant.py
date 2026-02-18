# 08_monthly_merchant.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 91-122)
# M5: Monthly rank tracking, growth/decline, consistency, cohort, movers
# ===========================================================================


# ===========================================================================
# 5 - Monthly Merchant
# ===========================================================================

# ---- MONTHLY RANK TRACKING - TOP MERCHANTS ----

# M5A: MONTHLY RANK TRACKING - TOP MERCHANTS
# Shows how top merchants move up/down in rankings month-over-month
print("\n" + "="*120)
print(" " * 40 + "M5A: MONTHLY RANK TRACKING - TOP MERCHANTS")
print("="*120)

# Get monthly rankings for all merchants
sorted_months = sorted(combined_df['year_month'].unique())
monthly_rankings = {}

for month in sorted_months:
    month_data = combined_df[combined_df['year_month'] == month]
    rankings = month_data.groupby('merchant_consolidated').agg({
        'amount': 'sum'
    }).sort_values('amount', ascending=False)
    
    # Store rank for each merchant
    for rank, merchant in enumerate(rankings.index, 1):
        if merchant not in monthly_rankings:
            monthly_rankings[merchant] = {}
        monthly_rankings[merchant][month] = rank

# Get merchants that appear in top 50 at any point
top_merchants = set()
for month in sorted_months:
    month_data = combined_df[combined_df['year_month'] == month]
    top_50 = month_data.groupby('merchant_consolidated')['amount'].sum().nlargest(50)
    top_merchants.update(top_50.index)

# Create ranking matrix
rank_matrix = []
for merchant in top_merchants:
    row = {'merchant': merchant}
    for month in sorted_months:
        row[month] = monthly_rankings.get(merchant, {}).get(month, None)
    rank_matrix.append(row)

# Convert to DataFrame
rank_df = pd.DataFrame(rank_matrix)

# Calculate average rank and consistency
rank_df['avg_rank'] = rank_df[sorted_months].mean(axis=1, skipna=True)
rank_df['months_in_top_50'] = rank_df[sorted_months].apply(lambda x: (x <= 50).sum(), axis=1)

# Sort by average rank
rank_df = rank_df.sort_values('avg_rank').head(50)

print("\n📊 TOP 50 MERCHANTS BY AVERAGE RANK ACROSS ALL MONTHS")
print("="*120)

# Display table
display_df = rank_df.copy()
display_df['merchant'] = display_df['merchant'].str[:45]

# Format rank columns
for month in sorted_months:
    display_df[month] = display_df[month].apply(lambda x: f"#{int(x)}" if pd.notna(x) and x <= 50 else "-")

display_df['avg_rank'] = display_df['avg_rank'].apply(lambda x: f"#{x:.1f}")
display_df = display_df.rename(columns={
    'merchant': 'Merchant',
    'avg_rank': 'Avg Rank',
    'months_in_top_50': 'Months in Top 50'
})

# Reorder columns
cols = ['Merchant'] + [month for month in sorted_months] + ['Avg Rank', 'Months in Top 50']
display_df = display_df[cols]

display(display_df.style.hide(axis='index'))


# Viz - Merchant Movement

print("\n" + "="*120)
print("📈 RANK MOVEMENT VISUALIZATION")
print("="*120)

# Create line chart showing rank changes for top 50 merchants
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(16, 12))

# Get top 50 by average rank
top_50_merchants = rank_df.nsmallest(50, 'avg_rank')

# Use a larger color palette
colors = plt.cm.tab20(range(20))
colors2 = plt.cm.tab20b(range(20))
colors3 = plt.cm.tab20c(range(10))
all_colors = list(colors) + list(colors2) + list(colors3)

for idx, (_, row) in enumerate(top_50_merchants.iterrows()):
    merchant = row['merchant']
    ranks = [row[month] for month in sorted_months]
    
    # Convert None to NaN for plotting
    ranks = [r if r is not None else float('nan') for r in ranks]
    
    # Plot line - thinner lines for 50 merchants
    ax.plot(range(len(sorted_months)), ranks, 
            marker='o', linewidth=1.5, markersize=4,
            label=merchant[:30], color=all_colors[idx % len(all_colors)], alpha=0.7)

# Invert y-axis (rank 1 at top)
ax.invert_yaxis()
ax.set_ylabel('Rank Position', fontsize=12, fontweight='bold')
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_title('Top 50 Merchants - Rank Movement Over Time', fontsize=14, fontweight='bold', pad=20)

# Set x-axis
ax.set_xticks(range(len(sorted_months)))
ax.set_xticklabels([str(m) for m in sorted_months], rotation=45, ha='right')

# Set y-axis to show ranks 1-50
ax.set_ylim(50, 1)
ax.set_yticks(range(1, 51, 5))

# Grid
ax.grid(True, alpha=0.3, linestyle='--')

# Legend - split into 2 columns for better readability
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7, ncol=2)

plt.tight_layout()
plt.show()

print("\n💡 KEY INSIGHTS:")
print("-"*120)
print(f"   • Top 50 merchants tracked across {len(sorted_months)} months")
print(f"   • Chart shows rank movement for all top 50 performers")
print(f"   • Lower position on chart = higher rank (#1 at top)")
print(f"   • Multiple colors distinguish individual merchant trajectories")
print("="*120)


# ---- GROWTH LEADERS & DECLINERS ----

# M5B-1: GROWTH LEADERS & DECLINERS - ANALYSIS
# Identifies merchants with biggest month-over-month spend changes
print("\n" + "="*120)
print(" " * 40 + "M5B-1: GROWTH LEADERS & DECLINERS - ANALYSIS")
print("="*120)

# Calculate month-over-month changes for each merchant
sorted_months = sorted(combined_df['year_month'].unique())

growth_data = []

for i in range(1, len(sorted_months)):
    prev_month = sorted_months[i-1]
    curr_month = sorted_months[i]
    
    # Previous month spending
    prev_spend = combined_df[combined_df['year_month'] == prev_month].groupby('merchant_consolidated')['amount'].sum()
    
    # Current month spending
    curr_spend = combined_df[combined_df['year_month'] == curr_month].groupby('merchant_consolidated')['amount'].sum()
    
    # Calculate changes for merchants in both months
    for merchant in set(prev_spend.index) & set(curr_spend.index):
        prev_amt = prev_spend[merchant]
        curr_amt = curr_spend[merchant]
        change_amt = curr_amt - prev_amt
        change_pct = (change_amt / prev_amt * 100) if prev_amt > 0 else 0
        
        # Only include significant merchants (min $1000 in either month)
        if max(prev_amt, curr_amt) >= 1000:
            growth_data.append({
                'merchant': merchant,
                'month_pair': f"{prev_month} → {curr_month}",
                'prev_month': prev_month,
                'curr_month': curr_month,
                'prev_spend': prev_amt,
                'curr_spend': curr_amt,
                'change_amount': change_amt,
                'change_percent': change_pct
            })

growth_df = pd.DataFrame(growth_data)

# TOP GROWTH LEADERS
print("\n📈 TOP 50 GROWTH LEADERS (Largest $ Increases)")
print("="*120)

top_growth = growth_df.nlargest(50, 'change_amount').copy()
top_growth['merchant'] = top_growth['merchant'].str[:40]
top_growth_display = top_growth[[
    'merchant', 'month_pair', 'prev_spend', 'curr_spend', 'change_amount', 'change_percent'
]].copy()

top_growth_display.columns = ['Merchant', 'Period', 'Previous Month', 'Current Month', 'Change ($)', 'Change (%)']

# Format currency and percentages
top_growth_display['Previous Month'] = top_growth_display['Previous Month'].apply(lambda x: f"${x:,.0f}")
top_growth_display['Current Month'] = top_growth_display['Current Month'].apply(lambda x: f"${x:,.0f}")
top_growth_display['Change ($)'] = top_growth_display['Change ($)'].apply(lambda x: f"${x:,.0f}")
top_growth_display['Change (%)'] = top_growth_display['Change (%)'].apply(lambda x: f"{x:,.1f}%")

display(top_growth_display.style.hide(axis='index'))

print("\n" + "="*120)

# TOP DECLINERS
print("\n📉 TOP 50 DECLINERS (Largest $ Decreases)")
print("="*120)

top_decline = growth_df.nsmallest(50, 'change_amount').copy()
top_decline['merchant'] = top_decline['merchant'].str[:40]
top_decline_display = top_decline[[
    'merchant', 'month_pair', 'prev_spend', 'curr_spend', 'change_amount', 'change_percent'
]].copy()

top_decline_display.columns = ['Merchant', 'Period', 'Previous Month', 'Current Month', 'Change ($)', 'Change (%)']

# Format currency and percentages
top_decline_display['Previous Month'] = top_decline_display['Previous Month'].apply(lambda x: f"${x:,.0f}")
top_decline_display['Current Month'] = top_decline_display['Current Month'].apply(lambda x: f"${x:,.0f}")
top_decline_display['Change ($)'] = top_decline_display['Change ($)'].apply(lambda x: f"${x:,.0f}")
top_decline_display['Change (%)'] = top_decline_display['Change (%)'].apply(lambda x: f"{x:,.1f}%")

display(top_decline_display.style.hide(axis='index'))

print("\n💡 SUMMARY STATISTICS:")
print("-"*120)
print(f"   • Total month-over-month comparisons analyzed: {len(growth_df):,}")
print(f"   • Average absolute change: ${growth_df['change_amount'].abs().mean():,.0f}")
print(f"   • Median change: ${growth_df['change_amount'].median():,.0f}")
print(f"   • Merchants with increases: {(growth_df['change_amount'] > 0).sum():,} ({(growth_df['change_amount'] > 0).sum() / len(growth_df) * 100:.1f}%)")
print(f"   • Merchants with decreases: {(growth_df['change_amount'] < 0).sum():,} ({(growth_df['change_amount'] < 0).sum() / len(growth_df) * 100:.1f}%)")
print("="*120)


# Viz - Growth

# M5B-2: GROWTH LEADERS VISUALIZATION
print("\n" + "="*120)
print("📈 GROWTH LEADERS - VISUALIZATION")
print("="*120)

# Rebuild growth_df (in case cells run separately)
sorted_months = sorted(combined_df['year_month'].unique())
growth_data = []

for i in range(1, len(sorted_months)):
    prev_month = sorted_months[i-1]
    curr_month = sorted_months[i]
    prev_spend = combined_df[combined_df['year_month'] == prev_month].groupby('merchant_consolidated')['amount'].sum()
    curr_spend = combined_df[combined_df['year_month'] == curr_month].groupby('merchant_consolidated')['amount'].sum()
    
    for merchant in set(prev_spend.index) & set(curr_spend.index):
        prev_amt = prev_spend[merchant]
        curr_amt = curr_spend[merchant]
        change_amt = curr_amt - prev_amt
        change_pct = (change_amt / prev_amt * 100) if prev_amt > 0 else 0
        
        if max(prev_amt, curr_amt) >= 1000:
            growth_data.append({
                'merchant': merchant,
                'change_amount': change_amt,
                'change_percent': change_pct
            })

growth_df = pd.DataFrame(growth_data)

# Create visualization
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 10))

plot_data = growth_df.nlargest(50, 'change_amount').copy()
plot_data = plot_data.sort_values('change_amount', ascending=True)

merchants = plot_data['merchant'].str[:35]
changes = plot_data['change_amount']

bars = ax.barh(range(len(merchants)), changes, color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=0.5)

ax.set_yticks(range(len(merchants)))
ax.set_yticklabels([f"#{i+1} {m}" for i, m in enumerate(merchants)], fontsize=8)
ax.set_xlabel('Month-over-Month Spend Increase ($)', fontsize=11, fontweight='bold')
ax.set_title('Top 50 Growth Leaders - Largest Spend Increases', fontsize=13, fontweight='bold', pad=15)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, changes)):
    ax.text(val, bar.get_y() + bar.get_height()/2, f' ${val:,.0f}', 
            va='center', fontsize=7, fontweight='bold')

ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.show()

print("="*120)


# Viz - Decline

# M5B-3: DECLINERS VISUALIZATION
print("\n" + "="*120)
print("📉 DECLINERS - VISUALIZATION")
print("="*120)

# Rebuild growth_df (in case cells run separately)
sorted_months = sorted(combined_df['year_month'].unique())
growth_data = []

for i in range(1, len(sorted_months)):
    prev_month = sorted_months[i-1]
    curr_month = sorted_months[i]
    prev_spend = combined_df[combined_df['year_month'] == prev_month].groupby('merchant_consolidated')['amount'].sum()
    curr_spend = combined_df[combined_df['year_month'] == curr_month].groupby('merchant_consolidated')['amount'].sum()
    
    for merchant in set(prev_spend.index) & set(curr_spend.index):
        prev_amt = prev_spend[merchant]
        curr_amt = curr_spend[merchant]
        change_amt = curr_amt - prev_amt
        change_pct = (change_amt / prev_amt * 100) if prev_amt > 0 else 0
        
        if max(prev_amt, curr_amt) >= 1000:
            growth_data.append({
                'merchant': merchant,
                'change_amount': change_amt,
                'change_percent': change_pct
            })

growth_df = pd.DataFrame(growth_data)

# Create visualization
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 10))

plot_data = growth_df.nsmallest(50, 'change_amount').copy()
plot_data = plot_data.sort_values('change_amount', ascending=False)  # Most negative at top

merchants = plot_data['merchant'].str[:35]
changes = plot_data['change_amount']

bars = ax.barh(range(len(merchants)), changes, color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=0.5)

ax.set_yticks(range(len(merchants)))
ax.set_yticklabels([f"#{i+1} {m}" for i, m in enumerate(merchants)], fontsize=8)
ax.set_xlabel('Month-over-Month Spend Decrease ($)', fontsize=11, fontweight='bold')
ax.set_title('Top 50 Decliners - Largest Spend Decreases', fontsize=13, fontweight='bold', pad=15)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, changes)):
    ax.text(val, bar.get_y() + bar.get_height()/2, f' ${val:,.0f}', 
            va='center', fontsize=7, fontweight='bold')

ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.show()

print("="*120)


# ---- SPENDING CONSISTENCY ANALYSIS ----

# M5C-1: SPENDING CONSISTENCY ANALYSIS
# Identifies merchants with stable vs volatile spending patterns
print("\n" + "="*120)
print(" " * 40 + "M5C-1: SPENDING CONSISTENCY ANALYSIS")
print("="*120)

# Calculate monthly spending for each merchant
sorted_months = sorted(combined_df['year_month'].unique())

merchant_monthly = combined_df.groupby(['merchant_consolidated', 'year_month'])['amount'].sum().reset_index()

# Pivot to get monthly spending pattern
spending_pivot = merchant_monthly.pivot(index='merchant_consolidated', columns='year_month', values='amount').fillna(0)

# Calculate consistency metrics
consistency_data = []

for merchant in spending_pivot.index:
    monthly_values = spending_pivot.loc[merchant].values
    
    # Filter out zero months
    non_zero_values = monthly_values[monthly_values > 0]
    
    # Only analyze merchants with at least 3 months of activity
    if len(non_zero_values) >= 3:
        total_spend = non_zero_values.sum()
        mean_spend = non_zero_values.mean()
        std_spend = non_zero_values.std()
        cv = (std_spend / mean_spend * 100) if mean_spend > 0 else 0  # Coefficient of variation
        months_active = len(non_zero_values)
        
        consistency_data.append({
            'merchant': merchant,
            'total_spend': total_spend,
            'mean_monthly': mean_spend,
            'std_dev': std_spend,
            'coefficient_variation': cv,
            'months_active': months_active,
            'consistency_score': 100 - min(cv, 100)  # Inverse of CV (higher = more consistent)
        })

consistency_df = pd.DataFrame(consistency_data)

# Filter for significant merchants (at least $10,000 total spend)
consistency_df = consistency_df[consistency_df['total_spend'] >= 10000].copy()

print("\n📊 TOP 50 MOST CONSISTENT MERCHANTS (Low Variation)")
print("="*120)
print("Lower Coefficient of Variation = More Predictable Spending Pattern")
print("-"*120)

most_consistent = consistency_df.nlargest(50, 'consistency_score').copy()
most_consistent['merchant'] = most_consistent['merchant'].str[:40]

consistent_display = most_consistent[[
    'merchant', 'total_spend', 'mean_monthly', 'std_dev', 'coefficient_variation', 'months_active'
]].copy()

consistent_display.columns = ['Merchant', 'Total Spend', 'Avg Monthly', 'Std Dev', 'CV (%)', 'Months Active']

# Format numbers
consistent_display['Total Spend'] = consistent_display['Total Spend'].apply(lambda x: f"${x:,.0f}")
consistent_display['Avg Monthly'] = consistent_display['Avg Monthly'].apply(lambda x: f"${x:,.0f}")
consistent_display['Std Dev'] = consistent_display['Std Dev'].apply(lambda x: f"${x:,.0f}")
consistent_display['CV (%)'] = consistent_display['CV (%)'].apply(lambda x: f"{x:.1f}%")

display(consistent_display.style.hide(axis='index'))

print("\n" + "="*120)

print("\n📊 TOP 50 MOST VOLATILE MERCHANTS (High Variation)")
print("="*120)
print("Higher Coefficient of Variation = More Unpredictable Spending Pattern")
print("-"*120)

most_volatile = consistency_df.nsmallest(50, 'consistency_score').copy()
most_volatile['merchant'] = most_volatile['merchant'].str[:40]

volatile_display = most_volatile[[
    'merchant', 'total_spend', 'mean_monthly', 'std_dev', 'coefficient_variation', 'months_active'
]].copy()

volatile_display.columns = ['Merchant', 'Total Spend', 'Avg Monthly', 'Std Dev', 'CV (%)', 'Months Active']

# Format numbers
volatile_display['Total Spend'] = volatile_display['Total Spend'].apply(lambda x: f"${x:,.0f}")
volatile_display['Avg Monthly'] = volatile_display['Avg Monthly'].apply(lambda x: f"${x:,.0f}")
volatile_display['Std Dev'] = volatile_display['Std Dev'].apply(lambda x: f"${x:,.0f}")
volatile_display['CV (%)'] = volatile_display['CV (%)'].apply(lambda x: f"{x:.1f}%")

display(volatile_display.style.hide(axis='index'))

print("\n💡 CONSISTENCY METRICS EXPLAINED:")
print("-"*120)
print("   • Coefficient of Variation (CV) = Standard Deviation / Mean × 100")
print("   • CV < 50%: Consistent spending pattern")
print("   • CV 50-100%: Moderate variation")
print("   • CV > 100%: High volatility (spiky spending)")
print("\n📈 SUMMARY STATISTICS:")
print("-"*120)
print(f"   • Total merchants analyzed: {len(consistency_df):,}")
print(f"   • Average CV: {consistency_df['coefficient_variation'].mean():.1f}%")
print(f"   • Median CV: {consistency_df['coefficient_variation'].median():.1f}%")
print(f"   • Consistent merchants (CV < 50%): {(consistency_df['coefficient_variation'] < 50).sum():,} ({(consistency_df['coefficient_variation'] < 50).sum() / len(consistency_df) * 100:.1f}%)")
print(f"   • Volatile merchants (CV > 100%): {(consistency_df['coefficient_variation'] > 100).sum():,} ({(consistency_df['coefficient_variation'] > 100).sum() / len(consistency_df) * 100:.1f}%)")
print("="*120)


# Viz - Consisentcy

# M5C-2: CONSISTENT MERCHANTS VISUALIZATION
print("\n" + "="*120)
print("📊 MOST CONSISTENT MERCHANTS - VISUALIZATION")
print("="*120)

# Rebuild consistency_df (in case cells run separately)
sorted_months = sorted(combined_df['year_month'].unique())
merchant_monthly = combined_df.groupby(['merchant_consolidated', 'year_month'])['amount'].sum().reset_index()
spending_pivot = merchant_monthly.pivot(index='merchant_consolidated', columns='year_month', values='amount').fillna(0)

consistency_data = []
for merchant in spending_pivot.index:
    monthly_values = spending_pivot.loc[merchant].values
    non_zero_values = monthly_values[monthly_values > 0]
    
    if len(non_zero_values) >= 3:
        total_spend = non_zero_values.sum()
        mean_spend = non_zero_values.mean()
        std_spend = non_zero_values.std()
        cv = (std_spend / mean_spend * 100) if mean_spend > 0 else 0
        months_active = len(non_zero_values)
        
        consistency_data.append({
            'merchant': merchant,
            'coefficient_variation': cv,
            'consistency_score': 100 - min(cv, 100)
        })

consistency_df = pd.DataFrame(consistency_data)

# Visualization
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 10))

plot_data = consistency_df.nlargest(50, 'consistency_score').head(50).sort_values('coefficient_variation', ascending=False)

merchants = plot_data['merchant'].str[:35]
cv_values = plot_data['coefficient_variation']

bars = ax.barh(range(len(merchants)), cv_values, color='#3498db', alpha=0.8, edgecolor='black', linewidth=0.5)

ax.set_yticks(range(len(merchants)))
ax.set_yticklabels([f"#{i+1} {m}" for i, m in enumerate(merchants)], fontsize=8)
ax.set_xlabel('Coefficient of Variation (%)', fontsize=11, fontweight='bold')
ax.set_title('Top 50 Most Consistent Merchants - Lowest Spending Variation', fontsize=13, fontweight='bold', pad=15)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, cv_values)):
    ax.text(val, bar.get_y() + bar.get_height()/2, f' {val:.1f}%', 
            va='center', fontsize=7, fontweight='bold')

ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.show()

print("="*120)


# Viz - Volatile Merchants

# M5C-3: VOLATILE MERCHANTS VISUALIZATION
print("\n" + "="*120)
print("📊 MOST VOLATILE MERCHANTS - VISUALIZATION")
print("="*120)

# Rebuild consistency_df (in case cells run separately)
sorted_months = sorted(combined_df['year_month'].unique())
merchant_monthly = combined_df.groupby(['merchant_consolidated', 'year_month'])['amount'].sum().reset_index()
spending_pivot = merchant_monthly.pivot(index='merchant_consolidated', columns='year_month', values='amount').fillna(0)

consistency_data = []
for merchant in spending_pivot.index:
    monthly_values = spending_pivot.loc[merchant].values
    non_zero_values = monthly_values[monthly_values > 0]
    
    if len(non_zero_values) >= 3:
        total_spend = non_zero_values.sum()
        mean_spend = non_zero_values.mean()
        std_spend = non_zero_values.std()
        cv = (std_spend / mean_spend * 100) if mean_spend > 0 else 0
        months_active = len(non_zero_values)
        
        consistency_data.append({
            'merchant': merchant,
            'total_spend': total_spend,
            'coefficient_variation': cv,
            'consistency_score': 100 - min(cv, 100)
        })

consistency_df = pd.DataFrame(consistency_data)
consistency_df = consistency_df[consistency_df['total_spend'] >= 10000].copy()

# Visualization
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 10))

plot_data = consistency_df.nsmallest(50, 'consistency_score').head(50).sort_values('coefficient_variation', ascending=True)

merchants = plot_data['merchant'].str[:35]
cv_values = plot_data['coefficient_variation']

bars = ax.barh(range(len(merchants)), cv_values, color='#e67e22', alpha=0.8, edgecolor='black', linewidth=0.5)

ax.set_yticks(range(len(merchants)))
ax.set_yticklabels([f"#{i+1} {m}" for i, m in enumerate(merchants)], fontsize=8)
ax.set_xlabel('Coefficient of Variation (%)', fontsize=11, fontweight='bold')
ax.set_title('Top 50 Most Volatile Merchants - Highest Spending Variation', fontsize=13, fontweight='bold', pad=15)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, cv_values)):
    ax.text(val, bar.get_y() + bar.get_height()/2, f' {val:.1f}%', 
            va='center', fontsize=7, fontweight='bold')

ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.show()

print("="*120)


# ---- NEW VS DECLINING MERCHANTS - ANALYSIS ----

# M5D-1: NEW VS DECLINING MERCHANTS - ANALYSIS (OPTIMIZED)
# Tracks merchant lifecycle - new entrants, established, and declining merchants
print("\n" + "="*120)
print(" " * 40 + "M5D-1: NEW VS DECLINING MERCHANTS - ANALYSIS")
print("="*120)

sorted_months = sorted(combined_df['year_month'].unique())

# OPTIMIZED: Build merchant activity dictionary with vectorized operations
print("Building merchant activity tracker...")

# Get first and last appearance for each merchant (vectorized)
merchant_first_last = combined_df.groupby('merchant_consolidated')['year_month'].agg(['min', 'max', 'nunique'])
merchant_first_last.columns = ['first_month', 'last_month', 'months_active_count']

# Build merchant activity dictionary (much faster)
merchant_activity = {}
for merchant, row in merchant_first_last.iterrows():
    merchant_activity[merchant] = {
        'first_month': row['first_month'],
        'last_month': row['last_month'],
        'months_active': []  # We'll populate this only if needed
    }

print(f"Tracked {len(merchant_activity):,} unique merchants")

# OPTIMIZED: Pre-compute merchant sets per month
print("Computing monthly merchant sets...")
monthly_merchant_sets = {}
monthly_spend_data = {}

for month in sorted_months:
    month_data = combined_df[combined_df['year_month'] == month]
    monthly_merchant_sets[month] = set(month_data['merchant_consolidated'].unique())
    monthly_spend_data[month] = month_data

print(f"Processed {len(sorted_months)} months")

# Analyze each month's cohorts (using pre-computed sets)
print("Analyzing cohorts...")
cohort_analysis = []

for i, month in enumerate(sorted_months):
    month_data = monthly_spend_data[month]
    current_merchants = monthly_merchant_sets[month]
    
    # New merchants (first appearance this month)
    new_merchants = {m for m in current_merchants if merchant_activity[m]['first_month'] == month}
    
    # Returning merchants (active before, not in previous month, but back now)
    if i > 0:
        prev_month = sorted_months[i-1]
        prev_merchants = monthly_merchant_sets[prev_month]
        
        returning = {m for m in current_merchants 
                    if m not in prev_merchants and merchant_activity[m]['first_month'] != month}
        
        # Lost merchants (in previous month, not in current)
        lost = prev_merchants - current_merchants
    else:
        returning = set()
        lost = set()
    
    # Calculate spending (vectorized)
    new_spend = month_data[month_data['merchant_consolidated'].isin(new_merchants)]['amount'].sum()
    returning_spend = month_data[month_data['merchant_consolidated'].isin(returning)]['amount'].sum()
    total_spend = month_data['amount'].sum()
    
    cohort_analysis.append({
        'month': month,
        'total_merchants': len(current_merchants),
        'new_merchants': len(new_merchants),
        'returning_merchants': len(returning),
        'lost_merchants': len(lost),
        'new_spend': new_spend,
        'returning_spend': returning_spend,
        'total_spend': total_spend
    })

cohort_df = pd.DataFrame(cohort_analysis)

print("\n📊 MONTHLY COHORT ANALYSIS")
print("="*120)

display_cohort = cohort_df.copy()
display_cohort['month'] = display_cohort['month'].astype(str)
display_cohort['new_pct'] = (display_cohort['new_merchants'] / display_cohort['total_merchants'] * 100)
display_cohort['returning_pct'] = (display_cohort['returning_merchants'] / display_cohort['total_merchants'] * 100)
display_cohort['new_spend_pct'] = (display_cohort['new_spend'] / display_cohort['total_spend'] * 100)

display_cols = display_cohort[[
    'month', 'total_merchants', 'new_merchants', 'new_pct', 
    'returning_merchants', 'returning_pct', 'lost_merchants',
    'new_spend', 'new_spend_pct'
]].copy()

display_cols.columns = [
    'Month', 'Total Merchants', 'New', 'New %', 
    'Returning', 'Return %', 'Lost',
    'New Merchant $', 'New $ %'
]

# Format
display_cols['New %'] = display_cols['New %'].apply(lambda x: f"{x:.1f}%")
display_cols['Return %'] = display_cols['Return %'].apply(lambda x: f"{x:.1f}%")
display_cols['New Merchant $'] = display_cols['New Merchant $'].apply(lambda x: f"${x:,.0f}")
display_cols['New $ %'] = display_cols['New $ %'].apply(lambda x: f"{x:.1f}%")

display(display_cols.style.hide(axis='index'))

print("\n" + "="*120)

# OPTIMIZED: Top New Merchants by First Month (vectorized aggregation)
print("\n🆕 TOP NEW MERCHANTS BY COHORT (First Appearance)")
print("="*120)

# Build comprehensive summary with a single groupby
new_merchant_summary = combined_df.groupby('merchant_consolidated').agg({
    'amount': ['sum', 'mean'],
    'year_month': ['min', 'nunique'],
    'primary_account_num': 'nunique',
    'transaction_date': 'count'
}).round(2)

new_merchant_summary.columns = ['total_spend', 'avg_transaction', 'first_month', 'months_active', 'unique_accounts', 'transaction_count']
new_merchant_summary['avg_monthly_spend'] = new_merchant_summary['total_spend'] / new_merchant_summary['months_active']
new_merchant_summary = new_merchant_summary.reset_index()

# Show top 5 new merchants from each of the last 3 months - BY TOTAL SPEND
recent_months = sorted_months[-3:]

print("\n" + "="*120)
print("📊 TOP 5 BY TOTAL SPEND")
print("="*120)

for month in recent_months:
    month_new = new_merchant_summary[new_merchant_summary['first_month'] == month].nlargest(5, 'total_spend')
    
    if len(month_new) > 0:
        print(f"\n{str(month)} Cohort:")
        print("-"*120)
        
        display_new = month_new[['merchant_consolidated', 'total_spend', 'unique_accounts', 'transaction_count', 'avg_monthly_spend']].copy()
        display_new['merchant_consolidated'] = display_new['merchant_consolidated'].str[:40]
        display_new.columns = ['Merchant', 'Total Spend', 'Unique Accounts', 'Transactions', 'Avg Monthly Spend']
        
        display_new['Total Spend'] = display_new['Total Spend'].apply(lambda x: f"${x:,.0f}")
        display_new['Unique Accounts'] = display_new['Unique Accounts'].apply(lambda x: f"{int(x):,}")
        display_new['Transactions'] = display_new['Transactions'].apply(lambda x: f"{int(x):,}")
        display_new['Avg Monthly Spend'] = display_new['Avg Monthly Spend'].apply(lambda x: f"${x:,.0f}")
        
        display(display_new.style.hide(axis='index'))

# TOP 5 BY UNIQUE ACCOUNTS
print("\n" + "="*120)
print("👥 TOP 5 BY UNIQUE ACCOUNTS")
print("="*120)

for month in recent_months:
    month_new = new_merchant_summary[new_merchant_summary['first_month'] == month].nlargest(5, 'unique_accounts')
    
    if len(month_new) > 0:
        print(f"\n{str(month)} Cohort:")
        print("-"*120)
        
        display_new = month_new[['merchant_consolidated', 'unique_accounts', 'total_spend', 'transaction_count', 'avg_transaction']].copy()
        display_new['merchant_consolidated'] = display_new['merchant_consolidated'].str[:40]
        display_new.columns = ['Merchant', 'Unique Accounts', 'Total Spend', 'Transactions', 'Avg Transaction']
        
        display_new['Unique Accounts'] = display_new['Unique Accounts'].apply(lambda x: f"{int(x):,}")
        display_new['Total Spend'] = display_new['Total Spend'].apply(lambda x: f"${x:,.0f}")
        display_new['Transactions'] = display_new['Transactions'].apply(lambda x: f"{int(x):,}")
        display_new['Avg Transaction'] = display_new['Avg Transaction'].apply(lambda x: f"${x:,.2f}")
        
        display(display_new.style.hide(axis='index'))

# TOP 5 BY TRANSACTION COUNT
print("\n" + "="*120)
print("🔄 TOP 5 BY TRANSACTION COUNT")
print("="*120)

for month in recent_months:
    month_new = new_merchant_summary[new_merchant_summary['first_month'] == month].nlargest(5, 'transaction_count')
    
    if len(month_new) > 0:
        print(f"\n{str(month)} Cohort:")
        print("-"*120)
        
        display_new = month_new[['merchant_consolidated', 'transaction_count', 'unique_accounts', 'total_spend', 'avg_transaction']].copy()
        display_new['merchant_consolidated'] = display_new['merchant_consolidated'].str[:40]
        display_new.columns = ['Merchant', 'Transactions', 'Unique Accounts', 'Total Spend', 'Avg Transaction']
        
        display_new['Transactions'] = display_new['Transactions'].apply(lambda x: f"{int(x):,}")
        display_new['Unique Accounts'] = display_new['Unique Accounts'].apply(lambda x: f"{int(x):,}")
        display_new['Total Spend'] = display_new['Total Spend'].apply(lambda x: f"${x:,.0f}")
        display_new['Avg Transaction'] = display_new['Avg Transaction'].apply(lambda x: f"${x:,.2f}")
        
        display(display_new.style.hide(axis='index'))

print("\n💡 SUMMARY STATISTICS:")
print("-"*120)
print(f"   • Total unique merchants across all months: {len(merchant_activity):,}")
print(f"   • Average new merchants per month: {cohort_df['new_merchants'].mean():.0f}")
print(f"   • Average returning merchants per month: {cohort_df['returning_merchants'].mean():.0f}")
print(f"   • Average lost merchants per month: {cohort_df['lost_merchants'].mean():.0f}")
print(f"   • Average new merchant contribution: {(cohort_df['new_spend'] / cohort_df['total_spend'] * 100).mean():.1f}% of monthly spend")
print("="*120)


# Viz - Biz Rank Climbers

# M5E-2: BUSINESS RANK CLIMBERS VISUALIZATION
print("\n" + "="*120)
print("📈 BUSINESS RANK CLIMBERS - VISUALIZATION")
print("="*120)

import matplotlib.pyplot as plt

# Rebuild movers_df
sorted_months = sorted(business_df['year_month'].unique())
monthly_movers = []

for i in range(1, len(sorted_months)):
    prev_month = sorted_months[i-1]
    curr_month = sorted_months[i]
    prev_data = business_df[business_df['year_month'] == prev_month]
    prev_rankings = prev_data.groupby('merchant_consolidated')['amount'].sum().sort_values(ascending=False)
    prev_rankings = prev_rankings.reset_index()
    prev_rankings['rank'] = range(1, len(prev_rankings) + 1)
    prev_rankings = prev_rankings.set_index('merchant_consolidated')
    
    curr_data = business_df[business_df['year_month'] == curr_month]
    curr_rankings = curr_data.groupby('merchant_consolidated')['amount'].sum().sort_values(ascending=False)
    curr_rankings = curr_rankings.reset_index()
    curr_rankings['rank'] = range(1, len(curr_rankings) + 1)
    curr_rankings = curr_rankings.set_index('merchant_consolidated')
    
    common = set(prev_rankings.index) & set(curr_rankings.index)
    
    for merchant in common:
        prev_rank = prev_rankings.loc[merchant, 'rank']
        curr_rank = curr_rankings.loc[merchant, 'rank']
        rank_change = prev_rank - curr_rank
        
        if prev_rank <= 100 or curr_rank <= 100:
            monthly_movers.append({'merchant': merchant, 'rank_change': rank_change})

movers_df = pd.DataFrame(monthly_movers)
top_climbers = movers_df[movers_df['rank_change'] > 0].nlargest(50, 'rank_change')

fig, ax = plt.subplots(figsize=(12, 10))
plot_data = top_climbers.sort_values('rank_change', ascending=True)
merchants = plot_data['merchant'].str[:35]
rank_changes = plot_data['rank_change']

bars = ax.barh(range(len(merchants)), rank_changes, color='#9b59b6', alpha=0.8, edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(merchants)))
ax.set_yticklabels([f"#{i+1} {m}" for i, m in enumerate(merchants)], fontsize=8)
ax.set_xlabel('Rank Positions Gained', fontsize=11, fontweight='bold')
ax.set_title('Business Accounts - Top 50 Rank Climbers', fontsize=13, fontweight='bold', pad=15)

for i, (bar, val) in enumerate(zip(bars, rank_changes)):
    ax.text(val, bar.get_y() + bar.get_height()/2, f' ↑{int(val)}', va='center', fontsize=8, fontweight='bold')

ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.show()
print("="*120)


# Viz - Business Rank Fallers

# M5E-3: BUSINESS RANK FALLERS VISUALIZATION
print("\n" + "="*120)
print("📉 BUSINESS RANK FALLERS - VISUALIZATION")
print("="*120)

import matplotlib.pyplot as plt

# Rebuild movers_df
sorted_months = sorted(business_df['year_month'].unique())
monthly_movers = []

for i in range(1, len(sorted_months)):
    prev_month = sorted_months[i-1]
    curr_month = sorted_months[i]
    prev_data = business_df[business_df['year_month'] == prev_month]
    prev_rankings = prev_data.groupby('merchant_consolidated')['amount'].sum().sort_values(ascending=False)
    prev_rankings = prev_rankings.reset_index()
    prev_rankings['rank'] = range(1, len(prev_rankings) + 1)
    prev_rankings = prev_rankings.set_index('merchant_consolidated')
    
    curr_data = business_df[business_df['year_month'] == curr_month]
    curr_rankings = curr_data.groupby('merchant_consolidated')['amount'].sum().sort_values(ascending=False)
    curr_rankings = curr_rankings.reset_index()
    curr_rankings['rank'] = range(1, len(curr_rankings) + 1)
    curr_rankings = curr_rankings.set_index('merchant_consolidated')
    
    common = set(prev_rankings.index) & set(curr_rankings.index)
    
    for merchant in common:
        prev_rank = prev_rankings.loc[merchant, 'rank']
        curr_rank = curr_rankings.loc[merchant, 'rank']
        rank_change = prev_rank - curr_rank
        
        if prev_rank <= 100 or curr_rank <= 100:
            monthly_movers.append({'merchant': merchant, 'rank_change': rank_change})

movers_df = pd.DataFrame(monthly_movers)
top_fallers = movers_df[movers_df['rank_change'] < 0].nsmallest(50, 'rank_change')

fig, ax = plt.subplots(figsize=(12, 10))
plot_data = top_fallers.sort_values('rank_change', ascending=False)
merchants = plot_data['merchant'].str[:35]
rank_changes = plot_data['rank_change'].abs()

bars = ax.barh(range(len(merchants)), rank_changes, color='#8e44ad', alpha=0.8, edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(merchants)))
ax.set_yticklabels([f"#{i+1} {m}" for i, m in enumerate(merchants)], fontsize=8)
ax.set_xlabel('Rank Positions Lost', fontsize=11, fontweight='bold')
ax.set_title('Business Accounts - Top 50 Rank Fallers', fontsize=13, fontweight='bold', pad=15)

for i, (bar, val) in enumerate(zip(bars, rank_changes)):
    ax.text(val, bar.get_y() + bar.get_height()/2, f' ↓{int(val)}', va='center', fontsize=8, fontweight='bold')

ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.show()
print("="*120)


# ---- Personal - MoM Analysis ----

# M5F-1: PERSONAL ACCOUNT - MONTH-OVER-MONTH ANALYSIS
# Focused analysis on personal merchant changes
print("\n" + "="*120)
print(" " * 35 + "M5F-1: PERSONAL ACCOUNT - MONTH-OVER-MONTH ANALYSIS")
print("="*120)

sorted_months = sorted(personal_df['year_month'].unique())

# Calculate month-over-month changes
monthly_movers = []

for i in range(1, len(sorted_months)):
    prev_month = sorted_months[i-1]
    curr_month = sorted_months[i]
    
    # Previous and current month rankings
    prev_data = personal_df[personal_df['year_month'] == prev_month]
    prev_rankings = prev_data.groupby('merchant_consolidated').agg({
        'amount': 'sum',
        'primary_account_num': 'nunique',
        'transaction_date': 'count'
    }).sort_values('amount', ascending=False)
    prev_rankings['rank'] = range(1, len(prev_rankings) + 1)
    
    curr_data = personal_df[personal_df['year_month'] == curr_month]
    curr_rankings = curr_data.groupby('merchant_consolidated').agg({
        'amount': 'sum',
        'primary_account_num': 'nunique',
        'transaction_date': 'count'
    }).sort_values('amount', ascending=False)
    curr_rankings['rank'] = range(1, len(curr_rankings) + 1)
    
    # Compare merchants in both months
    common = set(prev_rankings.index) & set(curr_rankings.index)
    
    for merchant in common:
        prev_rank = prev_rankings.loc[merchant, 'rank']
        curr_rank = curr_rankings.loc[merchant, 'rank']
        prev_spend = prev_rankings.loc[merchant, 'amount']
        curr_spend = curr_rankings.loc[merchant, 'amount']
        
        rank_change = prev_rank - curr_rank
        spend_change = curr_spend - prev_spend
        spend_change_pct = (spend_change / prev_spend * 100) if prev_spend > 0 else 0
        
        if prev_rank <= 100 or curr_rank <= 100:
            monthly_movers.append({
                'month_transition': f"{prev_month} → {curr_month}",
                'merchant': merchant,
                'prev_rank': prev_rank,
                'curr_rank': curr_rank,
                'rank_change': rank_change,
                'prev_spend': prev_spend,
                'curr_spend': curr_spend,
                'spend_change': spend_change,
                'spend_change_pct': spend_change_pct
            })

movers_df = pd.DataFrame(monthly_movers)

print("\n📈 TOP 50 PERSONAL RANK CLIMBERS (Biggest Improvements)")
print("="*120)

top_climbers = movers_df[movers_df['rank_change'] > 0].nlargest(50, 'rank_change').copy()
top_climbers['merchant'] = top_climbers['merchant'].str[:40]

climbers_display = top_climbers[[
    'month_transition', 'merchant', 'prev_rank', 'curr_rank', 'rank_change',
    'prev_spend', 'curr_spend', 'spend_change_pct'
]].copy()

climbers_display.columns = [
    'Period', 'Merchant', 'Prev Rank', 'Curr Rank', 'Rank +',
    'Previous $', 'Current $', 'Change %'
]

climbers_display['Previous $'] = climbers_display['Previous $'].apply(lambda x: f"${x:,.0f}")
climbers_display['Current $'] = climbers_display['Current $'].apply(lambda x: f"${x:,.0f}")
climbers_display['Change %'] = climbers_display['Change %'].apply(lambda x: f"{x:+.1f}%")
climbers_display['Rank +'] = climbers_display['Rank +'].apply(lambda x: f"↑{int(x)}")

display(climbers_display.style.hide(axis='index'))

print("\n" + "="*120)

print("\n📉 TOP 50 PERSONAL RANK FALLERS (Biggest Declines)")
print("="*120)

top_fallers = movers_df[movers_df['rank_change'] < 0].nsmallest(50, 'rank_change').copy()
top_fallers['merchant'] = top_fallers['merchant'].str[:40]

fallers_display = top_fallers[[
    'month_transition', 'merchant', 'prev_rank', 'curr_rank', 'rank_change',
    'prev_spend', 'curr_spend', 'spend_change_pct'
]].copy()

fallers_display.columns = [
    'Period', 'Merchant', 'Prev Rank', 'Curr Rank', 'Rank -',
    'Previous $', 'Current $', 'Change %'
]

fallers_display['Previous $'] = fallers_display['Previous $'].apply(lambda x: f"${x:,.0f}")
fallers_display['Current $'] = fallers_display['Current $'].apply(lambda x: f"${x:,.0f}")
fallers_display['Change %'] = fallers_display['Change %'].apply(lambda x: f"{x:+.1f}%")
fallers_display['Rank -'] = fallers_display['Rank -'].apply(lambda x: f"↓{abs(int(x))}")

display(fallers_display.style.hide(axis='index'))

print("\n💰 TOP 50 PERSONAL SPEND INCREASES")
print("="*120)

top_spend_increase = movers_df.nlargest(50, 'spend_change').copy()
top_spend_increase['merchant'] = top_spend_increase['merchant'].str[:40]

spend_inc_display = top_spend_increase[[
    'month_transition', 'merchant', 'prev_spend', 'curr_spend', 'spend_change', 'spend_change_pct'
]].copy()

spend_inc_display.columns = ['Period', 'Merchant', 'Previous $', 'Current $', 'Change $', 'Change %']

spend_inc_display['Previous $'] = spend_inc_display['Previous $'].apply(lambda x: f"${x:,.0f}")
spend_inc_display['Current $'] = spend_inc_display['Current $'].apply(lambda x: f"${x:,.0f}")
spend_inc_display['Change $'] = spend_inc_display['Change $'].apply(lambda x: f"${x:,.0f}")
spend_inc_display['Change %'] = spend_inc_display['Change %'].apply(lambda x: f"{x:+.1f}%")

display(spend_inc_display.style.hide(axis='index'))

print("\n💡 PERSONAL ACCOUNT SUMMARY:")
print("-"*120)
print(f"   • Total month-over-month comparisons: {len(movers_df):,}")
print(f"   • Merchants with rank improvements: {(movers_df['rank_change'] > 0).sum():,}")
print(f"   • Merchants with rank declines: {(movers_df['rank_change'] < 0).sum():,}")
print(f"   • Average absolute rank change: {movers_df['rank_change'].abs().mean():.1f} positions")
print(f"   • Merchants with spend increases: {(movers_df['spend_change'] > 0).sum():,} ({(movers_df['spend_change'] > 0).sum() / len(movers_df) * 100:.1f}%)")
print("="*120)


# Viz - Personal Rank Climbers

# M5F-2: PERSONAL RANK CLIMBERS VISUALIZATION
print("\n" + "="*120)
print("📈 PERSONAL RANK CLIMBERS - VISUALIZATION")
print("="*120)

import matplotlib.pyplot as plt

# Rebuild movers_df
sorted_months = sorted(personal_df['year_month'].unique())
monthly_movers = []

for i in range(1, len(sorted_months)):
    prev_month = sorted_months[i-1]
    curr_month = sorted_months[i]
    prev_data = personal_df[personal_df['year_month'] == prev_month]
    prev_rankings = prev_data.groupby('merchant_consolidated')['amount'].sum().sort_values(ascending=False)
    prev_rankings = prev_rankings.reset_index()
    prev_rankings['rank'] = range(1, len(prev_rankings) + 1)
    prev_rankings = prev_rankings.set_index('merchant_consolidated')
    
    curr_data = personal_df[personal_df['year_month'] == curr_month]
    curr_rankings = curr_data.groupby('merchant_consolidated')['amount'].sum().sort_values(ascending=False)
    curr_rankings = curr_rankings.reset_index()
    curr_rankings['rank'] = range(1, len(curr_rankings) + 1)
    curr_rankings = curr_rankings.set_index('merchant_consolidated')
    
    common = set(prev_rankings.index) & set(curr_rankings.index)
    
    for merchant in common:
        prev_rank = prev_rankings.loc[merchant, 'rank']
        curr_rank = curr_rankings.loc[merchant, 'rank']
        rank_change = prev_rank - curr_rank
        
        if prev_rank <= 100 or curr_rank <= 100:
            monthly_movers.append({'merchant': merchant, 'rank_change': rank_change})

movers_df = pd.DataFrame(monthly_movers)
top_climbers = movers_df[movers_df['rank_change'] > 0].nlargest(50, 'rank_change')

fig, ax = plt.subplots(figsize=(12, 10))
plot_data = top_climbers.sort_values('rank_change', ascending=True)
merchants = plot_data['merchant'].str[:35]
rank_changes = plot_data['rank_change']

bars = ax.barh(range(len(merchants)), rank_changes, color='#16a085', alpha=0.8, edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(merchants)))
ax.set_yticklabels([f"#{i+1} {m}" for i, m in enumerate(merchants)], fontsize=8)
ax.set_xlabel('Rank Positions Gained', fontsize=11, fontweight='bold')
ax.set_title('Personal Accounts - Top 50 Rank Climbers', fontsize=13, fontweight='bold', pad=15)

for i, (bar, val) in enumerate(zip(bars, rank_changes)):
    ax.text(val, bar.get_y() + bar.get_height()/2, f' ↑{int(val)}', va='center', fontsize=8, fontweight='bold')

ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.show()
print("="*120)


# Viz - Personal Rank Fallers

# M5F-3: PERSONAL RANK FALLERS VISUALIZATION
print("\n" + "="*120)
print("📉 PERSONAL RANK FALLERS - VISUALIZATION")
print("="*120)

import matplotlib.pyplot as plt

# Rebuild movers_df
sorted_months = sorted(personal_df['year_month'].unique())
monthly_movers = []

for i in range(1, len(sorted_months)):
    prev_month = sorted_months[i-1]
    curr_month = sorted_months[i]
    prev_data = personal_df[personal_df['year_month'] == prev_month]
    prev_rankings = prev_data.groupby('merchant_consolidated')['amount'].sum().sort_values(ascending=False)
    prev_rankings = prev_rankings.reset_index()
    prev_rankings['rank'] = range(1, len(prev_rankings) + 1)
    prev_rankings = prev_rankings.set_index('merchant_consolidated')
    
    curr_data = personal_df[personal_df['year_month'] == curr_month]
    curr_rankings = curr_data.groupby('merchant_consolidated')['amount'].sum().sort_values(ascending=False)
    curr_rankings = curr_rankings.reset_index()
    curr_rankings['rank'] = range(1, len(curr_rankings) + 1)
    curr_rankings = curr_rankings.set_index('merchant_consolidated')
    
    common = set(prev_rankings.index) & set(curr_rankings.index)
    
    for merchant in common:
        prev_rank = prev_rankings.loc[merchant, 'rank']
        curr_rank = curr_rankings.loc[merchant, 'rank']
        rank_change = prev_rank - curr_rank
        
        if prev_rank <= 100 or curr_rank <= 100:
            monthly_movers.append({'merchant': merchant, 'rank_change': rank_change})

movers_df = pd.DataFrame(monthly_movers)
top_fallers = movers_df[movers_df['rank_change'] < 0].nsmallest(50, 'rank_change')

fig, ax = plt.subplots(figsize=(12, 10))
plot_data = top_fallers.sort_values('rank_change', ascending=False)
merchants = plot_data['merchant'].str[:35]
rank_changes = plot_data['rank_change'].abs()

bars = ax.barh(range(len(merchants)), rank_changes, color='#c0392b', alpha=0.8, edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(merchants)))
ax.set_yticklabels([f"#{i+1} {m}" for i, m in enumerate(merchants)], fontsize=8)
ax.set_xlabel('Rank Positions Lost', fontsize=11, fontweight='bold')
ax.set_title('Personal Accounts - Top 50 Rank Fallers', fontsize=13, fontweight='bold', pad=15)

for i, (bar, val) in enumerate(zip(bars, rank_changes)):
    ax.text(val, bar.get_y() + bar.get_height()/2, f' ↓{int(val)}', va='center', fontsize=8, fontweight='bold')

ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.show()
print("="*120)
