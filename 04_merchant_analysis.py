# 04_merchant_analysis.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 40-51)
# M1: Top 50 merchants by spend, transactions, unique accounts
# ===========================================================================


# ===========================================================================
# 1 - Merchant Analysis
# ===========================================================================

# ---- Spend - Top 50 merchants overall ----

# ===========================================================================
# M1 - TOP 50 MERCHANTS BY TOTAL SPEND
# ===========================================================================
"""
## M1: Top 50 Merchants by Total Spend (Consolidated)
"""

top_merchants_overall = combined_df.groupby('merchant_consolidated').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique'
}).round(2)

top_merchants_overall.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts']
top_merchants_overall = top_merchants_overall.sort_values('total_amount', ascending=False).head(50)

# Format for display
display_df = top_merchants_overall.reset_index()
display_df = display_df.rename(columns={
    'merchant_consolidated': 'Merchant',
    'total_amount': 'Total Spend',
    'transaction_count': 'Transactions',
    'avg_transaction': 'Avg Transaction',
    'unique_accounts': 'Unique Accounts'
})

# Format currency columns
display_df['Total Spend'] = display_df['Total Spend'].apply(lambda x: f"${x:,.0f}")
display_df['Avg Transaction'] = display_df['Avg Transaction'].apply(lambda x: f"${x:.2f}")

print("\n" + "="*100)
print(" " * 35 + "TOP 50 MERCHANTS BY TOTAL SPEND")
print("="*100)

display(display_df)

# Summary stats
total_spend = top_merchants_overall['total_amount'].sum()
total_transactions = top_merchants_overall['transaction_count'].sum()
total_accounts = top_merchants_overall['unique_accounts'].sum()

summary = pd.DataFrame({
    'Metric': ['Total Spend (Top 50)', 'Total Transactions (Top 50)', 'Total Unique Accounts (Top 50)'],
    'Value': [f"${total_spend:,.0f}", f"{total_transactions:,.0f}", f"{total_accounts:,.0f}"]
})

print("\n")
display(summary)
print("="*100)


# Viz - Top 25 Merchants by Spend

# ===========================================================================
# M1 VISUALIZATION - Top 25 Merchants by Total Spend
# ===========================================================================

fig, ax = plt.subplots(figsize=(12, 10))

# Get top 25 and reverse order so #1 is at top
top_25 = top_merchants_overall.head(25).iloc[::-1]

merchants = [m[:40] + '...' if len(m) > 40 else m for m in top_25.index]
values = top_25['total_amount'].values

# Color gradient
colors = plt.cm.Blues(np.linspace(0.5, 0.9, 25))

bars = ax.barh(range(25), values, color=colors, edgecolor='black', linewidth=0.8)
ax.set_yticks(range(25))
ax.set_yticklabels(merchants, fontsize=10)
ax.set_xlabel('Total Spend ($)', fontsize=12, fontweight='bold')
ax.set_title('Top 25 Merchants by Total Spend', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, values)):
    ax.text(value + max(values)*0.01, bar.get_y() + bar.get_height()/2, 
            f'${value/1e6:.2f}M', va='center', fontsize=9, fontweight='bold')

# Format x-axis
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
ax.grid(axis='x', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

# Add rank labels on left side
for i, rank in enumerate(range(25, 0, -1)):
    ax.text(-max(values)*0.02, i, f'#{rank}', 
            ha='right', va='center', fontsize=9, fontweight='bold', color='gray')

plt.tight_layout()
plt.show()


# ---- Transactions - TOP 50 MERCHANTS BY TRANSACTION COUNT ----

# ===========================================================================
# M1B - TOP 50 MERCHANTS BY TRANSACTION COUNT
# ===========================================================================
"""
## M1B: Top 50 Merchants by Transaction Count (Consolidated)
"""

top_by_transactions = combined_df.groupby('merchant_consolidated').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique'
}).round(2)

top_by_transactions.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts']
top_by_transactions = top_by_transactions.sort_values('transaction_count', ascending=False).head(50)

# Format for display
display_df = top_by_transactions.reset_index()
display_df = display_df.rename(columns={
    'merchant_consolidated': 'Merchant',
    'transaction_count': 'Transactions',
    'total_amount': 'Total Spend',
    'avg_transaction': 'Avg Transaction',
    'unique_accounts': 'Unique Accounts'
})

