# 03_general.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 29-39)
# General Analysis: monthly summary, transaction distribution, variance
# ===========================================================================


# ===========================================================================
# =========== Analysis ===============
# ===========================================================================

# ===========================================================================
# General
# ===========================================================================

# ---- Monhtly Summary Analysis ----

# ===========================================================================
# GENERAL ANALYSIS 1 - MONTHLY SUMMARY
# ===========================================================================
"""
## Monthly Summary Analysis
"""

# Create year-month column for grouping
combined_df['year_month'] = combined_df['transaction_date'].dt.to_period('M')

# Monthly summary
monthly_summary = combined_df.groupby('year_month').agg({
    'primary_account_num': 'nunique',
    'transaction_date': 'count',
    'amount': ['sum', 'mean', 'median'],
    'merchant_name': 'nunique',
    'mcc_code': 'nunique'
}).round(2)

# Flatten column names
monthly_summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in monthly_summary.columns]
monthly_summary.rename(columns={
    'primary_account_num_nunique': 'unique_accounts',
    'transaction_date_count': 'transaction_count',
    'amount_sum': 'total_amount',
    'amount_mean': 'avg_amount',
    'amount_median': 'median_amount',
    'merchant_name_nunique': 'unique_merchants',
    'mcc_code_nunique': 'unique_mcc_codes'
}, inplace=True)

# Calculate month-over-month growth
monthly_summary['amount_growth_pct'] = monthly_summary['total_amount'].pct_change() * 100
monthly_summary['transaction_growth_pct'] = monthly_summary['transaction_count'].pct_change() * 100
monthly_summary['account_growth_pct'] = monthly_summary['unique_accounts'].pct_change() * 100

# Reset index to make year_month a column
monthly_summary_display = monthly_summary.reset_index()
monthly_summary_display['year_month'] = monthly_summary_display['year_month'].astype(str)

# Format for display
display_df = monthly_summary_display.copy()
display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"${x:,.0f}")
display_df['avg_amount'] = display_df['avg_amount'].apply(lambda x: f"${x:.2f}")
display_df['median_amount'] = display_df['median_amount'].apply(lambda x: f"${x:.2f}")
display_df['amount_growth_pct'] = display_df['amount_growth_pct'].apply(
    lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
)
display_df['transaction_growth_pct'] = display_df['transaction_growth_pct'].apply(
    lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
)
display_df['account_growth_pct'] = display_df['account_growth_pct'].apply(
    lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
)

# Rename for cleaner display
display_df = display_df.rename(columns={
    'year_month': 'Month',
    'unique_accounts': 'Accounts',
    'transaction_count': 'Transactions',
    'total_amount': 'Total Spend',
    'avg_amount': 'Avg Transaction',
    'median_amount': 'Median Transaction',
    'unique_merchants': 'Unique Merchants',
    'unique_mcc_codes': 'MCC Codes',
    'amount_growth_pct': 'Spend Growth',
    'transaction_growth_pct': 'Trans Growth',
    'account_growth_pct': 'Account Growth'
})

print("\n" + "="*120)
print(" " * 45 + "MONTHLY TRANSACTION SUMMARY")
print("="*120)

display(display_df)

# Summary statistics across all months
print("\n" + "="*120)
print(" " * 45 + "OVERALL SUMMARY STATISTICS")
print("="*120)

summary_stats = pd.DataFrame({
    'Metric': [
        'Total Months',
        'Avg Monthly Spend',
        'Total Spend (All Months)',
        'Avg Monthly Transactions',
        'Total Transactions (All Months)',
        'Avg Active Accounts/Month',
        'Peak Month (Spend)',
        'Lowest Month (Spend)'
    ],
    'Value': [
        len(monthly_summary),
        f"${monthly_summary['total_amount'].mean():,.0f}",
        f"${monthly_summary['total_amount'].sum():,.0f}",
        f"{monthly_summary['transaction_count'].mean():,.0f}",
        f"{monthly_summary['transaction_count'].sum():,.0f}",
        f"{monthly_summary['unique_accounts'].mean():,.0f}",
        f"{monthly_summary['total_amount'].idxmax()} (${monthly_summary['total_amount'].max():,.0f})",
        f"{monthly_summary['total_amount'].idxmin()} (${monthly_summary['total_amount'].min():,.0f})"
    ]
})

display(summary_stats)

print("="*120)


# ---- Transaction Distribution ----

