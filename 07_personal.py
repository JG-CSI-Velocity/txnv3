# 07_personal.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 76-90)
# M4: Personal merchant analysis by spend, transactions, accounts
# ===========================================================================


# ===========================================================================
# 4 - Personal Analysis
# ===========================================================================

# ---- Spend - Personal - Top 50 merchants overall ----

# ===========================================================================
# M4A - TOP 50 PERSONAL MERCHANTS BY TOTAL SPEND
# ===========================================================================
"""
## M4A: Top 50 Personal Merchants by Total Spend (Consolidated)
Analysis of merchants used by personal accounts only
"""

# Use consolidated merchant names for personal data
top_personal_spend = personal_df.groupby('merchant_consolidated').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique'
}).round(2)

top_personal_spend.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts']
top_personal_spend = top_personal_spend.sort_values('total_amount', ascending=False).head(50)

# Format for display
display_df = top_personal_spend.reset_index()
display_df = display_df.rename(columns={
    'merchant_consolidated': 'Merchant',
    'total_amount': 'Total Spend',
    'transaction_count': 'Transactions',
    'avg_transaction': 'Avg Transaction',
    'unique_accounts': 'Unique Accounts'
})

# Format columns
display_df['Total Spend'] = display_df['Total Spend'].apply(lambda x: f"${x:,.0f}")
display_df['Avg Transaction'] = display_df['Avg Transaction'].apply(lambda x: f"${x:.2f}")

print("\n" + "="*100)
print(" " * 30 + "TOP 50 PERSONAL MERCHANTS BY TOTAL SPEND")
print("="*100)

display(display_df.style.hide(axis='index'))

# Summary stats
total_spend = top_personal_spend['total_amount'].sum()
total_transactions = top_personal_spend['transaction_count'].sum()
total_accounts = top_personal_spend['unique_accounts'].sum()

# Calculate % of total personal spend
personal_total = personal_df['amount'].sum()
top_50_pct = (total_spend / personal_total) * 100

summary = pd.DataFrame({
    'Metric': [
        'Total Spend (Top 50)',
        '% of Total Personal Spend',
        'Total Transactions (Top 50)',
        'Total Personal Accounts (Top 50)',
        'Total Personal Spend (All)',
        'Total Personal Accounts (All)'
    ],
    'Value': [
        f"${total_spend:,.0f}",
        f"{top_50_pct:.1f}%",
        f"{total_transactions:,.0f}",
        f"{total_accounts:,.0f}",
        f"${personal_total:,.0f}",
        f"{personal_df['primary_account_num'].nunique():,}"
    ]
})

print("\n")
display(summary.style.hide(axis='index'))
print("="*100)


# Viz - Top 25 Personal Merchants by Spend

# ===========================================================================
# M4A VISUALIZATION - Top 25 Personal Merchants by Spend
# ===========================================================================

fig, ax = plt.subplots(figsize=(12, 10))

# Get top 25 and reverse order so #1 is at top
top_25 = top_personal_spend.head(25).iloc[::-1]

merchants = [m[:40] + '...' if len(m) > 40 else m for m in top_25.index]
values = top_25['total_amount'].values

# Color gradient - teal theme for personal
colors = plt.cm.BuGn(np.linspace(0.5, 0.9, 25))

bars = ax.barh(range(25), values, color=colors, edgecolor='black', linewidth=0.8)
ax.set_yticks(range(25))
ax.set_yticklabels(merchants, fontsize=10)
ax.set_xlabel('Total Spend ($)', fontsize=12, fontweight='bold')
ax.set_title('Top 25 Personal Merchants by Total Spend', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, values)):
    ax.text(value + max(values)*0.01, bar.get_y() + bar.get_height()/2, 
            f'${value/1e6:.2f}M' if value >= 1e6 else f'${value/1e3:.1f}K', 
            va='center', fontsize=9, fontweight='bold')

# Format x-axis
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M' if x >= 1e6 else f'${x/1e3:.0f}K'))
ax.grid(axis='x', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

# Add rank labels on left side
for i, rank in enumerate(range(25, 0, -1)):
    ax.text(-max(values)*0.02, i, f'#{rank}', 
            ha='right', va='center', fontsize=9, fontweight='bold', color='gray')

plt.tight_layout()
plt.show()


# ---- Transactions - Personal - TOP 50 MERCHANTS BY TRANSACTION COUNT ----

# ===========================================================================
# M4B - TOP 50 PERSONAL MERCHANTS BY TRANSACTION COUNT
# ===========================================================================
"""
## M4B: Top 50 Personal Merchants by Transaction Count (Consolidated)
"""

top_personal_trans = personal_df.groupby('merchant_consolidated').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique'
}).round(2)

top_personal_trans.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts']
top_personal_trans = top_personal_trans.sort_values('transaction_count', ascending=False).head(50)

