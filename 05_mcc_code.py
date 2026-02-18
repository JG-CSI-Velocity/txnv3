# 05_mcc_code.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 52-62)
# M2: MCC code analysis by accounts, transactions, spend
# ===========================================================================


# ===========================================================================
# 2 - MCC Code
# ===========================================================================

# ---- TOp 50 MCC Code by Unique Accounts ----

# ===========================================================================
# M2A - TOP 50 MERCHANT CATEGORIES (MCC) BY UNIQUE ACCOUNTS
# ===========================================================================
"""
## M2A: Top 50 Merchant Categories by Unique Account Count
Based on MCC (Merchant Category Code) groupings
"""

top_mcc_by_accounts = combined_df.groupby('mcc_code').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique',
    'merchant_name': 'nunique'
}).round(2)

top_mcc_by_accounts.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts', 'num_merchants']
top_mcc_by_accounts = top_mcc_by_accounts.sort_values('unique_accounts', ascending=False).head(50)

# Format for display
display_df = top_mcc_by_accounts.reset_index()
display_df = display_df.rename(columns={
    'mcc_code': 'MCC Code',
    'unique_accounts': 'Unique Accounts',
    'num_merchants': 'Merchants',
    'transaction_count': 'Transactions',
    'total_amount': 'Total Spend',
    'avg_transaction': 'Avg Transaction'
})

# Format columns
display_df['Total Spend'] = display_df['Total Spend'].apply(lambda x: f"${x:,.0f}")
display_df['Avg Transaction'] = display_df['Avg Transaction'].apply(lambda x: f"${x:.2f}")

print("\n" + "="*110)
print(" " * 30 + "TOP 50 MERCHANT CATEGORIES BY UNIQUE ACCOUNT COUNT")
print(" " * 40 + "(Based on MCC Codes)")
print("="*110)

display(display_df)

# Summary stats
total_spend = top_mcc_by_accounts['total_amount'].sum()
total_transactions = top_mcc_by_accounts['transaction_count'].sum()
total_accounts = top_mcc_by_accounts['unique_accounts'].sum()
total_merchants = top_mcc_by_accounts['num_merchants'].sum()

summary = pd.DataFrame({
    'Metric': [
        'Total MCC Categories (Top 50)', 
        'Total Unique Accounts (Top 50)', 
        'Total Merchants (Top 50)',
        'Total Transactions (Top 50)', 
        'Total Spend (Top 50)'
    ],
    'Value': [
        f"{len(top_mcc_by_accounts)}",
        f"{total_accounts:,.0f}",
        f"{total_merchants:,.0f}",
        f"{total_transactions:,.0f}", 
        f"${total_spend:,.0f}"
    ]
})

print("\n")
display(summary)
print("="*110)


# ---- TOP 50 MERCHANT CATEGORIES (MCC) BY TRANSACTION COUNT ----

# ===========================================================================
# M2B - TOP 50 MERCHANT CATEGORIES (MCC) BY TRANSACTION COUNT
# ===========================================================================
"""
## M2B: Top 50 Merchant Categories by Transaction Count
"""

top_mcc_by_trans = combined_df.groupby('mcc_code').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique',
    'merchant_name': 'nunique'
}).round(2)

top_mcc_by_trans.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts', 'num_merchants']
top_mcc_by_trans = top_mcc_by_trans.sort_values('transaction_count', ascending=False).head(50)

# Format for display
display_df = top_mcc_by_trans.reset_index()
display_df = display_df.rename(columns={
    'mcc_code': 'MCC Code',
    'transaction_count': 'Transactions',
    'unique_accounts': 'Unique Accounts',
    'num_merchants': 'Merchants',
    'total_amount': 'Total Spend',
    'avg_transaction': 'Avg Transaction'
})

# Format columns
display_df['Total Spend'] = display_df['Total Spend'].apply(lambda x: f"${x:,.0f}")
display_df['Avg Transaction'] = display_df['Avg Transaction'].apply(lambda x: f"${x:.2f}")

print("\n" + "="*110)
print(" " * 30 + "TOP 50 MERCHANT CATEGORIES BY TRANSACTION COUNT")
print("="*110)

display(display_df)

# Summary stats
total_spend = top_mcc_by_trans['total_amount'].sum()
total_transactions = top_mcc_by_trans['transaction_count'].sum()
total_accounts = top_mcc_by_trans['unique_accounts'].sum()

summary = pd.DataFrame({
    'Metric': [
        'Total Transactions (Top 50)', 
        'Total Spend (Top 50)', 
        'Total Unique Accounts (Top 50)'
    ],
    'Value': [
        f"{total_transactions:,.0f}", 
        f"${total_spend:,.0f}",
        f"{total_accounts:,.0f}"
    ]
})

print("\n")
display(summary)
print("="*110)


# ---- TOP 50 MERCHANT CATEGORIES (MCC) BY TOTAL SPEND ----

# ===========================================================================
# M2C - TOP 50 MERCHANT CATEGORIES (MCC) BY TOTAL SPEND
# ===========================================================================
"""
## M2C: Top 50 Merchant Categories by Total Spend
"""