# ===========================================================================
# GENERAL ANALYSIS 2 - TRANSACTION DISTRIBUTION BY AMOUNT
# ===========================================================================
"""
## Transaction Distribution Analysis
"""

# Define spending brackets
bins = [0, 1, 5, 10, 25, 50, 100, 500, float('inf')]
labels = ['< $1', '$1-5', '$5-10', '$10-25', '$25-50', '$50-100', '$100-500', '$500+']

# Create spending brackets column
combined_df['amount_bracket'] = pd.cut(combined_df['amount'], bins=bins, labels=labels, right=False)

# Create summary statistics
bracket_stats = []
for bracket in labels:
    bracket_data = combined_df[combined_df['amount_bracket'] == bracket]
    count = len(bracket_data)
    total_value = bracket_data['amount'].sum()
    
    bracket_stats.append({
        'Amount Range': bracket,
        'Transactions': count,
        'Trans %': (count / len(combined_df)) * 100,
        'Total Value': total_value,
        'Value %': (total_value / combined_df['amount'].sum()) * 100
    })

bracket_summary = pd.DataFrame(bracket_stats)

# Format for display
display_df = bracket_summary.copy()
display_df['Transactions'] = display_df['Transactions'].apply(lambda x: f"{x:,}")
display_df['Trans %'] = display_df['Trans %'].apply(lambda x: f"{x:.1f}%")
display_df['Total Value'] = display_df['Total Value'].apply(lambda x: f"${x:,.0f}")
display_df['Value %'] = display_df['Value %'].apply(lambda x: f"{x:.1f}%")

print("\n" + "="*100)
print(" " * 30 + "TRANSACTION DISTRIBUTION BY AMOUNT")
print("="*100)

display(display_df)

# Key insights
print("\n" + "="*100)
print(" " * 35 + "KEY INSIGHTS")
print("="*100)

insights = pd.DataFrame({
    'Insight': [
        'Most Common Range',
        'Highest Value Range',
        'Small Transactions (<$10)',
        'Large Transactions (>$100)',
        'Average Transaction'
    ],
    'Value': [
        f"{bracket_summary.loc[bracket_summary['Transactions'].idxmax(), 'Amount Range']} "
        f"({bracket_summary['Transactions'].max():,} transactions)",
        
        f"{bracket_summary.loc[bracket_summary['Total Value'].idxmax(), 'Amount Range']} "
        f"(${bracket_summary['Total Value'].max():,.0f})",
        
        f"{bracket_summary[bracket_summary['Amount Range'].isin(['< $1', '$1-5', '$5-10'])]['Trans %'].sum():.1f}% of transactions",
        
        f"{bracket_summary[bracket_summary['Amount Range'].isin(['$100-500', '$500+'])]['Trans %'].sum():.1f}% of transactions, "
        f"{bracket_summary[bracket_summary['Amount Range'].isin(['$100-500', '$500+'])]['Value %'].sum():.1f}% of value",
        
        f"${combined_df['amount'].mean():.2f}"
    ]
})

display(insights)
print("="*100)


# ===========================================================================
# GENERAL ANALYSIS 2A - VISUALIZATION: Transaction Volume
# ===========================================================================

fig, ax = plt.subplots(figsize=(12, 7))

colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51', '#5D576B', '#F4D35E']

bars = ax.bar(bracket_summary['Amount Range'], 
              bracket_summary['Transactions'], 
              color=colors, 
              edgecolor='black', 
              linewidth=1.5,
              alpha=0.8)

