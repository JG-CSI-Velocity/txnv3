# 12_campaigns.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 263-324)
# Campaigns: mail campaigns, spend campaigns, ladder movement
# ===========================================================================


# ===========================================================================
# Mail Campaigns
# ===========================================================================

# Examine the mail campaign data - ONLY actual campaign columns
print("MAIL CAMPAIGN ANALYSIS")
print("="*80)

# Identify ONLY campaign mail/response columns (format: MmmYY Mail/Resp)
import re
mail_pattern = re.compile(r'^[A-Z][a-z]{2}\d{2} Mail$')  # Apr25 Mail, Jun25 Mail, etc.
resp_pattern = re.compile(r'^[A-Z][a-z]{2}\d{2} Resp$')   # Apr25 Resp, Jun25 Resp, etc.

mail_columns = [col for col in rewards_df.columns if mail_pattern.match(col)]
resp_columns = [col for col in rewards_df.columns if resp_pattern.match(col)]

print(f"Found {len(mail_columns)} mail campaigns:")
for col in mail_columns:
    print(f"  • {col}")

print(f"\nCorresponding response columns:")
for col in resp_columns:
    print(f"  • {col}")

# Analyze each campaign
for mail_col in mail_columns:
    campaign_month = mail_col.replace(' Mail', '')
    resp_col = f"{campaign_month} Resp"
    
    # Get offer distribution
    offers = rewards_df[mail_col].value_counts()
    total_mailed = rewards_df[mail_col].notna().sum()
    
    # Get response data
    response_data = rewards_df[resp_col]
    
    # Count actual responders (exclude NU 1-4 as they are non-responders)
    non_responder_patterns = ['NU 1', 'NU 2', 'NU 3', 'NU 4']
    actual_responders = 0
    
    if resp_col in rewards_df.columns:
        # Count rows with response data that are NOT non-responders
        resp_values = response_data.dropna()
        actual_responders = len(resp_values)
        
        # Subtract non-responders if they exist in the data
        for pattern in non_responder_patterns:
            non_resp_count = (resp_values.astype(str).str.contains(pattern, na=False)).sum()
            actual_responders -= non_resp_count
    
    response_rate = (actual_responders / total_mailed * 100) if total_mailed > 0 else 0
    
    print(f"\n{campaign_month} Campaign:")
    print(f"  Total Mailed: {total_mailed:,}")
    print(f"  Actual Responders: {actual_responders:,}")
    print(f"  Response Rate: {response_rate:.1f}%")
    
    if len(offers) > 0:
        print(f"  Offers sent:")
        for offer, count in offers.items():
            pct = (count / total_mailed * 100)
            threshold = offer.split('-')[-1] if '-' in str(offer) else '5'  # Extract threshold
            print(f"    {offer}: {count:,} ({pct:.1f}%) - Must swipe {threshold}+ times")


# Analyze transaction behavior of responders vs non-responders
print("LINKING CAMPAIGN RESPONDERS TO TRANSACTION DATA")
print("="*80)