# Format columns
display_df['Total Spend'] = display_df['Total Spend'].apply(lambda x: f"${x:,.0f}")
display_df['Avg Transaction'] = display_df['Avg Transaction'].apply(lambda x: f"${x:.2f}")

print("\n" + "="*100)
print(" " * 30 + "TOP 50 MERCHANTS BY TRANSACTION COUNT")
print("="*100)

display(display_df)

# Summary stats
total_spend = top_by_transactions['total_amount'].sum()
total_transactions = top_by_transactions['transaction_count'].sum()
total_accounts = top_by_transactions['unique_accounts'].sum()

summary = pd.DataFrame({
    'Metric': ['Total Spend (Top 50)', 'Total Transactions (Top 50)', 'Total Unique Accounts (Top 50)'],
    'Value': [f"${total_spend:,.0f}", f"{total_transactions:,.0f}", f"{total_accounts:,.0f}"]
})

print("\n")
display(summary)
print("="*100)


# Viz - Top 25 Merchants by Txn Count

# ===========================================================================
# M1B VISUALIZATION - Top 25 Merchants by Transaction Count
# ===========================================================================

fig, ax = plt.subplots(figsize=(12, 10))

# Get top 25 and reverse order so #1 is at top
top_25 = top_by_transactions.head(25).iloc[::-1]

merchants = [m[:40] + '...' if len(m) > 40 else m for m in top_25.index]
values = top_25['transaction_count'].values

# Color gradient
colors = plt.cm.Greens(np.linspace(0.5, 0.9, 25))

bars = ax.barh(range(25), values, color=colors, edgecolor='black', linewidth=0.8)
ax.set_yticks(range(25))
ax.set_yticklabels(merchants, fontsize=10)
ax.set_xlabel('Transaction Count', fontsize=12, fontweight='bold')
ax.set_title('Top 25 Merchants by Transaction Count', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, values)):
    ax.text(value + max(values)*0.01, bar.get_y() + bar.get_height()/2, 
            f'{value:,.0f}', va='center', fontsize=9, fontweight='bold')

# Format x-axis
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e3:.0f}K' if x >= 1000 else f'{x:.0f}'))
ax.grid(axis='x', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

# Add rank labels on left side
for i, rank in enumerate(range(25, 0, -1)):
    ax.text(-max(values)*0.02, i, f'#{rank}', 
            ha='right', va='center', fontsize=9, fontweight='bold', color='gray')

plt.tight_layout()
plt.show()


# ---- Accounts - TOP 50 MERCHANTS BY UNIQUE ACCOUNTS ----

# ===========================================================================
# M1C - TOP 50 MERCHANTS BY UNIQUE ACCOUNT COUNT
# ===========================================================================
"""
## M1C: Top 50 Merchants by Unique Account Count (Consolidated)
"""

top_by_accounts = combined_df.groupby('merchant_consolidated').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique'
}).round(2)

top_by_accounts.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts']
top_by_accounts = top_by_accounts.sort_values('unique_accounts', ascending=False).head(50)

# Format for display
display_df = top_by_accounts.reset_index()
display_df = display_df.rename(columns={
    'merchant_consolidated': 'Merchant',
    'unique_accounts': 'Unique Accounts',
    'transaction_count': 'Transactions',
    'total_amount': 'Total Spend',
    'avg_transaction': 'Avg Transaction'
})

# Format columns
display_df['Total Spend'] = display_df['Total Spend'].apply(lambda x: f"${x:,.0f}")
display_df['Avg Transaction'] = display_df['Avg Transaction'].apply(lambda x: f"${x:.2f}")

print("\n" + "="*100)
print(" " * 30 + "TOP 50 MERCHANTS BY UNIQUE ACCOUNT COUNT")
print("="*100)

display(display_df)

# Summary stats
total_spend = top_by_accounts['total_amount'].sum()
total_transactions = top_by_accounts['transaction_count'].sum()
total_accounts = top_by_accounts['unique_accounts'].sum()

summary = pd.DataFrame({
    'Metric': ['Total Spend (Top 50)', 'Total Transactions (Top 50)', 'Total Unique Accounts (Top 50)'],
    'Value': [f"${total_spend:,.0f}", f"{total_transactions:,.0f}", f"{total_accounts:,.0f}"]
})

print("\n")
display(summary)
print("="*100)


# VIz - Top 25 Merchants by Unique Accts