ax.set_xlabel('Amount Range', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
ax.set_title('Transaction Volume by Amount Range', fontsize=14, fontweight='bold', pad=20)
ax.tick_params(axis='x', rotation=45)

# Add value labels on bars
for bar, value, pct in zip(bars, bracket_summary['Transactions'], bracket_summary['Trans %']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{value:,.0f}\n({pct:.1f}%)', 
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Add grid
ax.yaxis.grid(True, linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

# Format y-axis
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))

plt.tight_layout()
plt.show()


# ---- Monthly Transaction distribution variance ----

# ===========================================================================
# GENERAL ANALYSIS 3 - MONTHLY TRANSACTION DISTRIBUTION VARIANCE
# ===========================================================================
"""
## Monthly Distribution by Amount Bracket
"""

# Create monthly distribution data
monthly_brackets = pd.crosstab(combined_df['year_month'], combined_df['amount_bracket'])
monthly_brackets_pct = pd.crosstab(combined_df['year_month'], combined_df['amount_bracket'], normalize='index') * 100

# Format for display
display_df = monthly_brackets_pct.copy()
display_df.index = display_df.index.astype(str)
display_df = display_df.round(1)

# Add column formatting
for col in display_df.columns:
    display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%")

print("\n" + "="*100)
print(" " * 30 + "MONTHLY DISTRIBUTION BY AMOUNT BRACKET (%)")
print("="*100)

display(display_df)

# Volatility analysis
print("\n" + "="*100)
print(" " * 35 + "VOLATILITY ANALYSIS")
print("="*100)

volatility_stats = []
for bracket in labels:
    variance = monthly_brackets_pct[bracket].std()
    mean_pct = monthly_brackets_pct[bracket].mean()
    min_pct = monthly_brackets_pct[bracket].min()
    max_pct = monthly_brackets_pct[bracket].max()
    range_pct = max_pct - min_pct
    
    volatility_stats.append({
        'Amount Range': bracket,
        'Avg %': f"{mean_pct:.1f}%",
        'Std Dev': f"{variance:.2f}%",
        'Min %': f"{min_pct:.1f}%",
        'Max %': f"{max_pct:.1f}%",
        'Range': f"{range_pct:.1f}%",
        'Stability': 'Stable' if variance < 1.0 else 'Moderate' if variance < 2.0 else 'Volatile'
    })

volatility_df = pd.DataFrame(volatility_stats)
display(volatility_df)

# Key insights
print("\n" + "="*100)
print(" " * 40 + "KEY INSIGHTS")
print("="*100)

most_stable = volatility_df.loc[volatility_df['Std Dev'].str.replace('%', '').astype(float).idxmin(), 'Amount Range']
most_volatile = volatility_df.loc[volatility_df['Std Dev'].str.replace('%', '').astype(float).idxmax(), 'Amount Range']
dominant_bracket = volatility_df.loc[volatility_df['Avg %'].str.replace('%', '').astype(float).idxmax(), 'Amount Range']

insights = pd.DataFrame({
    'Insight': [
        'Most Consistent Range',
        'Most Volatile Range',
        'Dominant Transaction Range',
        'Small Transactions Trend (<$10)',
        'Large Transactions Trend (>$100)'
    ],
    'Finding': [
        f"{most_stable} - Most stable across months",
        f"{most_volatile} - Highest month-to-month variation",
        f"{dominant_bracket} - Highest average percentage",
        f"{monthly_brackets_pct[['< $1', '$1-5', '$5-10']].sum(axis=1).mean():.1f}% average, "
        f"{monthly_brackets_pct[['< $1', '$1-5', '$5-10']].sum(axis=1).std():.2f}% volatility",
        f"{monthly_brackets_pct[['$100-500', '$500+']].sum(axis=1).mean():.1f}% average, "
        f"{monthly_brackets_pct[['$100-500', '$500+']].sum(axis=1).std():.2f}% volatility"
    ]
})

display(insights)
print("="*100)


# ===========================================================================
# GENERAL ANALYSIS 3 - VISUALIZATION: Distribution Over Time
# ===========================================================================

fig, ax = plt.subplots(figsize=(14, 8))

# Prepare data for stacked bar chart
months = [str(m) for m in monthly_brackets_pct.index]
x_pos = np.arange(len(months))

# Define colors for each bracket
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']

# Create stacked bar chart
bottom = np.zeros(len(months))
for i, bracket in enumerate(labels):
    values = monthly_brackets_pct[bracket].values
    bars = ax.bar(x_pos, values, bottom=bottom, label=bracket, color=colors[i], 
                   width=0.8, edgecolor='white', linewidth=0.5)
    
    # Add percentage labels for larger segments
    for j, (bar, val) in enumerate(zip(bars, values)):
        if val > 5:  # Only label segments > 5%
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., bottom[j] + height/2,
                   f'{val:.0f}%', ha='center', va='center', fontsize=8, 
                   fontweight='bold', color='white')
    
    bottom += values

ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Percentage of Transactions', fontsize=12, fontweight='bold')
ax.set_title('Monthly Transaction Distribution by Amount Bracket (Stacked 100%)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x_pos)
ax.set_xticklabels(months, rotation=45, ha='right')
ax.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1, title='Amount Range')

# Add percentage labels on y-axis
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}%'))
ax.set_ylim(0, 100)

# Add grid
ax.yaxis.grid(True, linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

plt.tight_layout()
plt.show()