# Format for display
display_df = top_personal_trans.reset_index()
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
print(" " * 28 + "TOP 50 PERSONAL MERCHANTS BY TRANSACTION COUNT")
print("="*100)

display(display_df.style.hide(axis='index'))

# Summary stats
total_spend = top_personal_trans['total_amount'].sum()
total_transactions = top_personal_trans['transaction_count'].sum()
total_accounts = top_personal_trans['unique_accounts'].sum()

summary = pd.DataFrame({
    'Metric': [
        'Total Transactions (Top 50)',
        'Total Spend (Top 50)',
        'Total Personal Accounts (Top 50)'
    ],
    'Value': [
        f"{total_transactions:,.0f}",
        f"${total_spend:,.0f}",
        f"{total_accounts:,.0f}"
    ]
})

print("\n")
display(summary.style.hide(axis='index'))
print("="*100)


# Viz - Top 25 Personal Merchants by Transaction

# ===========================================================================
# M4B VISUALIZATION - Top 25 Personal Merchants by Transaction Count
# ===========================================================================

fig, ax = plt.subplots(figsize=(12, 10))

# Get top 25 and reverse order so #1 is at top
top_25 = top_personal_trans.head(25).iloc[::-1]

merchants = [m[:40] + '...' if len(m) > 40 else m for m in top_25.index]
values = top_25['transaction_count'].values

# Color gradient
colors = plt.cm.YlGn(np.linspace(0.5, 0.9, 25))

bars = ax.barh(range(25), values, color=colors, edgecolor='black', linewidth=0.8)
ax.set_yticks(range(25))
ax.set_yticklabels(merchants, fontsize=10)
ax.set_xlabel('Transaction Count', fontsize=12, fontweight='bold')
ax.set_title('Top 25 Personal Merchants by Transaction Count', fontsize=14, fontweight='bold', pad=20)

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


# ---- Accounts - Personal - TOP 50 MERCHANTS BY UNIQUE ACCOUNTS ----

# ===========================================================================
# M4C - TOP 50 PERSONAL MERCHANTS BY UNIQUE ACCOUNT COUNT
# ===========================================================================
"""
## M4C: Top 50 Personal Merchants by Unique Account Count (Consolidated)
"""

top_personal_accounts = personal_df.groupby('merchant_consolidated').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique'
}).round(2)

top_personal_accounts.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts']
top_personal_accounts = top_personal_accounts.sort_values('unique_accounts', ascending=False).head(50)

# Format for display
display_df = top_personal_accounts.reset_index()
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
print(" " * 28 + "TOP 50 PERSONAL MERCHANTS BY UNIQUE ACCOUNT COUNT")
print("="*100)

display(display_df.style.hide(axis='index'))

# Summary stats
total_spend = top_personal_accounts['total_amount'].sum()
total_transactions = top_personal_accounts['transaction_count'].sum()
total_accounts = top_personal_accounts['unique_accounts'].sum()

summary = pd.DataFrame({
    'Metric': [
        'Total Personal Accounts (Top 50)',
        'Total Transactions (Top 50)',
        'Total Spend (Top 50)'
    ],
    'Value': [
        f"{total_accounts:,.0f}",
        f"{total_transactions:,.0f}",
        f"${total_spend:,.0f}"
    ]
})

print("\n")
display(summary.style.hide(axis='index'))
print("="*100)


# Viz - Top 25 Personal Merchants by Unique Accounts

# ===========================================================================
# M4C VISUALIZATION - Top 25 Personal Merchants by Unique Accounts
# ===========================================================================

fig, ax = plt.subplots(figsize=(12, 10))

# Get top 25 and reverse order so #1 is at top
top_25 = top_personal_accounts.head(25).iloc[::-1]

merchants = [m[:40] + '...' if len(m) > 40 else m for m in top_25.index]
values = top_25['unique_accounts'].values

# Color gradient
colors = plt.cm.RdPu(np.linspace(0.5, 0.9, 25))

bars = ax.barh(range(25), values, color=colors, edgecolor='black', linewidth=0.8)
ax.set_yticks(range(25))
ax.set_yticklabels(merchants, fontsize=10)
ax.set_xlabel('Unique Personal Account Count', fontsize=12, fontweight='bold')
ax.set_title('Top 25 Personal Merchants by Account Count', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, values)):
    ax.text(value + max(values)*0.01, bar.get_y() + bar.get_height()/2, 
            f'{int(value):,}', va='center', fontsize=9, fontweight='bold')

# Format x-axis
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e3:.1f}K' if x >= 1000 else f'{x:.0f}'))
ax.grid(axis='x', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

# Add rank labels on left side
for i, rank in enumerate(range(25, 0, -1)):
    ax.text(-max(values)*0.02, i, f'#{rank}', 
            ha='right', va='center', fontsize=9, fontweight='bold', color='gray')

plt.tight_layout()
plt.show()