# For each campaign, analyze the transaction behavior
for mail_col in mail_columns:
    campaign_month = mail_col.replace(' Mail', '')
    resp_col = f"{campaign_month} Resp"
    
    # Get the measurement month dynamically
    measure_month_str = get_next_month_col(campaign_month)
    
    print(f"\n{campaign_month} Campaign Analysis:")
    print(f"  Campaign sent: {campaign_month}")
    print(f"  Performance measured: {measure_month_str} (following month)")
    print("-"*60)
    
    # Get campaign accounts
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    
    # Get offer types
    offer_types = campaign_accounts[mail_col].unique()
    
    # Analyze by offer type
    for offer in sorted([o for o in offer_types if pd.notna(o)]):
        offer_accounts = campaign_accounts[campaign_accounts[mail_col] == offer]
        
        # FIXED: Properly identify responders based on offer type
        if 'NU' in offer:
            # For NU offers, exclude NU 1-4 as non-responders
            responders = offer_accounts[
                (offer_accounts[resp_col].notna()) & 
                (~offer_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
            ]
            non_responders = offer_accounts[
                (offer_accounts[resp_col].isna()) | 
                (offer_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
            ]
        else:
            # For threshold offers (TH-X)
            responders = offer_accounts[offer_accounts[resp_col].notna()]
            non_responders = offer_accounts[offer_accounts[resp_col].isna()]
        
        # Extract threshold from offer name
        if '-' in str(offer):
            threshold = int(offer.split('-')[1])
        else:
            threshold = 5  # NU defaults to 5
        
        response_rate = (len(responders) / len(offer_accounts) * 100) if len(offer_accounts) > 0 else 0
        
        print(f"\n  {offer} (Threshold: {threshold}+ swipes)")
        print(f"    Sent to: {len(offer_accounts):,} accounts")
        print(f"    Responders: {len(responders):,} ({response_rate:.1f}%)")
        
        # Get spending data for measurement month
        month_spend_col = f"{measure_month_str} Spend"
        month_swipe_col = f"{measure_month_str} Swipes"
        
        if month_spend_col in rewards_df.columns and month_swipe_col in rewards_df.columns:
            # Compare responders vs non-responders
            resp_spend = responders[month_spend_col].mean() if len(responders) > 0 else 0
            non_resp_spend = non_responders[month_spend_col].mean() if len(non_responders) > 0 else 0
            
            resp_swipes = responders[month_swipe_col].mean() if len(responders) > 0 else 0
            non_resp_swipes = non_responders[month_swipe_col].mean() if len(non_responders) > 0 else 0
            
            spend_lift = ((resp_spend - non_resp_spend) / non_resp_spend * 100) if non_resp_spend > 0 else 0
            swipe_lift = ((resp_swipes - non_resp_swipes) / non_resp_swipes * 100) if non_resp_swipes > 0 else 0
            
            print(f"    Avg Spend - Responders: ${resp_spend:.2f} | Non-Resp: ${non_resp_spend:.2f} | Lift: {spend_lift:+.1f}%")
            print(f"    Avg Swipes - Responders: {resp_swipes:.1f} | Non-Resp: {non_resp_swipes:.1f} | Lift: {swipe_lift:+.1f}%")
            
            # Verify responders met threshold
            if resp_swipes >= threshold:
                print(f"    ✓ Responders exceeded threshold by {resp_swipes - threshold:.1f} swipes")
            else:
                print(f"    ✗ Responders averaged below threshold (gap: {threshold - resp_swipes:.1f} swipes)")


def create_campaign_response_chart(mail_col, rewards_df):
    """Create response rate chart for a campaign"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    
    # Get campaign data
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    unique_offers = sorted(campaign_accounts[mail_col].unique())
    
    # Prepare data
    offer_stats = []
    for offer in unique_offers:
        offer_accounts = campaign_accounts[campaign_accounts[mail_col] == offer]
        
        if 'NU' in offer:
            responders = offer_accounts[
                (offer_accounts[resp_col].notna()) & 
                (~offer_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
            ]
        else:
            responders = offer_accounts[offer_accounts[resp_col].notna()]
        
        offer_stats.append({
            'offer': offer,
            'sent': len(offer_accounts),
            'responded': len(responders),
            'rate': (len(responders) / len(offer_accounts) * 100) if len(offer_accounts) > 0 else 0
        })
    
    # Create chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    offers = [s['offer'] for s in offer_stats]
    rates = [s['rate'] for s in offer_stats]
    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(offers)))
    
    bars = ax.bar(offers, rates, color=colors, edgecolor='black')
    
    for bar, stat in zip(bars, offer_stats):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
               f'{stat["rate"]:.1f}%\n({stat["responded"]}/{stat["sent"]})',
               ha='center', va='bottom', fontsize=10)
    
    ax.set_title(f'{campaign} Campaign - Response Rates by Offer', fontsize=14, fontweight='bold')
    ax.set_ylabel('Response Rate (%)', fontsize=12)
    ax.set_xlabel('Offer Type', fontsize=12)
    ax.set_ylim(0, max(rates) * 1.2)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.show()

# Run for each campaign
for mail_col in mail_columns:
    create_campaign_response_chart(mail_col, rewards_df)


def create_campaign_lift_chart(mail_col, rewards_df):
    """Create lift analysis chart for a campaign"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    measure_month = get_next_month_col(campaign)
    
    # Check if measurement month exists in data
    month_spend_col = f"{measure_month} Spend"
    month_swipe_col = f"{measure_month} Swipes"
    
    if month_spend_col not in rewards_df.columns:
        print(f"{campaign} Campaign: Measurement month {measure_month} not yet available in data")
        return
    
    # Get campaign data
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    unique_offers = sorted(campaign_accounts[mail_col].unique())
    
    # Calculate lifts
    offer_lifts = []
    for offer in unique_offers:
        offer_accounts = campaign_accounts[campaign_accounts[mail_col] == offer]
        
        if 'NU' in offer:
            responders = offer_accounts[
                (offer_accounts[resp_col].notna()) & 
                (~offer_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
            ]
        else:
            responders = offer_accounts[offer_accounts[resp_col].notna()]
        
        non_responders = offer_accounts.drop(responders.index)
        
        resp_spend = responders[month_spend_col].mean() if len(responders) > 0 else 0
        non_resp_spend = non_responders[month_spend_col].mean() if len(non_responders) > 0 else 0
        
        resp_swipes = responders[month_swipe_col].mean() if len(responders) > 0 else 0
        non_resp_swipes = non_responders[month_swipe_col].mean() if len(non_responders) > 0 else 0
        
        spend_lift = ((resp_spend - non_resp_spend) / non_resp_spend * 100) if non_resp_spend > 0 else 0
        swipe_lift = ((resp_swipes - non_resp_swipes) / non_resp_swipes * 100) if non_resp_swipes > 0 else 0
        
        offer_lifts.append({
            'offer': offer,
            'spend_lift': spend_lift,
            'swipe_lift': swipe_lift,
            'resp_spend': resp_spend,
            'non_resp_spend': non_resp_spend,
            'resp_swipes': resp_swipes,
            'non_resp_swipes': non_resp_swipes
        })
    
    # Create chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    offers = [s['offer'] for s in offer_lifts]
    spend_lifts = [s['spend_lift'] for s in offer_lifts]
    swipe_lifts = [s['swipe_lift'] for s in offer_lifts]
    
    # Spend lift chart
    colors1 = ['green' if lift > 0 else 'red' for lift in spend_lifts]
    bars1 = ax1.bar(offers, spend_lifts, color=colors1, alpha=0.7, edgecolor='black')
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax1.set_title(f'{campaign} - Spending Lift in {measure_month}', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Lift (%)', fontsize=11)
    ax1.set_xlabel('Offer Type', fontsize=11)
    
    for bar, lift in zip(bars1, spend_lifts):
        ax1.text(bar.get_x() + bar.get_width()/2., 
                bar.get_height() + 2 if lift > 0 else bar.get_height() - 2,
                f'{lift:.1f}%', ha='center', 
                va='bottom' if lift > 0 else 'top', fontsize=9)
    
    # Swipe lift chart
    colors2 = ['green' if lift > 0 else 'red' for lift in swipe_lifts]
    bars2 = ax2.bar(offers, swipe_lifts, color=colors2, alpha=0.7, edgecolor='black')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_title(f'{campaign} - Swipe Lift in {measure_month}', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Lift (%)', fontsize=11)
    ax2.set_xlabel('Offer Type', fontsize=11)
    
    for bar, lift in zip(bars2, swipe_lifts):
        ax2.text(bar.get_x() + bar.get_width()/2., 
                bar.get_height() + 5 if lift > 0 else bar.get_height() - 5,
                f'{lift:.1f}%', ha='center', 
                va='bottom' if lift > 0 else 'top', fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"{campaign} Campaign - {measure_month} Performance:")
    print("-"*70)
    for lift in offer_lifts:
        print(f"{lift['offer']}: Spend Lift: {lift['spend_lift']:+.1f}% | Swipe Lift: {lift['swipe_lift']:+.1f}%")

# Run for each campaign
for mail_col in mail_columns:
    create_campaign_lift_chart(mail_col, rewards_df)
    print()


def analyze_transaction_patterns(mail_col, rewards_df):
    """Analyze transaction types and sizes for responders vs non-responders"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    measure_month = get_next_month_col(campaign)
    
    # Check if measurement month exists
    pin_col = f"{measure_month} PIN $"
    sig_col = f"{measure_month} Sig $"
    
    if pin_col not in rewards_df.columns:
        print(f"{campaign} Campaign: {measure_month} transaction data not yet available")
        return
    
    # Get campaign accounts
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    unique_offers = sorted(campaign_accounts[mail_col].unique())
    
    # Prepare data for analysis
    transaction_patterns = []
    
    for offer in unique_offers:
        offer_accounts = campaign_accounts[campaign_accounts[mail_col] == offer]
        
        # Identify responders
        if 'NU' in offer:
            responders = offer_accounts[
                (offer_accounts[resp_col].notna()) & 
                (~offer_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
            ]
        else:
            responders = offer_accounts[offer_accounts[resp_col].notna()]
        
        non_responders = offer_accounts.drop(responders.index)
        
        # Get PIN vs SIG breakdown
        resp_pin = responders[pin_col].mean() if len(responders) > 0 else 0
        resp_sig = responders[sig_col].mean() if len(responders) > 0 else 0
        non_resp_pin = non_responders[pin_col].mean() if len(non_responders) > 0 else 0
        non_resp_sig = non_responders[sig_col].mean() if len(non_responders) > 0 else 0
        
        # Calculate average transaction size
        swipe_col = f"{measure_month} Swipes"
        spend_col = f"{measure_month} Spend"
        
        resp_avg_trans = (responders[spend_col].sum() / responders[swipe_col].sum() 
                         if responders[swipe_col].sum() > 0 else 0)
        non_resp_avg_trans = (non_responders[spend_col].sum() / non_responders[swipe_col].sum() 
                             if non_responders[swipe_col].sum() > 0 else 0)
        
        transaction_patterns.append({
            'offer': offer,
            'resp_pin': resp_pin,
            'resp_sig': resp_sig,
            'non_resp_pin': non_resp_pin,
            'non_resp_sig': non_resp_sig,
            'resp_avg_trans': resp_avg_trans,
            'non_resp_avg_trans': non_resp_avg_trans
        })
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Chart 1: PIN vs SIG spending
    offers = [d['offer'] for d in transaction_patterns]
    x = np.arange(len(offers))
    width = 0.35
    
    resp_pins = [d['resp_pin'] for d in transaction_patterns]
    resp_sigs = [d['resp_sig'] for d in transaction_patterns]
    
    bottom_resp = np.zeros(len(offers))
    ax1.bar(x - width/2, resp_pins, width, label='PIN', color='#FF6B6B', alpha=0.8)
    ax1.bar(x - width/2, resp_sigs, width, bottom=resp_pins, label='SIG', color='#4ECDC4', alpha=0.8)
    
    non_resp_pins = [d['non_resp_pin'] for d in transaction_patterns]
    non_resp_sigs = [d['non_resp_sig'] for d in transaction_patterns]
    
    ax1.bar(x + width/2, non_resp_pins, width, color='#FF6B6B', alpha=0.4)
    ax1.bar(x + width/2, non_resp_sigs, width, bottom=non_resp_pins, color='#4ECDC4', alpha=0.4)
    
    ax1.set_title(f'{campaign} - PIN vs Signature Spending in {measure_month}', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Spend ($)', fontsize=11)
    ax1.set_xlabel('Offer Type (Solid=Responders, Faded=Non-Resp)', fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(offers)
    ax1.legend()
    
    # Chart 2: Average transaction size
    resp_avg = [d['resp_avg_trans'] for d in transaction_patterns]
    non_resp_avg = [d['non_resp_avg_trans'] for d in transaction_patterns]
    
    ax2.bar(x - width/2, resp_avg, width, label='Responders', color='#2E86AB', alpha=0.8)
    ax2.bar(x + width/2, non_resp_avg, width, label='Non-Responders', color='#A23B72', alpha=0.8)
    
    ax2.set_title(f'{campaign} - Average Transaction Size in {measure_month}', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Average Transaction Size ($)', fontsize=11)
    ax2.set_xlabel('Offer Type', fontsize=11)
    ax2.set_xticks(x)
    ax2.set_xticklabels(offers)
    ax2.legend()
    
    # Add value labels
    for i, (r, n) in enumerate(zip(resp_avg, non_resp_avg)):
        ax2.text(i - width/2, r + 1, f'${r:.0f}', ha='center', va='bottom', fontsize=9)
        ax2.text(i + width/2, n + 1, f'${n:.0f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\n{campaign} - Transaction Pattern Analysis ({measure_month})")
    print("="*80)
    print(f"{'Offer':<8} {'---Responders---':^30} {'---Non-Responders---':^30}")
    print(f"{'':8} {'PIN $':>10} {'SIG $':>10} {'Avg Size':>10} {'PIN $':>10} {'SIG $':>10} {'Avg Size':>10}")
    print("-"*80)
    
    for d in transaction_patterns:
        print(f"{d['offer']:<8} ${d['resp_pin']:>9.2f} ${d['resp_sig']:>9.2f} ${d['resp_avg_trans']:>9.2f} "
              f"${d['non_resp_pin']:>9.2f} ${d['non_resp_sig']:>9.2f} ${d['non_resp_avg_trans']:>9.2f}")

# Run for each campaign
for mail_col in mail_columns:
    analyze_transaction_patterns(mail_col, rewards_df)
    print()


def analyze_transaction_buckets_campaign(mail_col, rewards_df, combined_df):
    """Analyze how responders vs non-responders distribute across transaction size buckets"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    measure_month = get_next_month_col(campaign)
    
    # Parse month/year for filtering transaction data
    month_num, year = parse_campaign_month(measure_month)
    
    # Filter transaction data for measurement month
    measure_trans = combined_df[
        (combined_df['transaction_date'].dt.month == month_num) & 
        (combined_df['transaction_date'].dt.year == year)
    ].copy()
    
    if len(measure_trans) == 0:
        print(f"{campaign} Campaign: {measure_month} transaction detail not yet available")
        return
    
    # Get campaign accounts
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    
    # Get responder account numbers
    if 'NU' in campaign_accounts[mail_col].iloc[0]:
        responder_accounts = campaign_accounts[
            (campaign_accounts[resp_col].notna()) & 
            (~campaign_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
        ][' Acct Number'].values if ' Acct Number' in campaign_accounts.columns else []
    else:
        responder_accounts = campaign_accounts[campaign_accounts[resp_col].notna()][' Acct Number'].values if ' Acct Number' in campaign_accounts.columns else []
    
    non_responder_accounts = campaign_accounts[~campaign_accounts[' Acct Number'].isin(responder_accounts)][' Acct Number'].values if ' Acct Number' in campaign_accounts.columns else []
    
    # Match with transaction data (using hashed account numbers)
    resp_trans = measure_trans[measure_trans['primary_account_num'].isin(responder_accounts)]
    non_resp_trans = measure_trans[measure_trans['primary_account_num'].isin(non_responder_accounts)]
    
    # Calculate distribution across buckets
    bins = [0, 1, 5, 10, 25, 50, 100, 500, float('inf')]
    labels = ['< $1', '$1-5', '$5-10', '$10-25', '$25-50', '$50-100', '$100-500', '$500+']
    
    resp_dist = pd.cut(resp_trans['amount'], bins=bins, labels=labels).value_counts(normalize=True) * 100
    non_resp_dist = pd.cut(non_resp_trans['amount'], bins=bins, labels=labels).value_counts(normalize=True) * 100
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(labels))
    width = 0.35
    
    resp_values = [resp_dist.get(label, 0) for label in labels]
    non_resp_values = [non_resp_dist.get(label, 0) for label in labels]
    
    bars1 = ax.bar(x - width/2, resp_values, width, label=f'Responders', color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, non_resp_values, width, label=f'Non-Responders', color='#A23B72', alpha=0.8)
    
    ax.set_title(f'{campaign} Campaign - Transaction Size Distribution in {measure_month}', 
                 fontsize=14, fontweight='bold')
    ax.set_ylabel('% of Transactions', fontsize=12)
    ax.set_xlabel('Transaction Amount Range', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    
    # Add value labels
    for bar, val in zip(bars1, resp_values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    
    for bar, val in zip(bars2, non_resp_values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\n{campaign} - Transaction Size Distribution ({measure_month})")
    print("="*80)
    print(f"{'Amount Range':<15} {'Responders %':>15} {'Non-Resp %':>15} {'Difference':>15}")
    print("-"*80)
    
    for label in labels:
        resp_pct = resp_dist.get(label, 0)
        non_resp_pct = non_resp_dist.get(label, 0)
        diff = resp_pct - non_resp_pct
        print(f"{label:<15} {resp_pct:>14.1f}% {non_resp_pct:>14.1f}% {diff:>+14.1f}%")

# Run for each campaign
for mail_col in mail_columns:
    analyze_transaction_buckets_campaign(mail_col, rewards_df, combined_df)
    print()


def analyze_transaction_sizes(mail_col, rewards_df):
    """Simple analysis of transaction sizes for responders vs non-responders"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    measure_month = get_next_month_col(campaign)
    
    # Check if data exists
    spend_col = f"{measure_month} Spend"
    swipe_col = f"{measure_month} Swipes"
    
    if spend_col not in rewards_df.columns:
        print(f"{campaign}: {measure_month} data not available")
        return
    
    # Get campaign accounts
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    unique_offers = sorted(campaign_accounts[mail_col].unique())
    
    # Prepare data
    offer_data = []
    
    for offer in unique_offers:
        offer_accounts = campaign_accounts[campaign_accounts[mail_col] == offer]
        
        # Identify responders properly
        if 'NU' in offer:
            responders = offer_accounts[
                (offer_accounts[resp_col].notna()) & 
                (~offer_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
            ]
        else:
            responders = offer_accounts[offer_accounts[resp_col].notna()]
        
        non_responders = offer_accounts.drop(responders.index)
        
        # Calculate average transaction size
        resp_total_spend = responders[spend_col].sum()
        resp_total_swipes = responders[swipe_col].sum()
        resp_avg_trans_size = resp_total_spend / resp_total_swipes if resp_total_swipes > 0 else 0
        
        non_resp_total_spend = non_responders[spend_col].sum()
        non_resp_total_swipes = non_responders[swipe_col].sum()
        non_resp_avg_trans_size = non_resp_total_spend / non_resp_total_swipes if non_resp_total_swipes > 0 else 0
        
        # Average swipes per account
        resp_avg_swipes = responders[swipe_col].mean() if len(responders) > 0 else 0
        non_resp_avg_swipes = non_responders[swipe_col].mean() if len(non_responders) > 0 else 0
        
        offer_data.append({
            'offer': offer,
            'resp_avg_trans_size': resp_avg_trans_size,
            'non_resp_avg_trans_size': non_resp_avg_trans_size,
            'resp_avg_swipes': resp_avg_swipes,
            'non_resp_avg_swipes': non_resp_avg_swipes
        })
    
    # Create chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    offers = [d['offer'] for d in offer_data]
    x = np.arange(len(offers))
    width = 0.35
    
    resp_sizes = [d['resp_avg_trans_size'] for d in offer_data]
    non_resp_sizes = [d['non_resp_avg_trans_size'] for d in offer_data]
    
    bars1 = ax.bar(x - width/2, resp_sizes, width, label='Responders', color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, non_resp_sizes, width, label='Non-Responders', color='#A23B72', alpha=0.8)
    
    ax.set_title(f'{campaign} - Average Transaction Size in {measure_month}', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Transaction Size ($)', fontsize=12)
    ax.set_xlabel('Offer Type', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(offers)
    ax.legend()
    
    # Add value labels
    for bar, val in zip(bars1, resp_sizes):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
               f'${val:.0f}', ha='center', va='bottom', fontsize=10)
    
    for bar, val in zip(bars2, non_resp_sizes):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
               f'${val:.0f}', ha='center', va='bottom', fontsize=10)
    
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\n{campaign} - {measure_month} Transaction Analysis")
    print("="*80)
    print(f"{'Offer':<8} {'---Responders---':^25} {'---Non-Responders---':^25}")
    print(f"{'':8} {'Avg Size':>12} {'Avg Swipes':>12} {'Avg Size':>12} {'Avg Swipes':>12}")
    print("-"*80)
    
    for d in offer_data:
        print(f"{d['offer']:<8} ${d['resp_avg_trans_size']:>10.2f} {d['resp_avg_swipes']:>11.1f} "
              f"${d['non_resp_avg_trans_size']:>10.2f} {d['non_resp_avg_swipes']:>11.1f}")
    
    # Analysis summary
    print("\nKey Findings:")
    for d in offer_data:
        if d['resp_avg_swipes'] > d['non_resp_avg_swipes'] and d['resp_avg_trans_size'] < d['non_resp_avg_trans_size']:
            print(f"  {d['offer']}: Responders swiped MORE often with SMALLER transactions")
        elif d['resp_avg_swipes'] > d['non_resp_avg_swipes'] and d['resp_avg_trans_size'] > d['non_resp_avg_trans_size']:
            print(f"  {d['offer']}: Responders swiped MORE often with LARGER transactions")

# Run for each campaign
for mail_col in mail_columns:
    analyze_transaction_sizes(mail_col, rewards_df)


# Create a single, clear chart for campaign response rates
fig, ax = plt.subplots(figsize=(10, 6))

# Prepare data for all campaigns
campaign_data = []

for mail_col in mail_columns:
    campaign_month = mail_col.replace(' Mail', '')
    resp_col = f"{campaign_month} Resp"
    
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()]
    responders = rewards_df[rewards_df[resp_col].notna()]
    
    campaign_data.append({
        'Campaign': campaign_month,
        'Mailed': len(campaign_accounts),
        'Responded': len(responders),
        'Response Rate': (len(responders) / len(campaign_accounts) * 100) if len(campaign_accounts) > 0 else 0
    })

campaign_df = pd.DataFrame(campaign_data)

# Create bar chart
campaigns = campaign_df['Campaign']
response_rates = campaign_df['Response Rate']

colors = ['#2E86AB', '#A23B72', '#F18F01']
bars = ax.bar(campaigns, response_rates, color=colors, edgecolor='black', linewidth=1)

ax.set_title('Response Rates by Campaign', fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel('Response Rate (%)', fontsize=14)
ax.set_xlabel('Campaign Month', fontsize=14)
ax.set_ylim(0, max(response_rates) * 1.3)

# Add value labels on bars
for bar, rate in zip(bars, response_rates):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{rate:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Add grid
ax.yaxis.grid(True, linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

plt.tight_layout()
plt.show()

# Print summary below chart
for i, row in campaign_df.iterrows():
    print(f"{row['Campaign']}: {row['Mailed']:,} mailed, {row['Responded']:,} responded ({row['Response Rate']:.1f}%)")


# Create before/after analysis for ALL campaigns dynamically
def analyze_campaign_spending(mail_col, rewards_df):
    """Analyze spending 3 months before and after a campaign"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    
    # Get all month-specific spend columns (format: MmmYY Spend)
    import re
    month_pattern = re.compile(r'^[A-Z][a-z]{2}\d{2} Spend$')
    all_spend_cols = [col for col in rewards_df.columns if month_pattern.match(col)]
    all_months = [col.replace(' Spend', '') for col in all_spend_cols]
    
    # Sort months chronologically
    def sort_month_key(month_str):
        month_num, year = parse_campaign_month(month_str)
        return (year, month_num)
    
    all_months.sort(key=sort_month_key)
    
    # Find campaign month index
    campaign_idx = all_months.index(campaign) if campaign in all_months else -1
    
    if campaign_idx == -1:
        print(f"Campaign month {campaign} not found in data")
        return
    
    # Get 3 months before and 3 months after (or as many as available)
    start_idx = max(0, campaign_idx - 3)
    end_idx = min(len(all_months), campaign_idx + 4)  # +4 to include 3 months after
    months_to_analyze = all_months[start_idx:end_idx]
    
    # Get responders and non-responders
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    responders = campaign_accounts[campaign_accounts[resp_col].notna()]
    non_responders = campaign_accounts[campaign_accounts[resp_col].isna()]
    
    # Calculate spending
    resp_spending = []
    non_resp_spending = []
    
    for month in months_to_analyze:
        spend_col = f'{month} Spend'
        resp_avg = responders[spend_col].mean() if len(responders) > 0 else 0
        non_resp_avg = non_responders[spend_col].mean() if len(non_responders) > 0 else 0
        resp_spending.append(resp_avg)
        non_resp_spending.append(non_resp_avg)
    
    # Create chart
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(months_to_analyze))
    width = 0.35
    
    # Choose colors based on campaign
    colors = [('#2E86AB', '#A23B72'), ('#4ECDC4', '#FF6B6B'), ('#6A994E', '#BC4B51')]
    campaign_idx_color = list(mail_columns).index(mail_col) % len(colors)
    color1, color2 = colors[campaign_idx_color]
    
    bars1 = ax.bar(x - width/2, resp_spending, width, 
                   label=f'Responders (n={len(responders):,})', 
                   color=color1, alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, non_resp_spending, width, 
                   label=f'Non-Responders (n={len(non_responders):,})', 
                   color=color2, alpha=0.8, edgecolor='black')
    
    # Mark campaign month
    campaign_position = months_to_analyze.index(campaign) if campaign in months_to_analyze else -1
    if campaign_position >= 0:
        ax.axvline(x=campaign_position, color='red', linestyle='--', alpha=0.5, linewidth=2)
        ax.text(campaign_position, max(max(resp_spending), max(non_resp_spending)) * 1.1, 
                'Campaign Month', ha='center', fontsize=11, color='red', fontweight='bold')
    
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Spend per Account ($)', fontsize=12, fontweight='bold')
    ax.set_title(f'{campaign} Campaign - Spending Trends (Before & After)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(months_to_analyze, rotation=45, ha='right')
    ax.legend(loc='upper left')
    
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.show()
    
    # Print statistics
    print(f"{campaign} CAMPAIGN - SPENDING ANALYSIS")
    print("="*80)
    print(f"Responders: {len(responders):,} | Non-Responders: {len(non_responders):,}")
    print("\nAverage Monthly Spend:")
    
    measurement_month = get_next_month_col(campaign)
    for i, month in enumerate(months_to_analyze):
        marker = " <-- Campaign" if month == campaign else " <-- Measurement" if month == measurement_month else ""
        lift = ((resp_spending[i] - non_resp_spending[i]) / non_resp_spending[i] * 100) if non_resp_spending[i] > 0 else 0
        print(f"{month}: Resp: ${resp_spending[i]:>7.2f} | Non-Resp: ${non_resp_spending[i]:>7.2f} | Lift: {lift:+6.1f}%{marker}")

# Run for all campaigns
for mail_col in mail_columns:
    analyze_campaign_spending(mail_col, rewards_df)
    print("\n")


# ===========================================================================
# Spend Campaign
# ===========================================================================

def analyze_campaign_by_offer(mail_col, rewards_df):
    """Create separate charts for each offer type within a campaign"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    
    # Get all month-specific spend columns
    import re
    month_pattern = re.compile(r'^[A-Z][a-z]{2}\d{2} Spend$')
    all_spend_cols = [col for col in rewards_df.columns if month_pattern.match(col)]
    all_months = [col.replace(' Spend', '') for col in all_spend_cols]
    
    # Sort months chronologically
    def sort_month_key(month_str):
        month_num, year = parse_campaign_month(month_str)
        return (year, month_num)
    
    all_months.sort(key=sort_month_key)
    
    # Find campaign month index
    campaign_idx = all_months.index(campaign) if campaign in all_months else -1
    
    if campaign_idx == -1:
        print(f"Campaign month {campaign} not found in data")
        return
    
    # Get analysis window
    start_idx = max(0, campaign_idx - 3)
    end_idx = min(len(all_months), campaign_idx + 4)
    months_to_analyze = all_months[start_idx:end_idx]
    
    # Get unique offers for this campaign
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    unique_offers = sorted(campaign_accounts[mail_col].unique())
    
    # Create a figure for each offer type
    for offer in unique_offers:
        # Get accounts for this specific offer
        offer_accounts = campaign_accounts[campaign_accounts[mail_col] == offer]
        responders = offer_accounts[offer_accounts[resp_col].notna()]
        non_responders = offer_accounts[offer_accounts[resp_col].isna()]
        
        # Calculate spending
        resp_spending = []
        non_resp_spending = []
        
        for month in months_to_analyze:
            spend_col = f'{month} Spend'
            resp_avg = responders[spend_col].mean() if len(responders) > 0 else 0
            non_resp_avg = non_responders[spend_col].mean() if len(non_responders) > 0 else 0
            resp_spending.append(resp_avg)
            non_resp_spending.append(non_resp_avg)
        
        # Create chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(months_to_analyze))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, resp_spending, width, 
                       label=f'Responders (n={len(responders):,})', 
                       color='#2E86AB', alpha=0.8, edgecolor='black')
        bars2 = ax.bar(x + width/2, non_resp_spending, width, 
                       label=f'Non-Responders (n={len(non_responders):,})', 
                       color='#A23B72', alpha=0.8, edgecolor='black')
        
        # Add value labels on top of bars
        for bar, value in zip(bars1, resp_spending):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 3,
                       f'${value:.0f}', ha='center', va='bottom', fontsize=9)
        
        for bar, value in zip(bars2, non_resp_spending):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 3,
                       f'${value:.0f}', ha='center', va='bottom', fontsize=9)
        
        # Mark campaign month with a better vertical line
        campaign_position = months_to_analyze.index(campaign) if campaign in months_to_analyze else -1
        if campaign_position >= 0:
            # Draw line from bottom to near top
            y_max = max(max(resp_spending), max(non_resp_spending))
            ax.axvline(x=campaign_position, ymin=0, ymax=0.95, color='red', 
                      linestyle='--', alpha=0.6, linewidth=2)
            ax.text(campaign_position, y_max * 1.15, 'Campaign Month', 
                   ha='center', fontsize=10, color='red', fontweight='bold')
        
        # Calculate response rate
        response_rate = (len(responders) / len(offer_accounts) * 100) if len(offer_accounts) > 0 else 0
        
        ax.set_xlabel('Month', fontsize=11, fontweight='bold')
        ax.set_ylabel('Average Spend ($)', fontsize=11, fontweight='bold')
        ax.set_title(f'{campaign} Campaign - {offer} Offer (Response Rate: {response_rate:.1f}%)', 
                     fontsize=13, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(months_to_analyze, rotation=45, ha='right')
        ax.legend(loc='upper left')
        
        # Set y-axis limit to give room for labels
        ax.set_ylim(0, max(max(resp_spending), max(non_resp_spending)) * 1.2)
        
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        plt.show()
        
        # Print statistics for this offer
        print(f"{campaign} - {offer} OFFER")
        print("-"*60)
        print(f"Sent: {len(offer_accounts):,} | Responded: {len(responders):,} | Rate: {response_rate:.1f}%")
        
        measurement_month = get_next_month_col(campaign)
        measurement_idx = months_to_analyze.index(measurement_month) if measurement_month in months_to_analyze else -1
        
        if measurement_idx >= 0:
            lift = ((resp_spending[measurement_idx] - non_resp_spending[measurement_idx]) / 
                   non_resp_spending[measurement_idx] * 100) if non_resp_spending[measurement_idx] > 0 else 0
            print(f"Measurement Month ({measurement_month}): Resp: ${resp_spending[measurement_idx]:.2f} | "
                  f"Non-Resp: ${non_resp_spending[measurement_idx]:.2f} | Lift: {lift:+.1f}%")
        print()

# Run for each campaign
print("="*80)
print("CAMPAIGN ANALYSIS BY OFFER TYPE")
print("="*80)

for mail_col in mail_columns:
    campaign = mail_col.replace(' Mail', '')
    print(f"\n{campaign} CAMPAIGN CHARTS:")
    print("="*80)
    analyze_campaign_by_offer(mail_col, rewards_df)


def analyze_campaign_swipes_by_offer(mail_col, rewards_df):
    """Create swipe analysis charts for each offer type within a campaign"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    
    # Get all month-specific swipe columns
    import re
    month_pattern = re.compile(r'^[A-Z][a-z]{2}\d{2} Swipes$')
    all_swipe_cols = [col for col in rewards_df.columns if month_pattern.match(col)]
    all_months = [col.replace(' Swipes', '') for col in all_swipe_cols]
    
    # Sort months chronologically
    def sort_month_key(month_str):
        month_num, year = parse_campaign_month(month_str)
        return (year, month_num)
    
    all_months.sort(key=sort_month_key)
    
    # Find campaign month index
    campaign_idx = all_months.index(campaign) if campaign in all_months else -1
    
    if campaign_idx == -1:
        print(f"Campaign month {campaign} not found in data")
        return
    
    # Get analysis window
    start_idx = max(0, campaign_idx - 3)
    end_idx = min(len(all_months), campaign_idx + 4)
    months_to_analyze = all_months[start_idx:end_idx]
    
    # Get unique offers for this campaign
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    unique_offers = sorted(campaign_accounts[mail_col].unique())
    
    # Create a figure for each offer type
    for offer in unique_offers:
        # Get accounts for this specific offer
        offer_accounts = campaign_accounts[campaign_accounts[mail_col] == offer]
        
        # FIXED: Check actual response values, not just if field is not null
        # Responders should have the offer type in their response column (e.g., "NU 5", "TH-10", etc.)
        # Non-responders might have null OR values like "NU 1", "NU 2", "NU 3", "NU 4"
        
        # For NU offers, responders are those who hit 5+ swipes
        if 'NU' in offer:
            # True responders for NU have values like "NU 5", "NU 6", etc. or just "NU"
            responders = offer_accounts[
                (offer_accounts[resp_col].notna()) & 
                (~offer_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
            ]
            non_responders = offer_accounts[
                (offer_accounts[resp_col].isna()) | 
                (offer_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
            ]
        else:
            # For threshold offers (TH-X), responders have non-null response
            responders = offer_accounts[offer_accounts[resp_col].notna()]
            non_responders = offer_accounts[offer_accounts[resp_col].isna()]
        
        # Extract threshold from offer
        threshold = int(offer.split('-')[1]) if '-' in offer else 5
        
        # Calculate swipes
        resp_swipes = []
        non_resp_swipes = []
        
        for month in months_to_analyze:
            swipe_col = f'{month} Swipes'
            resp_avg = responders[swipe_col].mean() if len(responders) > 0 else 0
            non_resp_avg = non_responders[swipe_col].mean() if len(non_responders) > 0 else 0
            resp_swipes.append(resp_avg)
            non_resp_swipes.append(non_resp_avg)
        
        # Create chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(months_to_analyze))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, resp_swipes, width, 
                       label=f'Responders (n={len(responders):,})', 
                       color='#4ECDC4', alpha=0.8, edgecolor='black')
        bars2 = ax.bar(x + width/2, non_resp_swipes, width, 
                       label=f'Non-Responders (n={len(non_responders):,})', 
                       color='#FF6B6B', alpha=0.8, edgecolor='black')
        
        # Add value labels on top of bars
        for bar, value in zip(bars1, resp_swipes):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                       f'{value:.1f}', ha='center', va='bottom', fontsize=9)
        
        for bar, value in zip(bars2, non_resp_swipes):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                       f'{value:.1f}', ha='center', va='bottom', fontsize=9)
        
        # Mark campaign month
        campaign_position = months_to_analyze.index(campaign) if campaign in months_to_analyze else -1
        if campaign_position >= 0:
            y_max = max(max(resp_swipes), max(non_resp_swipes))
            ax.axvline(x=campaign_position, ymin=0, ymax=0.95, color='red', 
                      linestyle='--', alpha=0.6, linewidth=2)
            ax.text(campaign_position, y_max * 1.15, 'Campaign Month', 
                   ha='center', fontsize=10, color='red', fontweight='bold')
        
        # Add threshold line
        ax.axhline(y=threshold, color='green', linestyle=':', alpha=0.5, linewidth=1.5)
        ax.text(len(months_to_analyze) - 0.5, threshold, f'Threshold: {threshold}', 
               va='center', fontsize=9, color='green', fontweight='bold')
        
        # Calculate response rate
        response_rate = (len(responders) / len(offer_accounts) * 100) if len(offer_accounts) > 0 else 0
        
        ax.set_xlabel('Month', fontsize=11, fontweight='bold')
        ax.set_ylabel('Average Swipes per Account', fontsize=11, fontweight='bold')
        ax.set_title(f'{campaign} Campaign - {offer} Offer - SWIPES (Response Rate: {response_rate:.1f}%)', 
                     fontsize=13, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(months_to_analyze, rotation=45, ha='right')
        ax.legend(loc='upper left')
        
        # Set y-axis limit to give room for labels
        ax.set_ylim(0, max(max(resp_swipes), max(non_resp_swipes), threshold) * 1.2)
        
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        plt.show()
        
        # Print statistics for this offer
        print(f"{campaign} - {offer} OFFER (SWIPES)")
        print("-"*60)
        print(f"Threshold: {threshold} swipes | Sent: {len(offer_accounts):,} | Responded: {len(responders):,}")
        
        measurement_month = get_next_month_col(campaign)
        measurement_idx = months_to_analyze.index(measurement_month) if measurement_month in months_to_analyze else -1
        
        if measurement_idx >= 0:
            resp_m = resp_swipes[measurement_idx]
            non_resp_m = non_resp_swipes[measurement_idx]
            lift = ((resp_m - non_resp_m) / non_resp_m * 100) if non_resp_m > 0 else 0
            print(f"Measurement Month ({measurement_month}): Resp: {resp_m:.1f} swipes | "
                  f"Non-Resp: {non_resp_m:.1f} swipes | Lift: {lift:+.1f}%")
            if resp_m >= threshold:
                print(f"✓ Responders exceeded threshold by: {resp_m - threshold:.1f} swipes")
            else:
                print(f"✗ Responders fell short of threshold by: {threshold - resp_m:.1f} swipes")
        print()

# Run for each campaign
print("="*80)
print("CAMPAIGN SWIPE ANALYSIS BY OFFER TYPE")
print("="*80)

for mail_col in mail_columns:
    campaign = mail_col.replace(' Mail', '')
    print(f"\n{campaign} CAMPAIGN - SWIPE CHARTS:")
    print("="*80)
    analyze_campaign_swipes_by_offer(mail_col, rewards_df)


def analyze_mcc_shifts(mail_col, rewards_df, combined_df):
    """Analyze if responders change where they shop (MCC codes) after campaigns"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    measure_month = get_next_month_col(campaign)
    
    # Parse months for transaction filtering
    campaign_month_num, campaign_year = parse_campaign_month(campaign)
    measure_month_num, measure_year = parse_campaign_month(measure_month)
    
    # Get 3 months before campaign
    before_months = []
    for i in range(3):
        month = campaign_month_num - (i + 1)
        year = campaign_year
        if month <= 0:
            month += 12
            year -= 1
        before_months.append((month, year))
    
    # Filter transactions
    before_trans = combined_df[
        combined_df['transaction_date'].apply(lambda x: (x.month, x.year) in before_months)
    ]
    
    after_trans = combined_df[
        (combined_df['transaction_date'].dt.month == measure_month_num) & 
        (combined_df['transaction_date'].dt.year == measure_year)
    ]
    
    if len(after_trans) == 0:
        print(f"{campaign}: {measure_month} transaction detail not available")
        return
    
    # Get responder/non-responder accounts
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    
    if 'NU' in str(campaign_accounts[mail_col].iloc[0]):
        responder_accts = campaign_accounts[
            (campaign_accounts[resp_col].notna()) & 
            (~campaign_accounts[resp_col].astype(str).str.contains('NU [1-4]', na=False, regex=True))
        ][' Acct Number'].values
    else:
        responder_accts = campaign_accounts[campaign_accounts[resp_col].notna()][' Acct Number'].values
    
    non_responder_accts = campaign_accounts[~campaign_accounts[' Acct Number'].isin(responder_accts)][' Acct Number'].values
    
    # Get MCC distributions
    resp_before = before_trans[before_trans['primary_account_num'].isin(responder_accts)].groupby('mcc_code')['amount'].sum()
    resp_after = after_trans[after_trans['primary_account_num'].isin(responder_accts)].groupby('mcc_code')['amount'].sum()
    
    non_resp_before = before_trans[before_trans['primary_account_num'].isin(non_responder_accts)].groupby('mcc_code')['amount'].sum()
    non_resp_after = after_trans[after_trans['primary_account_num'].isin(non_responder_accts)].groupby('mcc_code')['amount'].sum()
    
    # Get top MCCs
    top_mccs = resp_after.nlargest(10).index.tolist()
    
    # Calculate percentage shifts
    mcc_shifts = []
    for mcc in top_mccs:
        resp_before_pct = (resp_before.get(mcc, 0) / resp_before.sum() * 100) if resp_before.sum() > 0 else 0
        resp_after_pct = (resp_after.get(mcc, 0) / resp_after.sum() * 100) if resp_after.sum() > 0 else 0
        
        non_resp_before_pct = (non_resp_before.get(mcc, 0) / non_resp_before.sum() * 100) if non_resp_before.sum() > 0 else 0
        non_resp_after_pct = (non_resp_after.get(mcc, 0) / non_resp_after.sum() * 100) if non_resp_after.sum() > 0 else 0
        
        mcc_shifts.append({
            'mcc': mcc,
            'resp_shift': resp_after_pct - resp_before_pct,
            'non_resp_shift': non_resp_after_pct - non_resp_before_pct
        })
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 6))
    
    mcc_df = pd.DataFrame(mcc_shifts)
    x = np.arange(len(mcc_df))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, mcc_df['resp_shift'], width, label='Responders', color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, mcc_df['non_resp_shift'], width, label='Non-Responders', color='#A23B72', alpha=0.8)
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_title(f'{campaign} - MCC Category Shifts (% Change from Pre to Post Campaign)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Change in Spend Share (%)', fontsize=11)
    ax.set_xlabel('MCC Code', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(mcc_df['mcc'].astype(str), rotation=45)
    ax.legend()
    
    plt.tight_layout()
    plt.show()
    
    print(f"\n{campaign} - Merchant Category Shifts")
    print("="*70)
    print(f"{'MCC Code':>10} {'Responder Shift':>18} {'Non-Resp Shift':>18}")
    print("-"*70)
    for _, row in mcc_df.iterrows():
        print(f"{row['mcc']:>10} {row['resp_shift']:>+17.1f}% {row['non_resp_shift']:>+17.1f}%")

# Run for each campaign
for mail_col in mail_columns:
    analyze_mcc_shifts(mail_col, rewards_df, combined_df)


# ===========================================================================
# Ladder movement
# ===========================================================================

# Define the ladder levels
ladder_levels = {
    'NU': 5,      # Non-user to 5+ swipes
    'TH-10': 10,  # Threshold 10 swipes
    'TH-15': 15,  # Threshold 15 swipes
    'TH-20': 20,  # Threshold 20 swipes
    'TH-25': 25   # Threshold 25 swipes
}

print("THE LADDER CONCEPT")
print("="*70)
print("Goal: Move accounts UP the ladder over time")
print("-"*70)
print("Ladder Levels:")
for offer, threshold in ladder_levels.items():
    print(f"  {offer:6} = {threshold:2} swipes required")
print("\n" + "-"*70)
print("Strategy:")
print("  • Start accounts at lower thresholds (NU or TH-10)")
print("  • If they respond, move them UP to higher thresholds")
print("  • If they don't respond, move them DOWN or keep same")
print("  • Goal: Sustained behavior at higher swipe levels")


# ===========================================================================
# Track Individual Account Journeys
# ===========================================================================

# Pick some example accounts to track their journey
sample_accounts = []

# Find accounts that appeared in all 3 campaigns
for _, row in rewards_df.iterrows():
    if all(pd.notna(row[col]) for col in mail_columns):
        sample_accounts.append(row[' Acct Number'])
    if len(sample_accounts) >= 5:  # Just get 5 examples
        break

print("SAMPLE ACCOUNT JOURNEYS")
print("="*70)

for acct in sample_accounts[:3]:  # Show 3 examples
    acct_data = rewards_df[rewards_df[' Acct Number'] == acct].iloc[0]
    
    print(f"\nAccount: {acct[:10]}...")
    print("-"*50)
    
    for mail_col in mail_columns:
        campaign = mail_col.replace(' Mail', '')
        resp_col = f'{campaign} Resp'
        
        offer = acct_data[mail_col]
        threshold = ladder_levels.get(offer, 0)
        responded = 'YES' if pd.notna(acct_data[resp_col]) else 'NO'
        
        # Check for NU non-responders
        if 'NU' in str(offer) and pd.notna(acct_data[resp_col]):
            if str(acct_data[resp_col]).startswith('NU '):
                responded = 'NO'
        
        print(f"  {campaign}: Offered {offer:6} ({threshold:2} swipes) → Responded: {responded}")


def analyze_responder_history(mail_col, rewards_df):
    """For each campaign's responders, check their previous response history"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    campaign_idx = mail_columns.index(mail_col)
    
    # Get this campaign's TRUE responders (excluding "NU 1-4")
    campaign_data = rewards_df[rewards_df[mail_col].notna()].copy()
    
    # Filter out "NU 1-4" which are non-responders
    true_responders = campaign_data[
        (campaign_data[resp_col].notna()) & 
        (campaign_data[resp_col] != 'NU 1-4')
    ]
    
    if len(true_responders) == 0:
        print(f"\n{campaign} - No responders found")
        return pd.DataFrame(), campaign
    
    # Track their history
    history_data = []
    
    for _, responder in true_responders.iterrows():
        current_offer = responder[mail_col]
        current_threshold = ladder_levels.get(current_offer, 0)
        
        # Look for previous responses
        prev_campaign_responded = None
        prev_offer = None
        prev_threshold = None
        
        # Search backwards through previous campaigns
        for prev_idx in range(campaign_idx - 1, -1, -1):
            prev_mail_col = mail_columns[prev_idx]
            prev_resp_col = prev_mail_col.replace(' Mail', '') + ' Resp'
            
            # Check if they received and responded to previous campaign
            if pd.notna(responder[prev_mail_col]) and pd.notna(responder[prev_resp_col]):
                # Check for valid response (not "NU 1-4")
                if responder[prev_resp_col] != 'NU 1-4':
                    prev_campaign_responded = prev_mail_col.replace(' Mail', '')
                    prev_offer = responder[prev_mail_col]
                    prev_threshold = ladder_levels.get(prev_offer, 0)
                    break
        
        # Determine movement
        if prev_campaign_responded:
            movement = current_threshold - prev_threshold
            direction = 'Higher' if movement > 0 else 'Lower' if movement < 0 else 'Same'
        else:
            movement = 0
            direction = 'First Response'
        
        history_data.append({
            'current_offer': current_offer,
            'current_threshold': current_threshold,
            'prev_campaign': prev_campaign_responded,
            'prev_offer': prev_offer,
            'prev_threshold': prev_threshold,
            'movement': movement,
            'direction': direction
        })
    
    history_df = pd.DataFrame(history_data)
    
    print(f"\n{campaign} RESPONDER HISTORY ANALYSIS")
    print("="*70)
    print(f"Total Responders: {len(history_df):,}")
    
    if len(history_df) > 0:
        # Summary by direction
        direction_counts = history_df['direction'].value_counts()
        for direction, count in direction_counts.items():
            pct = (count / len(history_df)) * 100
            print(f"  {direction:15} {count:6,} ({pct:5.1f}%)")
    
    return history_df, campaign

# Define ladder levels
ladder_levels = {
    'NU': 5,
    'TH-10': 10,
    'TH-15': 15,
    'TH-20': 20,
    'TH-25': 25
}

# Analyze each campaign
responder_histories = {}
for mail_col in mail_columns:
    history_df, campaign = analyze_responder_history(mail_col, rewards_df)
    if len(history_df) > 0:
        responder_histories[campaign] = history_df


# Run the corrected analysis
responder_histories = {}
for mail_col in mail_columns:
    history_df, campaign = analyze_responder_history(mail_col, rewards_df)
    if len(history_df) > 0:
        responder_histories[campaign] = history_df


# Create chart for each campaign showing responder history
for campaign, history_df in responder_histories.items():
    if len(history_df) == 0:
        continue
        
    fig, ax = plt.subplots(figsize=(10, 6))
    
    direction_counts = history_df['direction'].value_counts()
    colors = {
        'Higher': '#4ECDC4',
        'Lower': '#FF6B6B', 
        'Same': '#FFA500',
        'First Response': '#9B59B6'
    }
    
    # Ensure consistent order
    order = ['First Response', 'Higher', 'Same', 'Lower']
    ordered_counts = [direction_counts.get(d, 0) for d in order if d in direction_counts.index]
    ordered_labels = [d for d in order if d in direction_counts.index]
    
    bars = ax.bar(ordered_labels, ordered_counts,
                   color=[colors.get(x, '#808080') for x in ordered_labels],
                   edgecolor='black', linewidth=1)
    
    ax.set_title(f'{campaign} - Responder History (n={len(history_df):,})', 
                 fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Responders', fontsize=12)
    ax.set_xlabel('Compared to Previous Response', fontsize=12)
    
    # Add value labels
    for bar, count in zip(bars, ordered_counts):
        pct = (count / len(history_df)) * 100
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 5,
               f'{count:,}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()


# For each campaign, show how responders at each level got there
for campaign, history_df in responder_histories.items():
    if len(history_df) == 0:
        continue
    
    print(f"\n{campaign} - LADDER MOVEMENT DETAILS")
    print("="*70)
    
    # Group by current offer
    for offer in sorted(history_df['current_offer'].unique()):
        offer_data = history_df[history_df['current_offer'] == offer]
        threshold = ladder_levels.get(offer, 0)
        
        print(f"\n{offer} Responders ({threshold} swipes) - {len(offer_data):,} total:")
        
        # Show where they came from
        direction_breakdown = offer_data['direction'].value_counts()
        for direction, count in direction_breakdown.items():
            pct = (count / len(offer_data)) * 100
            
            if direction == 'Higher':
                # Show what offers they moved up from
                prev_offers = offer_data[offer_data['direction'] == 'Higher']['prev_offer'].value_counts()
                print(f"  Moved UP: {count:,} ({pct:.1f}%)")
                for prev_offer, prev_count in prev_offers.items():
                    print(f"    from {prev_offer}: {prev_count:,}")
            elif direction == 'Lower':
                # Show what offers they moved down from
                prev_offers = offer_data[offer_data['direction'] == 'Lower']['prev_offer'].value_counts()
                print(f"  Moved DOWN: {count:,} ({pct:.1f}%)")
                for prev_offer, prev_count in prev_offers.items():
                    print(f"    from {prev_offer}: {prev_count:,}")
            else:
                print(f"  {direction}: {count:,} ({pct:.1f}%)")


def track_responder_movement(prev_mail_col, curr_mail_col, rewards_df):
    """Track what happened to responders from one campaign to the next"""
    
    prev_campaign = prev_mail_col.replace(' Mail', '')
    curr_campaign = curr_mail_col.replace(' Mail', '')
    prev_resp_col = f'{prev_campaign} Resp'
    curr_resp_col = f'{curr_campaign} Resp'
    
    # Get previous campaign responders
    prev_responders = rewards_df[
        (rewards_df[prev_mail_col].notna()) & 
        (rewards_df[prev_resp_col].notna()) &
        (rewards_df[prev_resp_col] != 'NU 1-4')
    ]
    
    print(f"\nWHAT HAPPENED TO {prev_campaign} RESPONDERS?")
    print("="*70)
    print(f"Total {prev_campaign} responders: {len(prev_responders):,}")
    
    # Check how many were mailed in next campaign
    curr_mailed = prev_responders[prev_responders[curr_mail_col].notna()]
    print(f"Mailed again in {curr_campaign}: {len(curr_mailed):,} ({len(curr_mailed)/len(prev_responders)*100:.1f}%)")
    
    # Not mailed in next campaign
    not_mailed = prev_responders[prev_responders[curr_mail_col].isna()]
    print(f"NOT mailed in {curr_campaign}: {len(not_mailed):,} ({len(not_mailed)/len(prev_responders)*100:.1f}%)")
    
    # Of those mailed, how many responded?
    if len(curr_mailed) > 0:
        curr_responded = curr_mailed[
            (curr_mailed[curr_resp_col].notna()) & 
            (curr_mailed[curr_resp_col] != 'NU 1-4')
        ]
        print(f"Responded again in {curr_campaign}: {len(curr_responded):,} ({len(curr_responded)/len(curr_mailed)*100:.1f}% of those mailed)")
        
        # Break down by offer movement
        print(f"\nOffer changes for {prev_campaign} responders mailed in {curr_campaign}:")
        
        # Get unique offers from previous campaign
        prev_offers = sorted(curr_mailed[prev_mail_col].unique())
        
        for prev_offer in prev_offers:
            prev_offer_responders = curr_mailed[curr_mailed[prev_mail_col] == prev_offer]
            if len(prev_offer_responders) > 0:
                print(f"\n  {prev_offer} responders ({len(prev_offer_responders):,}):")
                curr_offers = prev_offer_responders[curr_mail_col].value_counts()
                for curr_offer, count in curr_offers.items():
                    # Check response rate
                    responded = prev_offer_responders[
                        (prev_offer_responders[curr_mail_col] == curr_offer) &
                        (prev_offer_responders[curr_resp_col].notna()) &
                        (prev_offer_responders[curr_resp_col] != 'NU 1-4')
                    ]
                    resp_rate = len(responded) / count * 100 if count > 0 else 0
                    
                    # Determine direction
                    prev_threshold = ladder_levels.get(prev_offer, 0)
                    curr_threshold = ladder_levels.get(curr_offer, 0)
                    if curr_threshold > prev_threshold:
                        direction = "↑"
                    elif curr_threshold < prev_threshold:
                        direction = "↓"
                    else:
                        direction = "→"
                    
                    print(f"    {direction} {curr_offer}: {count:,} ({resp_rate:.1f}% responded)")

# Run for each consecutive campaign pair
for i in range(len(mail_columns) - 1):
    track_responder_movement(mail_columns[i], mail_columns[i + 1], rewards_df)


def track_responder_journey(account_list, rewards_df, start_campaign=None):
    """Track a cohort of accounts through multiple campaigns"""
    
    # If no start campaign specified, use the first one
    if start_campaign is None:
        start_campaign = mail_columns[0].replace(' Mail', '')
    
    start_idx = None
    for i, col in enumerate(mail_columns):
        if col.replace(' Mail', '') == start_campaign:
            start_idx = i
            break
    
    if start_idx is None:
        print(f"Campaign {start_campaign} not found")
        return None
    
    # Track the cohort through subsequent campaigns
    journey_data = []
    
    for mail_col in mail_columns[start_idx:]:
        campaign = mail_col.replace(' Mail', '')
        resp_col = f'{campaign} Resp'
        
        # Get status for this campaign
        mailed = account_list[account_list[mail_col].notna()]
        responded = mailed[
            (mailed[resp_col].notna()) & 
            (mailed[resp_col] != 'NU 1-4')
        ]
        
        # Calculate average threshold offered
        avg_threshold = 0
        if len(mailed) > 0:
            thresholds = [ladder_levels.get(offer, 0) for offer in mailed[mail_col]]
            avg_threshold = np.mean(thresholds)
        
        journey_data.append({
            'campaign': campaign,
            'mailed': len(mailed),
            'responded': len(responded),
            'response_rate': len(responded) / len(mailed) * 100 if len(mailed) > 0 else 0,
            'avg_threshold': avg_threshold,
            'retention_from_start': len(responded) / len(account_list) * 100
        })
    
    return pd.DataFrame(journey_data)

# Example: Track April responders through all subsequent campaigns
apr_responders = rewards_df[
    (rewards_df['Apr25 Mail'].notna()) & 
    (rewards_df['Apr25 Resp'].notna()) &
    (rewards_df['Apr25 Resp'] != 'NU 1-4')
]

print("TRACKING APRIL 2025 RESPONDERS THROUGH TIME")
print("="*70)
print(f"Starting cohort: {len(apr_responders):,} April responders\n")

journey_df = track_responder_journey(apr_responders, rewards_df, 'Apr25')

for _, row in journey_df.iterrows():
    print(f"{row['campaign']:8} Mailed: {row['mailed']:5,} | "
          f"Responded: {row['responded']:5,} ({row['response_rate']:5.1f}%) | "
          f"Avg Threshold: {row['avg_threshold']:4.1f} | "
          f"Retention: {row['retention_from_start']:5.1f}%")


def visualize_cohort_journey(cohort_name, cohort_accounts, rewards_df, start_campaign=None):
    """Create visual tracking of a cohort over time"""
    
    journey_df = track_responder_journey(cohort_accounts, rewards_df, start_campaign)
    
    if journey_df is None or len(journey_df) == 0:
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    campaigns = journey_df['campaign'].tolist()
    x = range(len(campaigns))
    
    # 1. Mailed vs Responded
    ax1.bar(x, journey_df['mailed'], alpha=0.5, label='Mailed', color='#4ECDC4')
    ax1.bar(x, journey_df['responded'], alpha=0.8, label='Responded', color='#2E86AB')
    ax1.set_title(f'{cohort_name} - Participation Over Time', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Campaign')
    ax1.set_ylabel('Number of Accounts')
    ax1.set_xticks(x)
    ax1.set_xticklabels(campaigns, rotation=45)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Response Rate Trend
    ax2.plot(x, journey_df['response_rate'], 'o-', color='#FF6B6B', linewidth=2, markersize=8)
    ax2.set_title(f'{cohort_name} - Response Rate Trend', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Campaign')
    ax2.set_ylabel('Response Rate (%)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(campaigns, rotation=45)
    ax2.set_ylim(0, max(journey_df['response_rate']) * 1.2 if len(journey_df) > 0 else 100)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for i, rate in enumerate(journey_df['response_rate']):
        ax2.text(i, rate + 1, f'{rate:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 3. Average Threshold Progression
    ax3.plot(x, journey_df['avg_threshold'], 's-', color='#9B59B6', linewidth=2, markersize=8)
    ax3.set_title(f'{cohort_name} - Average Threshold Level', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Campaign')
    ax3.set_ylabel('Average Threshold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(campaigns, rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for i, thresh in enumerate(journey_df['avg_threshold']):
        ax3.text(i, thresh + 0.3, f'{thresh:.0f}', ha='center', va='bottom', fontsize=9)
    
    # 4. Retention from Start
    ax4.bar(x, journey_df['retention_from_start'], color='#FFA500', alpha=0.7, edgecolor='black')
    ax4.set_title(f'{cohort_name} - Retention from Original Cohort', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Campaign')
    ax4.set_ylabel('% Still Responding')
    ax4.set_xticks(x)
    ax4.set_xticklabels(campaigns, rotation=45)
    ax4.set_ylim(0, max(journey_df['retention_from_start']) * 1.2 if len(journey_df) > 0 else 100)
    
    # Add value labels
    for i, ret in enumerate(journey_df['retention_from_start']):
        ax4.text(i, ret + 0.5, f'{ret:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle(f'Cohort Journey: {cohort_name}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    return journey_df

# Visualize April responders
apr_journey = visualize_cohort_journey('April 2025 Responders', apr_responders, rewards_df, 'Apr25')


def analyze_transaction_distribution_by_response(mail_col, rewards_df, combined_df):
    """Analyze transaction distribution for each response group in a campaign"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    measure_month = get_next_month_col(campaign)
    
    # Parse month/year for filtering
    month_num, year = parse_campaign_month(measure_month)
    
    # Filter transactions for measurement month
    month_trans = combined_df[
        (combined_df['transaction_date'].dt.month == month_num) & 
        (combined_df['transaction_date'].dt.year == year)
    ]
    
    if len(month_trans) == 0:
        print(f"{campaign}: {measure_month} transaction data not available")
        return None
    
    # Get campaign accounts
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    
    # Define transaction buckets
    bins = [0, 1, 5, 10, 25, 50, 100, 500, float('inf')]
    labels = ['< $1', '$1-5', '$5-10', '$10-25', '$25-50', '$50-100', '$100-500', '$500+']
    
    # Get unique response values (including NU 1-4 and non-responders)
    response_groups = {}
    
    # Non-responders (mailed but no response)
    non_responders = campaign_accounts[campaign_accounts[resp_col].isna()]
    if len(non_responders) > 0:
        response_groups['No Response'] = non_responders[' Acct Number'].values
    
    # NU 1-4 (attempted but didn't meet threshold)
    nu_non_responders = campaign_accounts[campaign_accounts[resp_col] == 'NU 1-4']
    if len(nu_non_responders) > 0:
        response_groups['NU 1-4'] = nu_non_responders[' Acct Number'].values
    
    # True responders by offer type
    true_responders = campaign_accounts[
        (campaign_accounts[resp_col].notna()) & 
        (campaign_accounts[resp_col] != 'NU 1-4')
    ]
    
    # Group by response value
    for resp_value in sorted(true_responders[resp_col].unique()):
        if pd.notna(resp_value):
            resp_accounts = true_responders[true_responders[resp_col] == resp_value]
            response_groups[resp_value] = resp_accounts[' Acct Number'].values
    
    # Calculate distribution for each group
    distributions = {}
    
    for group_name, account_list in response_groups.items():
        group_trans = month_trans[month_trans['primary_account_num'].isin(account_list)]
        
        if len(group_trans) > 0:
            # Create distribution
            dist = pd.cut(group_trans['amount'], bins=bins, labels=labels).value_counts()
            dist_pct = (dist / dist.sum() * 100).round(1)
            distributions[group_name] = dist_pct
        else:
            distributions[group_name] = pd.Series(0, index=labels)
    
    if len(distributions) == 0:
        print(f"{campaign}: No transaction data found")
        return None
    
    # Create DataFrame for heatmap
    dist_df = pd.DataFrame(distributions).fillna(0)
    
    # Ensure all buckets are present
    for label in labels:
        if label not in dist_df.index:
            dist_df.loc[label] = 0
    
    # Reorder rows to match bucket order
    dist_df = dist_df.reindex(labels)
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create heatmap
    im = ax.imshow(dist_df.values, cmap='YlOrRd', aspect='auto', vmin=0, vmax=30)
    
    # Set ticks
    ax.set_xticks(np.arange(len(dist_df.columns)))
    ax.set_yticks(np.arange(len(dist_df.index)))
    ax.set_xticklabels(dist_df.columns, rotation=45, ha='right')
    ax.set_yticklabels(dist_df.index)
    
    # Add text annotations
    for i in range(len(dist_df.index)):
        for j in range(len(dist_df.columns)):
            value = dist_df.iloc[i, j]
            if value > 0:
                text = ax.text(j, i, f'{value:.1f}%', 
                             ha="center", va="center", color="black", fontsize=9)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('% of Transactions', rotation=270, labelpad=15)
    
    ax.set_title(f'{campaign} Campaign - Transaction Distribution by Response Group ({measure_month})', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Response Group', fontsize=12)
    ax.set_ylabel('Transaction Amount Range', fontsize=12)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print(f"\n{campaign} - Transaction Distribution Summary")
    print("="*70)
    print(f"{'Response Group':<15} {'Avg Trans Size':>15} {'# Transactions':>15}")
    print("-"*70)
    
    for group_name, account_list in response_groups.items():
        group_trans = month_trans[month_trans['primary_account_num'].isin(account_list)]
        if len(group_trans) > 0:
            avg_size = group_trans['amount'].mean()
            num_trans = len(group_trans)
            print(f"{group_name:<15} ${avg_size:>14.2f} {num_trans:>15,}")
    
    return dist_df

# Run for each campaign
transaction_distributions = {}
for mail_col in mail_columns:
    dist_df = analyze_transaction_distribution_by_response(mail_col, rewards_df, combined_df)
    if dist_df is not None:
        campaign = mail_col.replace(' Mail', '')
        transaction_distributions[campaign] = dist_df


def create_transaction_distribution_table(mail_col, rewards_df, combined_df):
    """Create a clean formatted table of transaction distribution by response group"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    measure_month = get_next_month_col(campaign)
    
    # Parse month/year for filtering
    month_num, year = parse_campaign_month(measure_month)
    
    # Filter transactions for measurement month
    month_trans = combined_df[
        (combined_df['transaction_date'].dt.month == month_num) & 
        (combined_df['transaction_date'].dt.year == year)
    ]
    
    if len(month_trans) == 0:
        print(f"{campaign}: {measure_month} transaction data not available")
        return None
    
    # Get campaign accounts
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    
    # Define transaction buckets
    bins = [0, 1, 5, 10, 25, 50, 100, 500, float('inf')]
    labels = ['< $1', '$1-5', '$5-10', '$10-25', '$25-50', '$50-100', '$100-500', '$500+']
    
    # Get response groups
    response_groups = {}
    
    # Non-responders
    non_responders = campaign_accounts[campaign_accounts[resp_col].isna()]
    if len(non_responders) > 0:
        response_groups['No Resp'] = non_responders[' Acct Number'].values
    
    # NU 1-4
    nu_non_responders = campaign_accounts[campaign_accounts[resp_col] == 'NU 1-4']
    if len(nu_non_responders) > 0:
        response_groups['NU 1-4'] = nu_non_responders[' Acct Number'].values
    
    # True responders
    true_responders = campaign_accounts[
        (campaign_accounts[resp_col].notna()) & 
        (campaign_accounts[resp_col] != 'NU 1-4')
    ]
    
    for resp_value in sorted(true_responders[resp_col].unique()):
        if pd.notna(resp_value):
            resp_accounts = true_responders[true_responders[resp_col] == resp_value]
            response_groups[resp_value] = resp_accounts[' Acct Number'].values
    
    # Calculate distributions
    distributions = {}
    
    for group_name, account_list in response_groups.items():
        group_trans = month_trans[month_trans['primary_account_num'].isin(account_list)]
        
        if len(group_trans) > 0:
            dist = pd.cut(group_trans['amount'], bins=bins, labels=labels).value_counts()
            dist_pct = (dist / dist.sum() * 100).round(1)
            distributions[group_name] = dist_pct
    
    if len(distributions) == 0:
        print(f"{campaign}: No transaction data found")
        return None
    
    # Create DataFrame
    dist_df = pd.DataFrame(distributions).fillna(0)
    
    # Ensure all buckets are present
    for label in labels:
        if label not in dist_df.index:
            dist_df.loc[label] = 0
    
    dist_df = dist_df.reindex(labels)
    
    # Create the table visualization
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare table data
    table_data = []
    
    # Header row
    header = ['Amount'] + list(dist_df.columns)
    
    # Data rows
    for idx, row_label in enumerate(dist_df.index):
        row = [row_label]
        for col in dist_df.columns:
            value = dist_df.loc[row_label, col]
            if value > 0:
                row.append(f'{value:.1f}%')
            else:
                row.append('-')
        table_data.append(row)
    
    # Create table
    table = ax.table(cellText=table_data, 
                     colLabels=header,
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.12] + [0.11] * len(dist_df.columns))
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(1.2, 2)
    
    # Color code cells based on percentage
    for i in range(len(table_data)):
        for j in range(1, len(header)):  # Skip first column (labels)
            cell_val = table_data[i][j]
            if cell_val != '-':
                val = float(cell_val.replace('%', ''))
                # Color intensity based on value
                if val >= 20:
                    color = '#ffcccc'
                elif val >= 15:
                    color = '#ffe6cc'
                elif val >= 10:
                    color = '#ffffcc'
                elif val >= 5:
                    color = '#e6ffcc'
                else:
                    color = '#f0f0f0'
                table[(i+1, j)].set_facecolor(color)
    
    # Style header row
    for j in range(len(header)):
        table[(0, j)].set_facecolor('#4ECDC4')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    # Style first column
    for i in range(1, len(table_data) + 1):
        table[(i, 0)].set_facecolor('#e0e0e0')
        table[(i, 0)].set_text_props(weight='bold')
    
    plt.title(f'{campaign} Campaign - Transaction Distribution ({measure_month})\n', 
              fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.show()
    
    # Print text summary
    print(f"\n{campaign} - Key Insights")
    print("="*70)
    
    # Find highest concentration for each group
    for col in dist_df.columns:
        max_bucket = dist_df[col].idxmax()
        max_value = dist_df[col].max()
        print(f"{col:10} → Peak at {max_bucket:8} ({max_value:.1f}% of transactions)")
    
    return dist_df

# Run for each campaign
for mail_col in mail_columns:
    dist_df = create_transaction_distribution_table(mail_col, rewards_df, combined_df)
    if dist_df is not None:
        print()


def create_transaction_distribution_table(mail_col, rewards_df, combined_df):
    """Create a clean formatted table of transaction distribution by response group"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    measure_month = get_next_month_col(campaign)
    
    # Parse month/year for filtering
    month_num, year = parse_campaign_month(measure_month)
    
    # Filter transactions for measurement month
    month_trans = combined_df[
        (combined_df['transaction_date'].dt.month == month_num) & 
        (combined_df['transaction_date'].dt.year == year)
    ]
    
    if len(month_trans) == 0:
        print(f"{campaign}: {measure_month} transaction data not available")
        return None
    
    # Define transaction buckets
    bins = [0, 1, 5, 10, 25, 50, 100, 500, float('inf')]
    labels = ['< $1', '$1-5', '$5-10', '$10-25', '$25-50', '$50-100', '$100-500', '$500+']
    
    # Get response groups
    response_groups = {}
    
    # No Mail (Control group)
    not_mailed = rewards_df[rewards_df[mail_col].isna()]
    if len(not_mailed) > 0:
        response_groups['No Mail'] = not_mailed[' Acct Number'].values
    
    # Get campaign accounts
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    
    # Combined Non-Responders (No Response + NU 1-4 ONLY)
    non_responders = campaign_accounts[
        (campaign_accounts[resp_col].isna()) | 
        (campaign_accounts[resp_col] == 'NU 1-4')
    ]
    if len(non_responders) > 0:
        response_groups['Non-Resp'] = non_responders[' Acct Number'].values
    
    # True responders
    true_responders = campaign_accounts[
        (campaign_accounts[resp_col].notna()) & 
        (campaign_accounts[resp_col] != 'NU 1-4')
    ]
    
    # Get unique response values and rename NU to NU 5+
    for resp_value in sorted(true_responders[resp_col].unique()):
        if pd.notna(resp_value):
            resp_accounts = true_responders[true_responders[resp_col] == resp_value]
            # Rename NU to NU 5+ for display
            display_name = 'NU 5+' if resp_value == 'NU' else resp_value
            response_groups[display_name] = resp_accounts[' Acct Number'].values
    
    # Calculate distributions
    distributions = {}
    account_counts = {}
    
    for group_name, account_list in response_groups.items():
        group_trans = month_trans[month_trans['primary_account_num'].isin(account_list)]
        account_counts[group_name] = len(account_list)
        
        if len(group_trans) > 0:
            dist = pd.cut(group_trans['amount'], bins=bins, labels=labels).value_counts()
            dist_pct = (dist / dist.sum() * 100).round(1)
            distributions[group_name] = dist_pct
    
    if len(distributions) == 0:
        print(f"{campaign}: No transaction data found")
        return None
    
    # Create DataFrame
    dist_df = pd.DataFrame(distributions).fillna(0)
    
    # Ensure all buckets are present
    for label in labels:
        if label not in dist_df.index:
            dist_df.loc[label] = 0
    
    dist_df = dist_df.reindex(labels)
    
    # FIXED ORDER: No Mail, Non-Resp, NU 5+, TH-10, TH-15, TH-20, TH-25
    col_order = []
    if 'No Mail' in dist_df.columns:
        col_order.append('No Mail')
    if 'Non-Resp' in dist_df.columns:
        col_order.append('Non-Resp')
    if 'NU 5+' in dist_df.columns:
        col_order.append('NU 5+')
    for threshold in ['TH-10', 'TH-15', 'TH-20', 'TH-25']:
        if threshold in dist_df.columns:
            col_order.append(threshold)
    
    # Add any other columns not yet included
    other_cols = [col for col in dist_df.columns if col not in col_order]
    col_order.extend(sorted(other_cols))
    
    dist_df = dist_df[col_order]
    
    # Create the table visualization
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare table data
    table_data = []
    
    # Header row
    header = ['Amount'] + [f'{col}\n(n={account_counts.get(col, 0):,})' for col in dist_df.columns]
    
    # Data rows
    for idx, row_label in enumerate(dist_df.index):
        row = [row_label]
        for col in dist_df.columns:
            value = dist_df.loc[row_label, col]
            if value > 0:
                row.append(f'{value:.1f}%')
            else:
                row.append('-')
        table_data.append(row)
    
    # Add average transaction size row
    avg_row = ['Avg Size']
    for col in dist_df.columns:
        group_trans = month_trans[month_trans['primary_account_num'].isin(response_groups.get(col, []))]
        if len(group_trans) > 0:
            avg_size = group_trans['amount'].mean()
            avg_row.append(f'${avg_size:.0f}')
        else:
            avg_row.append('-')
    table_data.append(avg_row)
    
    # Create table
    table = ax.table(cellText=table_data, 
                     colLabels=header,
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.12] + [0.11] * len(dist_df.columns))
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(13)
    table.scale(1.2, 2.2)
    
    # Use blue gradient for intensity
    for i in range(len(table_data) - 1):  # Skip the average row
        for j in range(1, len(header)):  # Skip first column
            cell_val = table_data[i][j]
            if cell_val != '-':
                val = float(cell_val.replace('%', ''))
                # Blue gradient based on value
                if val >= 25:
                    color = '#08519c'
                    text_color = 'white'
                elif val >= 20:
                    color = '#3182bd'
                    text_color = 'white'
                elif val >= 15:
                    color = '#6baed6'
                    text_color = 'black'
                elif val >= 10:
                    color = '#9ecae1'
                    text_color = 'black'
                elif val >= 5:
                    color = '#c6dbef'
                    text_color = 'black'
                else:
                    color = '#f0f0f0'
                    text_color = 'black'
                table[(i+1, j)].set_facecolor(color)
                table[(i+1, j)].set_text_props(color=text_color)
    
    # Style header row
    for j in range(len(header)):
        if 'No Mail' in header[j]:
            table[(0, j)].set_facecolor('#666666')  # Gray for control
        elif 'Non-Resp' in header[j]:
            table[(0, j)].set_facecolor('#999999')  # Light gray for non-responders
        elif j == 0:
            table[(0, j)].set_facecolor('#333333')  # Dark for label column
        else:
            table[(0, j)].set_facecolor('#2E86AB')  # Teal for responders
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    # Style first column
    for i in range(1, len(table_data) + 1):
        table[(i, 0)].set_facecolor('#e0e0e0')
        table[(i, 0)].set_text_props(weight='bold')
    
    # Style average row
    for j in range(len(header)):
        table[(len(table_data), j)].set_facecolor('#FFD700')  # Gold
        table[(len(table_data), j)].set_text_props(weight='bold')
    
    # REDUCED padding
    plt.title(f'{campaign} - Transaction Size Distribution ({measure_month})', 
              fontsize=16, fontweight='bold', pad=2)
    
    plt.tight_layout()
    plt.show()
    
    return dist_df

# Run for each campaign
for mail_col in mail_columns:
    dist_df = create_transaction_distribution_table(mail_col, rewards_df, combined_df)


def create_responders_only_table(mail_col, rewards_df, combined_df):
    """Create table showing ONLY responder transaction distributions"""
    
    campaign = mail_col.replace(' Mail', '')
    resp_col = f'{campaign} Resp'
    measure_month = get_next_month_col(campaign)
    
    # Parse month/year for filtering
    month_num, year = parse_campaign_month(measure_month)
    
    # Filter transactions for measurement month
    month_trans = combined_df[
        (combined_df['transaction_date'].dt.month == month_num) & 
        (combined_df['transaction_date'].dt.year == year)
    ]
    
    if len(month_trans) == 0:
        print(f"{campaign}: {measure_month} transaction data not available")
        return None
    
    # Define transaction buckets
    bins = [0, 1, 5, 10, 25, 50, 100, 500, float('inf')]
    labels = ['< $1', '$1-5', '$5-10', '$10-25', '$25-50', '$50-100', '$100-500', '$500+']
    
    # Get campaign accounts
    campaign_accounts = rewards_df[rewards_df[mail_col].notna()].copy()
    
    # ONLY true responders (exclude NU 1-4)
    true_responders = campaign_accounts[
        (campaign_accounts[resp_col].notna()) & 
        (campaign_accounts[resp_col] != 'NU 1-4')
    ]
    
    if len(true_responders) == 0:
        print(f"{campaign}: No responders found")
        return None
    
    # Get response groups - RESPONDERS ONLY
    response_groups = {}
    
    for resp_value in sorted(true_responders[resp_col].unique()):
        if pd.notna(resp_value):
            resp_accounts = true_responders[true_responders[resp_col] == resp_value]
            # Rename NU to NU 5+ for display
            display_name = 'NU 5+' if resp_value == 'NU' else resp_value
            response_groups[display_name] = resp_accounts[' Acct Number'].values
    
    # Calculate distributions
    distributions = {}
    account_counts = {}
    
    for group_name, account_list in response_groups.items():
        group_trans = month_trans[month_trans['primary_account_num'].isin(account_list)]
        account_counts[group_name] = len(account_list)
        
        if len(group_trans) > 0:
            dist = pd.cut(group_trans['amount'], bins=bins, labels=labels).value_counts()
            dist_pct = (dist / dist.sum() * 100).round(1)
            distributions[group_name] = dist_pct
    
    if len(distributions) == 0:
        print(f"{campaign}: No transaction data found for responders")
        return None
    
    # Create DataFrame
    dist_df = pd.DataFrame(distributions).fillna(0)
    
    # Ensure all buckets are present
    for label in labels:
        if label not in dist_df.index:
            dist_df.loc[label] = 0
    
    dist_df = dist_df.reindex(labels)
    
    # ORDER: NU 5+, TH-10, TH-15, TH-20, TH-25
    col_order = []
    if 'NU 5+' in dist_df.columns:
        col_order.append('NU 5+')
    for threshold in ['TH-10', 'TH-15', 'TH-20', 'TH-25']:
        if threshold in dist_df.columns:
            col_order.append(threshold)
    
    dist_df = dist_df[col_order]
    
    # Create the table visualization
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare table data
    table_data = []
    
    # Header row
    header = ['Amount'] + [f'{col}\n(n={account_counts.get(col, 0):,})' for col in dist_df.columns]
    
    # Data rows
    for idx, row_label in enumerate(dist_df.index):
        row = [row_label]
        for col in dist_df.columns:
            value = dist_df.loc[row_label, col]
            if value > 0:
                row.append(f'{value:.1f}%')
            else:
                row.append('-')
        table_data.append(row)
    
    # Add average transaction size row
    avg_row = ['Avg Size']
    for col in dist_df.columns:
        group_trans = month_trans[month_trans['primary_account_num'].isin(response_groups.get(col, []))]
        if len(group_trans) > 0:
            avg_size = group_trans['amount'].mean()
            avg_row.append(f'${avg_size:.0f}')
        else:
            avg_row.append('-')
    table_data.append(avg_row)
    
    # Create table
    table = ax.table(cellText=table_data, 
                     colLabels=header,
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.15] + [0.17] * len(dist_df.columns))
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(1.3, 2.5)
    
    # Use blue gradient for intensity
    for i in range(len(table_data) - 1):  # Skip the average row
        for j in range(1, len(header)):  # Skip first column
            cell_val = table_data[i][j]
            if cell_val != '-':
                val = float(cell_val.replace('%', ''))
                # Blue gradient based on value
                if val >= 25:
                    color = '#08519c'
                    text_color = 'white'
                elif val >= 20:
                    color = '#3182bd'
                    text_color = 'white'
                elif val >= 15:
                    color = '#6baed6'
                    text_color = 'black'
                elif val >= 10:
                    color = '#9ecae1'
                    text_color = 'black'
                elif val >= 5:
                    color = '#c6dbef'
                    text_color = 'black'
                else:
                    color = '#f0f0f0'
                    text_color = 'black'
                table[(i+1, j)].set_facecolor(color)
                table[(i+1, j)].set_text_props(color=text_color)
    
    # Style header row - all responders are teal
    for j in range(len(header)):
        if j == 0:
            table[(0, j)].set_facecolor('#333333')  # Dark for label column
        else:
            table[(0, j)].set_facecolor('#2E86AB')  # Teal for all responders
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    # Style first column
    for i in range(1, len(table_data) + 1):
        table[(i, 0)].set_facecolor('#e0e0e0')
        table[(i, 0)].set_text_props(weight='bold')
    
    # Style average row
    for j in range(len(header)):
        table[(len(table_data), j)].set_facecolor('#FFD700')  # Gold
        table[(len(table_data), j)].set_text_props(weight='bold')
    
    # Minimal padding
    plt.title(f'{campaign} - Responder Transaction Distribution ({measure_month})', 
              fontsize=16, fontweight='bold', pad=2)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    total_responders = sum(account_counts.values())
    print(f"\n{campaign} - Responders: {total_responders:,} total")
    
    return dist_df

# Run responders-only table for each campaign
for mail_col in mail_columns:
    dist_df = create_responders_only_table(mail_col, rewards_df, combined_df)


# List all columns in rewards_df to see what data we have
print("REWARDS DATAFRAME COLUMNS")
print("="*80)

# Group columns by type
account_cols = [col for col in rewards_df.columns if 'Acct' in col or 'Account' in col]
mail_cols = [col for col in rewards_df.columns if 'Mail' in col]
resp_cols = [col for col in rewards_df.columns if 'Resp' in col]
spend_cols = [col for col in rewards_df.columns if 'Spend' in col]
swipe_cols = [col for col in rewards_df.columns if 'Swipes' in col or 'Swipe' in col]
pin_cols = [col for col in rewards_df.columns if 'PIN' in col]
sig_cols = [col for col in rewards_df.columns if 'Sig' in col]
other_cols = [col for col in rewards_df.columns if col not in account_cols + mail_cols + resp_cols + spend_cols + swipe_cols + pin_cols + sig_cols]

print("\nAccount Columns:")
for col in account_cols:
    print(f"  {col}")

print("\nMail Columns:")
for col in mail_cols:
    print(f"  {col}")

print("\nResponse Columns:")
for col in resp_cols:
    print(f"  {col}")

print("\nSpend Columns:")
for col in spend_cols:
    print(f"  {col}")

print("\nSwipe Columns:")
for col in swipe_cols:
    print(f"  {col}")

print("\nPIN Transaction Columns:")
for col in pin_cols:
    print(f"  {col}")

print("\nSignature Transaction Columns:")
for col in sig_cols:
    print(f"  {col}")

print("\nOther Columns:")
for col in other_cols:
    print(f"  {col}")

print("\n" + "="*80)
print(f"Total columns: {len(rewards_df.columns)}")


def analyze_business_vs_personal(rewards_df):
    """Analyze how business vs personal accounts respond to campaigns"""
    
    # Overall portfolio composition
    total_accounts = len(rewards_df)
    business_accounts = rewards_df[rewards_df['Business?'] == 'Y']
    personal_accounts = rewards_df[rewards_df['Business?'] != 'Y']
    
    print("PORTFOLIO COMPOSITION")
    print("="*70)
    print(f"Total Accounts:    {total_accounts:,}")
    print(f"Business Accounts: {len(business_accounts):,} ({len(business_accounts)/total_accounts*100:.1f}%)")
    print(f"Personal Accounts: {len(personal_accounts):,} ({len(personal_accounts)/total_accounts*100:.1f}%)")
    
    # Analyze each campaign
    campaign_results = []
    
    for mail_col in mail_columns:
        campaign = mail_col.replace(' Mail', '')
        resp_col = f'{campaign} Resp'
        
        # Get mailed accounts
        mailed = rewards_df[rewards_df[mail_col].notna()]
        
        # Split by business/personal
        bus_mailed = mailed[mailed['Business?'] == 'Y']
        pers_mailed = mailed[mailed['Business?'] != 'Y']
        
        # Get responders (excluding NU 1-4)
        bus_responders = bus_mailed[
            (bus_mailed[resp_col].notna()) & 
            (bus_mailed[resp_col] != 'NU 1-4')
        ]
        pers_responders = pers_mailed[
            (pers_mailed[resp_col].notna()) & 
            (pers_mailed[resp_col] != 'NU 1-4')
        ]
        
        # Calculate response rates
        bus_response_rate = (len(bus_responders) / len(bus_mailed) * 100) if len(bus_mailed) > 0 else 0
        pers_response_rate = (len(pers_responders) / len(pers_mailed) * 100) if len(pers_mailed) > 0 else 0
        
        campaign_results.append({
            'campaign': campaign,
            'bus_mailed': len(bus_mailed),
            'pers_mailed': len(pers_mailed),
            'bus_responded': len(bus_responders),
            'pers_responded': len(pers_responders),
            'bus_rate': bus_response_rate,
            'pers_rate': pers_response_rate
        })
    
    # Create visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    campaigns = [r['campaign'] for r in campaign_results]
    x = np.arange(len(campaigns))
    
    # Chart 1: Mailed volumes
    bus_mailed = [r['bus_mailed'] for r in campaign_results]
    pers_mailed = [r['pers_mailed'] for r in campaign_results]
    
    width = 0.35
    ax1.bar(x - width/2, bus_mailed, width, label='Business', color='#2E86AB', alpha=0.8)
    ax1.bar(x + width/2, pers_mailed, width, label='Personal', color='#4ECDC4', alpha=0.8)
    ax1.set_title('Accounts Mailed by Type', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Accounts')
    ax1.set_xticks(x)
    ax1.set_xticklabels(campaigns)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Chart 2: Response rates
    bus_rates = [r['bus_rate'] for r in campaign_results]
    pers_rates = [r['pers_rate'] for r in campaign_results]
    
    ax2.bar(x - width/2, bus_rates, width, label='Business', color='#2E86AB', alpha=0.8)
    ax2.bar(x + width/2, pers_rates, width, label='Personal', color='#4ECDC4', alpha=0.8)
    ax2.set_title('Response Rates by Account Type', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Response Rate (%)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(campaigns)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, (b, p) in enumerate(zip(bus_rates, pers_rates)):
        ax2.text(i - width/2, b + 0.2, f'{b:.1f}%', ha='center', va='bottom', fontsize=9)
        ax2.text(i + width/2, p + 0.2, f'{p:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Chart 3: Average spending comparison
    measure_months = [get_next_month_col(c) for c in campaigns]
    bus_avg_spend = []
    pers_avg_spend = []
    
    for campaign, measure_month in zip(campaigns, measure_months):
        spend_col = f"{measure_month} Spend"
        if spend_col in rewards_df.columns:
            # Get responders for this campaign
            resp_col = f'{campaign} Resp'
            mail_col = f'{campaign} Mail'
            
            bus_resp = rewards_df[
                (rewards_df[mail_col].notna()) &
                (rewards_df['Business?'] == 'Y') &
                (rewards_df[resp_col].notna()) &
                (rewards_df[resp_col] != 'NU 1-4')
            ]
            pers_resp = rewards_df[
                (rewards_df[mail_col].notna()) &
                (rewards_df['Business?'] != 'Y') &
                (rewards_df[resp_col].notna()) &
                (rewards_df[resp_col] != 'NU 1-4')
            ]
            
            bus_avg_spend.append(bus_resp[spend_col].mean() if len(bus_resp) > 0 else 0)
            pers_avg_spend.append(pers_resp[spend_col].mean() if len(pers_resp) > 0 else 0)
    
    if bus_avg_spend:
        ax3.bar(x[:len(bus_avg_spend)] - width/2, bus_avg_spend, width, label='Business', color='#2E86AB', alpha=0.8)
        ax3.bar(x[:len(pers_avg_spend)] + width/2, pers_avg_spend, width, label='Personal', color='#4ECDC4', alpha=0.8)
        ax3.set_title('Average Spend by Responders (Measurement Month)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Average Spend ($)')
        ax3.set_xticks(x[:len(bus_avg_spend)])
        ax3.set_xticklabels(campaigns[:len(bus_avg_spend)])
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, (b, p) in enumerate(zip(bus_avg_spend, pers_avg_spend)):
            ax3.text(i - width/2, b + 5, f'${b:.0f}', ha='center', va='bottom', fontsize=9)
            ax3.text(i + width/2, p + 5, f'${p:.0f}', ha='center', va='bottom', fontsize=9)
    
    # Chart 4: Response type distribution
    ax4.axis('off')
    
    # Create summary table
    summary_data = []
    summary_data.append(['Campaign', 'Bus Rate', 'Pers Rate', 'Difference'])
    for r in campaign_results:
        diff = r['bus_rate'] - r['pers_rate']
        summary_data.append([
            r['campaign'],
            f"{r['bus_rate']:.1f}%",
            f"{r['pers_rate']:.1f}%",
            f"{diff:+.1f}%"
        ])
    
    table = ax4.table(cellText=summary_data,
                      cellLoc='center',
                      loc='center',
                      colWidths=[0.2, 0.2, 0.2, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 2)
    
    # Style header row
    for j in range(4):
        table[(0, j)].set_facecolor('#2E86AB')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    # Color code difference column
    for i in range(1, len(summary_data)):
        diff_val = float(summary_data[i][3].replace('%', '').replace('+', ''))
        if diff_val > 0:
            table[(i, 3)].set_facecolor('#ccffcc')  # Green for positive
        else:
            table[(i, 3)].set_facecolor('#ffcccc')  # Red for negative
    
    plt.suptitle('Business vs Personal Account Campaign Performance', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()
    
    # Print detailed summary
    print("\n" + "="*70)
    print("CAMPAIGN PERFORMANCE BY ACCOUNT TYPE")
    print("="*70)
    
    for r in campaign_results:
        print(f"\n{r['campaign']}:")
        print(f"  Business: {r['bus_responded']:,}/{r['bus_mailed']:,} = {r['bus_rate']:.1f}% response")
        print(f"  Personal: {r['pers_responded']:,}/{r['pers_mailed']:,} = {r['pers_rate']:.1f}% response")
        
        if r['bus_rate'] > r['pers_rate']:
            print(f"  → Business accounts responded {r['bus_rate'] - r['pers_rate']:.1f}% better")
        else:
            print(f"  → Personal accounts responded {r['pers_rate'] - r['bus_rate']:.1f}% better")

analyze_business_vs_personal(rewards_df)


def analyze_business_personal_transactions(rewards_df):
    """Analyze transaction patterns for business vs personal responders"""
    
    # Calculate average transaction metrics
    business = rewards_df[rewards_df['Business?'] == 'Y']
    personal = rewards_df[rewards_df['Business?'] != 'Y']
    
    print("\nTRANSACTION BEHAVIOR COMPARISON")
    print("="*70)
    
    # Overall metrics
    print("\nOverall Account Metrics:")
    print(f"{'Metric':<25} {'Business':>15} {'Personal':>15}")
    print("-"*55)
    
    metrics = [
        ('Avg Monthly Spend (12mo)', 'MonthlySpend12'),
        ('Avg Monthly Spend (3mo)', 'MonthlySpend3'),
        ('Avg Monthly Swipes (12mo)', 'MonthlySwipes12'),
        ('Avg Monthly Swipes (3mo)', 'MonthlySwipes3'),
        ('Current Balance', 'Curr Bal'),
        ('Average Balance', 'Avg Bal')
    ]
    
    for metric_name, col_name in metrics:
        if col_name in rewards_df.columns:
            bus_val = business[col_name].mean()
            pers_val = personal[col_name].mean()
            
            if 'Spend' in metric_name or 'Balance' in metric_name:
                print(f"{metric_name:<25} ${bus_val:>14,.2f} ${pers_val:>14,.2f}")
            else:
                print(f"{metric_name:<25} {bus_val:>15.1f} {pers_val:>15.1f}")
    
    # Calculate average transaction size
    print("\n" + "-"*55)
    print("Average Transaction Size:")
    
    recent_months = ['May25', 'Jun25', 'Jul25']
    for month in recent_months:
        spend_col = f'{month} Spend'
        swipe_col = f'{month} Swipes'
        
        if spend_col in rewards_df.columns:
            bus_avg_trans = business[spend_col].sum() / business[swipe_col].sum() if business[swipe_col].sum() > 0 else 0
            pers_avg_trans = personal[spend_col].sum() / personal[swipe_col].sum() if personal[swipe_col].sum() > 0 else 0
            
            print(f"  {month}: Business ${bus_avg_trans:.2f} | Personal ${pers_avg_trans:.2f}")

analyze_business_personal_transactions(rewards_df)


def analyze_holder_age_response_all_campaigns(rewards_df):
    """Analyze response rates by account holder age for all campaigns"""
    
    # Create age bins starting at 18
    age_bins = [18, 25, 35, 45, 55, 65, 100]
    age_labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    rewards_df['Age Group'] = pd.cut(rewards_df['Account Holder Age'], bins=age_bins, labels=age_labels)
    
    # Analyze each campaign
    all_campaign_data = []
    
    for mail_col in mail_columns:
        campaign = mail_col.replace(' Mail', '')
        resp_col = f'{campaign} Resp'
        
        # Skip if no response data
        if rewards_df[resp_col].isna().all():
            continue
        
        # Get mailed accounts
        mailed = rewards_df[rewards_df[mail_col].notna()].copy()
        
        # Calculate response rate by age group
        for age_group in age_labels:
            group_accounts = mailed[mailed['Age Group'] == age_group]
            if len(group_accounts) > 0:
                responders = group_accounts[
                    (group_accounts[resp_col].notna()) & 
                    (group_accounts[resp_col] != 'NU 1-4')
                ]
                response_rate = len(responders) / len(group_accounts) * 100
                all_campaign_data.append({
                    'campaign': campaign,
                    'age_group': age_group,
                    'mailed': len(group_accounts),
                    'responded': len(responders),
                    'rate': response_rate
                })
    
    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Organize data for plotting
    campaigns = sorted(set(d['campaign'] for d in all_campaign_data))
    x = np.arange(len(age_labels))
    width = 0.25
    
    colors = ['#2E86AB', '#4ECDC4', '#FF6B6B']
    
    for i, campaign in enumerate(campaigns):
        campaign_rates = []
        for age_group in age_labels:
            rate = next((d['rate'] for d in all_campaign_data 
                        if d['campaign'] == campaign and d['age_group'] == age_group), 0)
            campaign_rates.append(rate)
        
        offset = (i - len(campaigns)/2 + 0.5) * width
        bars = ax.bar(x + offset, campaign_rates, width, 
                      label=campaign, color=colors[i % len(colors)], alpha=0.8)
        
        # Add value labels
        for bar, rate in zip(bars, campaign_rates):
            if rate > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                       f'{rate:.0f}%', ha='center', va='bottom', fontsize=8)
    
    ax.set_title('Response Rates by Account Holder Age - All Campaigns', fontsize=14, fontweight='bold')
    ax.set_xlabel('Age Group', fontsize=12)
    ax.set_ylabel('Response Rate (%)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(age_labels)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary table
    print("\nRESPONSE RATES BY AGE GROUP")
    print("="*70)
    for campaign in campaigns:
        print(f"\n{campaign}:")
        for age_group in age_labels:
            data = next((d for d in all_campaign_data 
                        if d['campaign'] == campaign and d['age_group'] == age_group), None)
            if data:
                print(f"  {age_group:8} {data['responded']:5,}/{data['mailed']:5,} = {data['rate']:5.1f}%")

analyze_holder_age_response_all_campaigns(rewards_df)


def analyze_account_age_response_all_campaigns(rewards_df):
    """Analyze response rates by account age for all campaigns"""
    
    # Calculate account age
    if 'Date Opened' in rewards_df.columns:
        rewards_df['Date Opened'] = pd.to_datetime(rewards_df['Date Opened'])
        current_date = pd.to_datetime('2025-08-31')
        rewards_df['Account Age Years'] = (current_date - rewards_df['Date Opened']).dt.days / 365.25
    else:
        rewards_df['Account Age Years'] = rewards_df['Account Age'] / 365.25
    
    # Create account age bins
    acct_age_bins = [0, 1, 3, 5, 10, 20, 100]
    acct_age_labels = ['<1yr', '1-3yr', '3-5yr', '5-10yr', '10-20yr', '20yr+']
    rewards_df['Account Age Group'] = pd.cut(rewards_df['Account Age Years'], bins=acct_age_bins, labels=acct_age_labels)
    
    # Analyze each campaign
    all_campaign_data = []
    
    for mail_col in mail_columns:
        campaign = mail_col.replace(' Mail', '')
        resp_col = f'{campaign} Resp'
        
        # Skip if no response data
        if rewards_df[resp_col].isna().all():
            continue
        
        # Get mailed accounts
        mailed = rewards_df[rewards_df[mail_col].notna()].copy()
        
        # Calculate response rate by account age
        for acct_age_group in acct_age_labels:
            group_accounts = mailed[mailed['Account Age Group'] == acct_age_group]
            if len(group_accounts) > 0:
                responders = group_accounts[
                    (group_accounts[resp_col].notna()) & 
                    (group_accounts[resp_col] != 'NU 1-4')
                ]
                response_rate = len(responders) / len(group_accounts) * 100
                all_campaign_data.append({
                    'campaign': campaign,
                    'acct_age_group': acct_age_group,
                    'mailed': len(group_accounts),
                    'responded': len(responders),
                    'rate': response_rate
                })
    
    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Organize data for plotting
    campaigns = sorted(set(d['campaign'] for d in all_campaign_data))
    x = np.arange(len(acct_age_labels))
    width = 0.25
    
    colors = ['#4ECDC4', '#FF6B6B', '#FFA500']
    
    for i, campaign in enumerate(campaigns):
        campaign_rates = []
        for acct_age_group in acct_age_labels:
            rate = next((d['rate'] for d in all_campaign_data 
                        if d['campaign'] == campaign and d['acct_age_group'] == acct_age_group), 0)
            campaign_rates.append(rate)
        
        offset = (i - len(campaigns)/2 + 0.5) * width
        bars = ax.bar(x + offset, campaign_rates, width, 
                      label=campaign, color=colors[i % len(colors)], alpha=0.8)
        
        # Add value labels
        for bar, rate in zip(bars, campaign_rates):
            if rate > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                       f'{rate:.0f}%', ha='center', va='bottom', fontsize=8)
    
    ax.set_title('Response Rates by Account Age - All Campaigns', fontsize=14, fontweight='bold')
    ax.set_xlabel('Account Age', fontsize=12)
    ax.set_ylabel('Response Rate (%)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(acct_age_labels)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary table
    print("\nRESPONSE RATES BY ACCOUNT AGE")
    print("="*70)
    for campaign in campaigns:
        print(f"\n{campaign}:")
        for acct_age_group in acct_age_labels:
            data = next((d for d in all_campaign_data 
                        if d['campaign'] == campaign and d['acct_age_group'] == acct_age_group), None)
            if data:
                print(f"  {acct_age_group:10} {data['responded']:5,}/{data['mailed']:5,} = {data['rate']:5.1f}%")

analyze_account_age_response_all_campaigns(rewards_df)


def analyze_spending_by_age_all_campaigns(rewards_df):
    """Analyze average spending by account holder age for all campaigns"""
    
    # Ensure age groups exist
    if 'Age Group' not in rewards_df.columns:
        age_bins = [18, 25, 35, 45, 55, 65, 100]
        age_labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        rewards_df['Age Group'] = pd.cut(rewards_df['Account Holder Age'], bins=age_bins, labels=age_labels)
    
    # Analyze each campaign
    all_spending_data = []
    
    for mail_col in mail_columns:
        campaign = mail_col.replace(' Mail', '')
        resp_col = f'{campaign} Resp'
        measure_month = get_next_month_col(campaign)
        spend_col = f"{measure_month} Spend"
        
        if spend_col not in rewards_df.columns:
            continue
        
        # Get responders only
        responders = rewards_df[
            (rewards_df[mail_col].notna()) &
            (rewards_df[resp_col].notna()) &
            (rewards_df[resp_col] != 'NU 1-4')
        ]
        
        # Calculate average spending by age group
        for age_group in ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']:
            age_responders = responders[responders['Age Group'] == age_group]
            if len(age_responders) > 0:
                avg_spend = age_responders[spend_col].mean()
                all_spending_data.append({
                    'campaign': campaign,
                    'age_group': age_group,
                    'avg_spend': avg_spend,
                    'count': len(age_responders)
                })
    
    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Organize data for plotting
    campaigns = sorted(set(d['campaign'] for d in all_spending_data))
    age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    x = np.arange(len(age_groups))
    width = 0.25
    
    colors = ['#FF6B6B', '#4ECDC4', '#FFA500']
    
    for i, campaign in enumerate(campaigns):
        campaign_spending = []
        for age_group in age_groups:
            spend = next((d['avg_spend'] for d in all_spending_data 
                         if d['campaign'] == campaign and d['age_group'] == age_group), 0)
            campaign_spending.append(spend)
        
        offset = (i - len(campaigns)/2 + 0.5) * width
        bars = ax.bar(x + offset, campaign_spending, width, 
                      label=f'{campaign} ({get_next_month_col(campaign)})', 
                      color=colors[i % len(colors)], alpha=0.8)
        
        # Add value labels
        for bar, spend in zip(bars, campaign_spending):
            if spend > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 10,
                       f'${spend:.0f}', ha='center', va='bottom', fontsize=8)
    
    ax.set_title('Average Spending by Account Holder Age (Responders Only)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Age Group', fontsize=12)
    ax.set_ylabel('Average Spend ($)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(age_groups)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary table
    print("\nAVERAGE SPENDING BY AGE GROUP (RESPONDERS)")
    print("="*70)
    for campaign in campaigns:
        print(f"\n{campaign} ({get_next_month_col(campaign)} spending):")
        for age_group in age_groups:
            data = next((d for d in all_spending_data 
                        if d['campaign'] == campaign and d['age_group'] == age_group), None)
            if data:
                print(f"  {age_group:8} ${data['avg_spend']:8.2f} (n={data['count']:,})")

analyze_spending_by_age_all_campaigns(rewards_df)