top_mcc_by_spend = combined_df.groupby('mcc_code').agg({
    'amount': ['sum', 'count', 'mean'],
    'primary_account_num': 'nunique',
    'merchant_name': 'nunique'
}).round(2)

top_mcc_by_spend.columns = ['total_amount', 'transaction_count', 'avg_transaction', 'unique_accounts', 'num_merchants']
top_mcc_by_spend = top_mcc_by_spend.sort_values('total_amount', ascending=False).head(50)

# Format for display
display_df = top_mcc_by_spend.reset_index()
display_df = display_df.rename(columns={
    'mcc_code': 'MCC Code',
    'total_amount': 'Total Spend',
    'unique_accounts': 'Unique Accounts',
    'transaction_count': 'Transactions',
    'num_merchants': 'Merchants',
    'avg_transaction': 'Avg Transaction'
})

# Format columns
display_df['Total Spend'] = display_df['Total Spend'].apply(lambda x: f"${x:,.0f}")
display_df['Avg Transaction'] = display_df['Avg Transaction'].apply(lambda x: f"${x:.2f}")

print("\n" + "="*110)
print(" " * 35 + "TOP 50 MERCHANT CATEGORIES BY TOTAL SPEND")
print("="*110)

display(display_df)

# Summary stats
total_spend = top_mcc_by_spend['total_amount'].sum()
total_transactions = top_mcc_by_spend['transaction_count'].sum()
total_accounts = top_mcc_by_spend['unique_accounts'].sum()

summary = pd.DataFrame({
    'Metric': [
        'Total Spend (Top 50)', 
        'Total Transactions (Top 50)', 
        'Total Unique Accounts (Top 50)'
    ],
    'Value': [
        f"${total_spend:,.0f}",
        f"{total_transactions:,.0f}", 
        f"{total_accounts:,.0f}"
    ]
})

print("\n")
display(summary)
print("="*110)


# ---- Viz - MCC Comparison ----

# ===========================================================================
# M2D VISUALIZATION - Top 20 MCC Categories Comparison
# ===========================================================================
"""
## M2D: MCC Category Comparison - Top 20 by Spend
"""
if len(top_mcc_by_spend) == 0:
    print("No MCC data available for this client — skipping M2D visualization.")
else:    
    fig, axes = plt.subplots(1, 3, figsize=(18, 8))
    
    # Get top 20 by spend
    top_20_mcc = top_mcc_by_spend.head(20).iloc[::-1]
    
    mcc_codes = [str(code) for code in top_20_mcc.index]
    
    # Chart 1: Total Spend
    ax1 = axes[0]
    values1 = top_20_mcc['total_amount'].values
    colors1 = plt.cm.Blues(np.linspace(0.5, 0.9, 20))
    
    bars1 = ax1.barh(range(20), values1, color=colors1, edgecolor='black', linewidth=0.5)
    ax1.set_yticks(range(20))
    ax1.set_yticklabels(mcc_codes, fontsize=9)
    ax1.set_xlabel('Total Spend ($)', fontsize=10, fontweight='bold')
    ax1.set_title('By Total Spend', fontsize=11, fontweight='bold')
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
    ax1.grid(axis='x', linestyle='--', alpha=0.3)
    ax1.set_axisbelow(True)
    
    # Chart 2: Transaction Count
    ax2 = axes[1]
    values2 = top_20_mcc['transaction_count'].values
    colors2 = plt.cm.Greens(np.linspace(0.5, 0.9, 20))
    
    bars2 = ax2.barh(range(20), values2, color=colors2, edgecolor='black', linewidth=0.5)
    ax2.set_yticks(range(20))
    ax2.set_yticklabels([''] * 20)  # Hide y-labels for middle chart
    ax2.set_xlabel('Transactions', fontsize=10, fontweight='bold')
    ax2.set_title('By Transaction Count', fontsize=11, fontweight='bold')
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
    ax2.grid(axis='x', linestyle='--', alpha=0.3)
    ax2.set_axisbelow(True)
    
    # Chart 3: Unique Accounts
    ax3 = axes[2]
    values3 = top_20_mcc['unique_accounts'].values
    colors3 = plt.cm.Oranges(np.linspace(0.5, 0.9, 20))
    
    bars3 = ax3.barh(range(20), values3, color=colors3, edgecolor='black', linewidth=0.5)
    ax3.set_yticks(range(20))
    ax3.set_yticklabels([''] * 20)  # Hide y-labels for right chart
    ax3.set_xlabel('Unique Accounts', fontsize=10, fontweight='bold')
    ax3.set_title('By Account Count', fontsize=11, fontweight='bold')
    ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e3:.1f}K' if x >= 1000 else f'{x:.0f}'))
    ax3.grid(axis='x', linestyle='--', alpha=0.3)
    ax3.set_axisbelow(True)
    
    # Overall title
    fig.suptitle('Top 20 MCC Categories - Three Perspectives', fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.show()
