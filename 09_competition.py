# 09_competition.py
# Extracted from: CH- Transaction Analysis.ipynb (cells 123-208)
# M6: Competition config, detection, metrics, risk assessment, account-level
# ===========================================================================


# ===========================================================================
# 6 - Direct Competition
# ===========================================================================

# ---- Competition Config ----

# Competition List Setup

# ===========================================================================
# M6A: COMPETITOR CONFIGURATION & DETECTION (REVISED)
# Client: 1453 - Connex Credit Union (Connecticut)
# Market: New Haven, Hartford, Middlesex, Fairfield counties
# ===========================================================================
#
# MATCHING STRATEGY:
#   - starts_with: merchant name begins with this pattern (primary method)
#   - contains:    pattern appears anywhere in merchant name (use sparingly)
#   - exact:       merchant name matches exactly (for short/ambiguous terms)
#
# This eliminates false positives from generic terms like "CHASE" matching
# "CHASE OUTDOORS" or "CURRENT" matching "CURRENT ELECTRIC SUPPLY".
# ===========================================================================

COMPETITOR_MERCHANTS = {

    # =======================================================================
    # BIG NATIONALS — Major banks with significant CT branch presence
    # =======================================================================
    'big_nationals': {
        'starts_with': [
            # Bank of America (83 CT branches)
            'BANK OF AMERICA', 'BANKOFAMERICA', 'B OF A', 'BOA ',
            'BK OF AMERICA', 'BK OF AMER',

            # Wells Fargo (47 CT branches)
            'WELLS FARGO', 'WF BANK', 'WF HOME', 'WELLSFARGO',

            # JPMorgan Chase (63 CT branches)
            'CHASE BANK', 'CHASE BK', 'CHASE CREDIT', 'CHASE CARD',
            'CHASE HOME', 'CHASE AUTO', 'CHASE MTG',
            'JPMORGAN', 'JP MORGAN',

            # Citibank (12 CT branches)
            'CITIBANK', 'CITI BANK', 'CITI CARD', 'CITICORP',
            'CITI MORTGAGE', 'CITIMORTGAGE',

            # TD Bank (53 CT branches)
            'TD BANK', 'TD BK', 'TD BANKNORTH', 'TDBANK',

            # Citizens Bank (30 CT branches)
            'CITIZENS BANK', 'CITIZENS BK', 'CITIZENS FINANCIAL',

            # Santander (13 CT branches)
            'SANTANDER',

            # KeyBank (47 CT branches)
            'KEYBANK', 'KEY BANK', 'KEY BK',

            # M&T Bank (117 CT branches — largest in state)
            'M&T BANK', 'M&T BK', 'M AND T BANK', 'M AND T BK',
            'MANUFACTURERS AND TRADERS',

            # US Bank
            'US BANK', 'U.S. BANK', 'US BK', 'USB ',

            # Capital One (banking arm)
            'CAPITAL ONE BK', 'CAPITAL ONE BANK', 'CAPITAL ONE 360',
            'CAP ONE BANK', 'CAPITALONE BK',
        ],
        'exact': [
            'CHASE',          # only match if entire name is just "CHASE"
            'KEYBANK',
            'SANTANDER',
            'BOA',
        ]
    },

    # =======================================================================
    # REGIONALS — CT community/savings banks in Connex's footprint
    # =======================================================================
    'regionals': {
        'starts_with': [
            # Webster Bank (95 CT branches — 2nd largest)
            'WEBSTER BANK', 'WEBSTER BK', 'WEBSTERBANK',

            # Liberty Bank (51 CT branches)
            'LIBERTY BANK', 'LIBERTY BK',

            # Ion Bank (23 CT branches)
            'ION BANK', 'ION BK',

            # Union Savings Bank (26 CT branches)
            'UNION SAVINGS', 'UNION SVG',

            # Newtown Savings Bank (19 CT branches)
            'NEWTOWN SAVINGS', 'NEWTOWN SVG',

            # Beacon Bank and Trust (18 CT branches)
            'BEACON BANK',

            # Fairfield County Bank (17 CT branches)
            'FAIRFIELD COUNTY BANK', 'FAIRFIELD COUNTY BK',

            # First County Bank (14 CT branches)
            'FIRST COUNTY BANK', 'FIRST COUNTY BK',

            # Ives Bank (16 CT branches)
            'IVES BANK', 'IVES BK',

            # Thomaston Savings Bank (16 CT branches)
            'THOMASTON SAVINGS', 'THOMASTON SVG',

            # Northwest Community Bank (15 CT branches)
            'NORTHWEST COMMUNITY', 'NW COMMUNITY BANK',

            # Chelsea Groton Bank (14 CT branches)
            'CHELSEA GROTON',

            # Ascend Bank (13 CT branches)
            'ASCEND BANK', 'ASCEND BK',

            # Windsor Federal (11 CT branches)
            'WINDSOR FEDERAL',

            # Guilford Savings Bank (in Connex's backyard)
            'GUILFORD SAVINGS', 'GUILFORD SVG', 'GSB BANK',

            # Essex Savings Bank
            'ESSEX SAVINGS', 'ESSEX SVG',

            # Milford Bank
            'MILFORD BANK', 'THE MILFORD BANK',

            # Bankwell (9 CT branches)
            'BANKWELL',

            # Patriot Bank (7 CT branches)
            'PATRIOT BANK', 'PATRIOT BK',

            # Centreville Bank (7 CT branches)
            'CENTREVILLE BANK',

            # Bank of New Haven
            'BANK OF NEW HAVEN',

            # Connecticut Community Bank (10 CT branches)
            'CONNECTICUT COMMUNITY', 'CT COMMUNITY BANK',

            # PeoplesBank (6 CT branches)
            'PEOPLES BANK', 'PEOPLESBANK', 'PEOPLES BK',

            # Savings Bank of Danbury
            'SAVINGS BANK OF DANBURY',

            # Berkshire Bank (21 CT branches)
            'BERKSHIRE BANK', 'BERKSHIRE BK',

            # NBT Bank (6 CT branches)
            'NBT BANK', 'NBT BK',
        ],
        'exact': [
            'BANKWELL',
        ]
    },

    # =======================================================================
    # CREDIT UNIONS — Local/regional CUs competing in Connex's market
    # =======================================================================
    'credit_unions': {
        'starts_with': [
            # Direct competitors in New Haven County
            'NEW HAVEN COUNTY CREDIT', 'NEW HAVEN COUNTY CU', 'NHCCU',
            'CROSSPOINT FEDERAL', 'CROSSPOINT FCU', 'CROSSPOINT CU',
            'AFFINITY FEDERAL CU', 'AFFINITY FCU', 'AFFINITY CU',
            'USALLIANCE FINANCIAL', 'USALLIANCE FED', 'USALLIANCE',
            'GE CREDIT UNION', 'GE CU',
            'SCIENT FEDERAL', 'SCIENT FCU', 'SCIENT CU',
            'SCIENCE PARK FCU', 'SCIENCE PARK FED',
            'MUTUAL SECURITY CU', 'MUTUAL SECURITY CREDIT',

            # Statewide CT credit unions
            'CT STATE EMPLOYEES CU', 'CONNECTICUT STATE EMPLOYEES',
            'ACHIEVE FINANCIAL CU', 'ACHIEVE FINANCIAL CREDIT',
            'NUTMEG STATE FINANCIAL', 'NUTMEG STATE CU', 'NUTMEG CU',
            'FINEX CREDIT UNION', 'FINEX CU', 'FINEX FCU',
            'WESTERN CT FCU', 'WESTERN CONNECTICUT FCU',
            'ISLAND FEDERAL CU', 'ISLAND FEDERAL CREDIT',

            # National CUs with CT presence
            'NAVY FEDERAL', 'NAVY FED', 'NFCU',
            'GOLDEN 1 CREDIT', 'GOLDEN 1 CU',
            'PENTAGON FEDERAL', 'PENFED',
            'STATE EMPLOYEES CU', 'SECU ',
        ],
        'contains': [
            # Catch-all for any CU we might miss — use with caution,
            # validated by also requiring financial MCC codes (6012, 6051)
            # Uncomment ONLY if paired with MCC filtering:
            # 'CREDIT UNION',
            # 'FEDERAL CU',
        ]
    },

    # =======================================================================
    # DIGITAL BANKS — Online-only banks (universal, no location customization)
    # =======================================================================
    'digital_banks': {
        'starts_with': [
            # Pure digital banks
            'ALLY BANK', 'ALLY BK', 'ALLY FINANCIAL',
            'DISCOVER BANK', 'DISCOVER BK', 'DISCOVER SAVINGS',
            'SOFI BANK', 'SOFI MONEY', 'SOFI LENDING', 'SOFI CREDIT',
            'CHIME BANK', 'CHIME FINANCIAL',
            'VARO BANK', 'VARO MONEY',
            'GO2BANK',
            'GREEN DOT BANK', 'GREEN DOT BK', 'GREENDOT',

            # Neobank / BaaS infrastructure banks
            'THE BANCORP', 'BANCORP BANK',
            'STRIDE BANK',
            'COASTAL COMMUNITY BK',  # backend for some fintechs

            # Big tech / investment bank offerings
            'MARCUS BY GS', 'MARCUS BY GOLDMAN', 'MARCUS GOLDMAN',
            'GOLDMAN SACHS BANK',
            'SCHWAB BANK', 'CHARLES SCHWAB BK', 'SCHWAB BK',
            'FIDELITY CASH', 'FIDELITY BROKERAGE',

            # Investment/robo platforms with banking
            'ROBINHOOD CASH', 'ROBINHOOD MONEY',
            'BETTERMENT',
            'WEALTHFRONT',

            # International digital banks
            'REVOLUT',
            'N26 BANK', 'N26',
            'MONZO',
        ],
        'exact': [
            'CHIME',
            'REVOLUT',
            'BETTERMENT',
            'WEALTHFRONT',
        ]
    },

    # =======================================================================
    # WALLETS & P2P — Payment platforms (universal)
    # =======================================================================
    'wallets_p2p': {
        'starts_with': [
            'PAYPAL',
            'VENMO',
            'CASH APP', 'CASHAPP',
            'APPLE CASH', 'APPLE CARD', 'APPLE PAY CASH',
            'GOOGLE PAY', 'GOOGLEPAY',
            'ZELLE',
        ],
        'exact': [
            'PAYPAL',
            'VENMO',
        ]
    },

    # =======================================================================
    # BNPL — Buy Now Pay Later (universal)
    # =======================================================================
    'bnpl': {
        'starts_with': [
            'KLARNA',
            'AFTERPAY',
            'AFFIRM', 'AFFIRM INC',
            'SEZZLE',
            'QUADPAY',
            'ZIP PAY', 'ZIPPAY',
        ],
        'exact': [
            'KLARNA',
            'AFTERPAY',
            'SEZZLE',
        ]
    },
}


# ===========================================================================
# MATCHING FUNCTION — Two-tier precision matching
# ===========================================================================

def classify_competitor(merchant_name, config=COMPETITOR_MERCHANTS):
    """
    Classify a merchant as a competitor using tiered matching.

    Priority: exact → starts_with → contains
    Returns: (category, matched_pattern) or (None, None)
    """
    if not merchant_name or not isinstance(merchant_name, str):
        return None, None

    name = merchant_name.upper().strip()

    # Pass 1: Exact matches (highest confidence)
    for category, rules in config.items():
        for pattern in rules.get('exact', []):
            if name == pattern:
                return category, pattern

    # Pass 2: Starts-with matches (high confidence)
    for category, rules in config.items():
        for pattern in rules.get('starts_with', []):
            if name.startswith(pattern):
                return category, pattern

    # Pass 3: Contains matches (use sparingly — higher false positive risk)
    for category, rules in config.items():
        for pattern in rules.get('contains', []):
            if pattern in name:
                return category, pattern

    return None, None


# ===========================================================================
# APPLY TO DATAFRAME
# ===========================================================================

def tag_competitors(df, merchant_col='merchant_consolidated'):
    """
    Tag all transactions with competitor category and matched pattern.
    Adds two columns: competitor_category, competitor_match

    Parameters:
        df: DataFrame with merchant names
        merchant_col: column name containing merchant names to match against

    Returns:
        DataFrame with competitor_category and competitor_match columns added
    """
    results = df[merchant_col].apply(
        lambda x: classify_competitor(x) if pd.notna(x) else (None, None)
    )
    df['competitor_category'] = results.apply(lambda x: x[0])
    df['competitor_match'] = results.apply(lambda x: x[1])
    return df


# ===========================================================================
# DISCOVERY — Find potential competitors NOT in config
# ===========================================================================

# Financial services MCC codes that suggest a competitor transaction
FINANCIAL_MCC_CODES = [
    6010,  # Financial Institution – Manual Cash Disbursements
    6011,  # Financial Institution – Automated Cash Disbursements (ATMs)
    6012,  # Financial Institution – Merchandise and Services
    6051,  # Non-Financial Institutions – Foreign Currency, Money Orders
    6211,  # Security Brokers/Dealers
    6300,  # Insurance
    6012,  # Member financial institution
]

def discover_unmatched_financial(df, merchant_col='merchant_consolidated',
                                 mcc_col='mcc_code'):
    """
    Find merchants with financial MCC codes that weren't matched as competitors.
    These are candidates to ADD to the config.

    Returns a DataFrame of unmatched financial merchants sorted by spend.
    """
    # Only look at transactions that weren't already tagged
    untagged = df[df['competitor_category'].isna()].copy()

    # Filter to financial MCC codes
    if mcc_col in untagged.columns:
        financial = untagged[untagged[mcc_col].isin(FINANCIAL_MCC_CODES)]
    else:
        # Fallback: keyword scan for financial-sounding merchants
        financial_keywords = [
            'BANK', ' BK ', 'BK,', 'CREDIT UNION', ' CU ', 'CU,',
            'FEDERAL CU', 'FCU', 'SAVINGS BANK', 'SVG BK',
            'FINANCIAL', 'LENDING', 'MORTGAGE', 'MTG ',
        ]
        mask = untagged[merchant_col].str.upper().apply(
            lambda x: any(kw in f' {x} ' for kw in financial_keywords)
            if pd.notna(x) else False
        )
        financial = untagged[mask]

    if len(financial) == 0:
        print("✓ No unmatched financial merchants found.")
        return pd.DataFrame()

    # Summarize
    summary = financial.groupby(merchant_col).agg(
        transaction_count=('amount', 'count'),
        total_spend=('amount', 'sum'),
        unique_accounts=('primary_account_num', 'nunique'),
    ).sort_values('total_spend', ascending=False)

    return summary


# ===========================================================================
# PRINT CONFIG SUMMARY
# ===========================================================================

def print_config_summary(config=COMPETITOR_MERCHANTS):
    """Print a summary of the competitor configuration."""
    print("\n" + "=" * 80)
    print(" " * 20 + "COMPETITOR CONFIGURATION SUMMARY")
    print("=" * 80)

    total_patterns = 0
    for category, rules in config.items():
        n_starts = len(rules.get('starts_with', []))
        n_exact = len(rules.get('exact', []))
        n_contains = len(rules.get('contains', []))
        n_total = n_starts + n_exact + n_contains
        total_patterns += n_total

        display_name = category.replace('_', ' ').title()
        print(f"\n  {display_name}:")
        print(f"    starts_with: {n_starts:3d} patterns")
        if n_exact:
            print(f"    exact:       {n_exact:3d} patterns")
        if n_contains:
            print(f"    contains:    {n_contains:3d} patterns  ⚠ higher false-positive risk")

    print(f"\n{'─' * 80}")
    print(f"  Total categories: {len(config)}")
    print(f"  Total patterns:   {total_patterns}")
    print("=" * 80)


# ===========================================================================
# USAGE EXAMPLE
# ===========================================================================
# --- In your notebook: ---

# 1. Print config summary
print_config_summary()

# 2. Tag competitors in your dataframe
personal_df = tag_competitors(personal_df, merchant_col='merchant_consolidated')

# 3. Quick results check
competitor_txns = personal_df[personal_df['competitor_category'].notna()]
print(f"Competitor transactions found: {len(competitor_txns):,}")
print(competitor_txns['competitor_category'].value_counts())

# 4. Discover potential competitors you might be missing
unmatched = discover_unmatched_financial(personal_df)
if len(unmatched) > 0:
    print("\\n⚠ Potential competitors NOT in config:")
    display(unmatched.head(20))


# M6A: COMPETITOR CONFIGURATION & TRANSACTION DETECTION
# Identifies all competitor transactions across the dataset
print("\n" + "="*120)
print(" " * 40 + "M6A: COMPETITOR CONFIGURATION & DETECTION")
print("="*120)

# ===========================================================================
# COMPETITOR UNIVERSE CONFIGURATION
# ===========================================================================

COMPETITOR_MERCHANTS = {
    'big_nationals': [
        'BANK OF AMERICA',
        'B OF A',
        'WELLS FARGO', 'WELLS FARGO BANK',
        'CHASE', 'JPMORGAN CHASE',
        'US BANK', 'U.S. BANK',
        'CITIBANK', 'CITI',
        'TD BANK', 'TD BANKNORTH',
        'CITIZENS BANK', 'CITIZENS',
        'SANTANDER', 'SANTANDER BANK',
        'KEYBANK', 'KEY BANK',
        'M&T BANK', 'M AND T BANK', 'MANUFACTURERS AND TRADERS',
    ],
    
    'regionals': [
        'WEBSTER BANK',
        'LIBERTY BANK',
        'ION BANK',
        'UNION SAVINGS BANK',
        'NEWTOWN SAVINGS BANK',
        'FAIRFIELD COUNTY BANK',
        'FIRST COUNTY BANK',
        'GUILFORD SAVINGS BANK',
        'ESSEX SAVINGS BANK',
        'MILFORD BANK',
        'BANKWELL',
        'PATRIOT BANK',
        'NORTHWEST COMMUNITY BANK',
        'THOMASTON SAVINGS BANK',
        'CENTREVILLE BANK',
        'IVES BANK',
        'BANK OF NEW HAVEN',
        'CONNECTICUT COMMUNITY BANK',
        'PEOPLES BANK', 'PEOPLESBANK',
    ],
    
    
    'credit_unions': [
        'NEW HAVEN COUNTY CU', 'NHCCU',
        'CROSSPOINT FEDERAL CU', 'CROSSPOINT FCU',
        'AFFINITY FEDERAL CU', 'AFFINITY FCU',
        'USALLIANCE', 'USALLIANCE FINANCIAL',
        'GE CREDIT UNION', 'GE CU',
        'SCIENT FEDERAL CU', 'SCIENT FCU',
        'SCIENCE PARK FCU',
        'MUTUAL SECURITY CU',
        'CT STATE EMPLOYEES CU', 'CONNECTICUT STATE EMPLOYEES CU',
        'ACHIEVE FINANCIAL CU',
        'NAVY FEDERAL', 'NAVY FEDERAL CU',
        'NUTMEG STATE FINANCIAL CU',
        'FINEX CREDIT UNION', 'FINEX CU',
        'WESTERN CT FCU',
        'ISLAND FEDERAL CU',
    ],
    

    
    'digital_banks': [
        'ALLY BANK',
        'DISCOVER BANK',
        'CAPITAL ONE 360',
        'SOFI BANK',
        'SOFI',
        'CHIME',
        'THE BANCORP',
        'STRIDE BANK',
        'VARO BANK',
        'VARO',
        'CURRENT',
        'GO2BANK',
        'GREEN DOT',
        'REVOLUT',
        'MARCUS',
        'GOLDMAN SACHS',
        'SCHWAB BANK',
        'CHARLES SCHWAB',
        'FIDELITY CASH',
        'ROBINHOOD',
        'BETTERMENT',
        'WEALTHFRONT',
    ],
    
    'wallets_p2p': [
        'PAYPAL',
        'VENMO',
        'CASH APP',
        'SQ*',
        'SUTTON',
        'LINCOLN SAVINGS',
        'APPLE CASH',
        'APPLE CARD',
        'GOOGLE PAY',
    ],
    
    'bnpl': [
        'KLARNA',
        'AFTERPAY',
        'AFFIRM',
        'ZIP',
        'QUADPAY',
        'SEZZLE',
    ]
}

print("\n✓ Competitor Universe Configured")
print(f"Total Categories: {len(COMPETITOR_MERCHANTS)}")
for category, merchants in COMPETITOR_MERCHANTS.items():
    print(f"  • {category.replace('_', ' ').title()}: {len(merchants)} competitors")

print(f"\nTotal Competitors to Track: {sum(len(v) for v in COMPETITOR_MERCHANTS.values())}")


# Competition Detetction

# ===========================================================================
# M6A-2: COMPETITOR DETECTION
# ===========================================================================
print("\n" + "="*120)
print(" " * 40 + "M6A-2: SEARCHING FOR COMPETITORS")
print("="*120)

# Tag competitors using the two-tier matching function
combined_df = tag_competitors(combined_df, merchant_col='merchant_consolidated')

# Build summary from tagged results
competitor_txns = combined_df[combined_df['competitor_category'].notna()]

summary_data = competitor_txns.groupby(['competitor_category', 'competitor_match']).agg(
    total_transactions=('amount', 'count'),
    unique_accounts=('primary_account_num', 'nunique'),
    total_amount=('amount', 'sum')
).reset_index().rename(columns={
    'competitor_category': 'category',
    'competitor_match': 'competitor'
}).sort_values('total_amount', ascending=False)

# Also tag business and personal if they exist
if 'business_df' in dir() and len(business_df) > 0:
    business_df = tag_competitors(business_df, merchant_col='merchant_consolidated')
if 'personal_df' in dir() and len(personal_df) > 0:
    personal_df = tag_competitors(personal_df, merchant_col='merchant_consolidated')

print(f"\nSearched {len(combined_df):,} transactions")
print(f"✓ Competitor transactions found: {len(competitor_txns):,}")
print(f"✓ Unique patterns matched: {competitor_txns['competitor_match'].nunique()}")
print(f"✓ Categories with activity: {competitor_txns['competitor_category'].nunique()}")

# Summary by category
print(f"\nBy category:")
cat_summary = competitor_txns.groupby('competitor_category').agg(
    transactions=('amount', 'count'),
    spend=('amount', 'sum'),
    accounts=('primary_account_num', 'nunique')
)
for cat, row in cat_summary.iterrows():
    print(f"  • {cat.replace('_', ' ').title():20s} {row['transactions']:>8,} txns  ${row['spend']:>12,.2f}  ({row['accounts']:,} accounts)")

print("="*120)


# In your reporting, split these
TRUE_COMPETITORS = ['big_nationals', 'regionals', 'credit_unions', 'digital_banks']
PAYMENT_ECOSYSTEMS = ['wallets_p2p', 'bnpl']

# Filter for actual competitive threats
true_competitor_txns = competitor_txns[competitor_txns['competitor_category'].isin(TRUE_COMPETITORS)]
ecosystem_txns = competitor_txns[competitor_txns['competitor_category'].isin(PAYMENT_ECOSYSTEMS)]

print(f"True competitor spend:      ${true_competitor_txns['amount'].sum():>14,.2f}")
print(f"Payment ecosystem spend:    ${ecosystem_txns['amount'].sum():>14,.2f}")


# Competitor Quick Summary

# ===========================================================================
# M6A-3: QUICK SUMMARY
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6A-3: COMPETITOR DETECTION SUMMARY")
print("="*120)

if len(all_competitor_data) == 0:
    print("\n⚠ No competitor transactions found")
else:
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('total_amount', ascending=False)
    
    total_competitor_trans = summary_df['total_transactions'].sum()
    total_competitor_spend = summary_df['total_amount'].sum()
    total_competitor_accounts = summary_df['unique_accounts'].sum()
    
    print(f"\n✓ Found {len(all_competitor_data)} competitors with activity")
    print(f"  • Total Transactions: {total_competitor_trans:,}")
    print(f"  • Total Spend: ${total_competitor_spend:,.2f}")
    print(f"  • Unique Accounts: {total_competitor_accounts:,}")
    
    # Quick category breakdown
    print("\n📊 By Category:")
    category_summary = summary_df.groupby('category')['total_amount'].sum().sort_values(ascending=False)
    for cat, amount in category_summary.items():
        print(f"  • {cat.replace('_', ' ').title()}: ${amount:,.0f}")

print("\n" + "="*120)
print("✓ Detection complete - data in 'all_competitor_data' and 'summary_data'")
print("="*120)


# ============================================
# COMPETITOR VALIDATION: Find Missing Patterns
# ============================================

import pandas as pd

# First, let's see what you're actually capturing
def audit_competitor_matches(df, competitor_dict):
    """
    Shows exactly which merchants matched and which might be missed
    """
    
    print("=" * 60)
    print("COMPETITOR MATCH AUDIT")
    print("=" * 60)
    
    for category, patterns in competitor_dict.items():
        print(f"\n📁 {category.upper()}")
        print("-" * 60)
        
        for pattern in patterns:
            # Find all merchants that match this pattern
            matches = df[df['merchant_name'].str.contains(pattern, case=False, na=False)]
            
            if len(matches) > 0:
                unique_merchants = matches['merchant_name'].unique()
                total_spend = matches['amount'].sum()
                total_txns = len(matches)
                
                print(f"\n  ✓ Pattern: '{pattern}'")
                print(f"    Spend: ${total_spend:,.2f} | Txns: {total_txns:,}")
                print(f"    Matched merchant names ({len(unique_merchants)}):")
                
                # Show first 10 actual merchant names
                for merchant in sorted(unique_merchants)[:10]:
                    merchant_spend = matches[matches['merchant_name'] == merchant]['amount'].sum()
                    print(f"      • {merchant}: ${merchant_spend:,.2f}")
                
                if len(unique_merchants) > 10:
                    print(f"      ... and {len(unique_merchants) - 10} more")
            else:
                print(f"\n  ✗ Pattern: '{pattern}' - NO MATCHES FOUND")

# Run the audit
audit_competitor_matches(combined_df, all_competitors)


# ============================================
# SANITY CHECK: Search for competitors manually
# ============================================

def find_potential_competitors(df, search_terms):
    """
    Broad search to see if competitors exist in data at all
    """
    
    print("\n" + "=" * 60)
    print("BROAD COMPETITOR SEARCH")
    print("=" * 60)
    
    for term in search_terms:
        matches = df[df['merchant_name'].str.contains(term, case=False, na=False)]
        
        if len(matches) > 0:
            print(f"\n🔍 Search: '{term}'")
            print(f"   Found: {len(matches):,} transactions | ${matches['amount'].sum():,.2f}")
            print(f"   Sample merchants:")
            
            # Show top 5 by spend
            top_merchants = matches.groupby('merchant_name')['amount'].agg(['sum', 'count'])
            top_merchants = top_merchants.sort_values('sum', ascending=False).head(5)
            
            for merchant, row in top_merchants.iterrows():
                print(f"      • {merchant}")
                print(f"        ${row['sum']:,.2f} | {int(row['count']):,} txns")
        else:
            print(f"\n✗ Search: '{term}' - Nothing found")

# Test with common competitor names
search_terms = [
    'CHIME',
    'CASH APP',
    'VENMO',
    'PAYPAL',
    'SOFI',
    'ALLY',
    'MARCUS',
    'CAPITAL ONE',
    'DISCOVER',
    'CHASE',
    'AFFIRM',
    'AFTERPAY',
    'KLARNA',
    'ZIP',
    'NAVY FEDERAL',
    'USAA',
    'PNC',
    'WELLS FARGO',
    'BANK OF AMERICA'
]

find_potential_competitors(combined_df, search_terms)


# ===========================================================================
# COMPETITOR SPEND ANALYSIS - ACCOUNT SEGMENTATION
# ===========================================================================
"""
## Creates competitor_spend_analysis dictionary for segmentation
Analyzes what % of each account's spend goes to each competitor
"""

print("\n" + "="*120)
print(" " * 40 + "ANALYZING COMPETITOR SPEND BY ACCOUNT")
print("="*120)

if len(all_competitor_data) == 0:
    print("\n⚠ No competitor data found - run M6A detection first!")
else:
    competitor_spend_analysis = {}
    
    # Get total spend per account (for percentage calculations)
    account_totals = combined_df.groupby('primary_account_num')['amount'].sum()
    
    print(f"\nAnalyzing spend patterns for {len(all_competitor_data)} competitors...")
    
    for competitor, competitor_trans in all_competitor_data.items():
        # Get spend per account for this competitor
        competitor_spend_by_account = competitor_trans.groupby('primary_account_num')['amount'].sum()
        
        # Create comparison dataframe
        comparison = pd.DataFrame({
            'account': competitor_spend_by_account.index,
            'competitor_spend': competitor_spend_by_account.values
        })
        
        # Add total spend for each account
        comparison['total_spend'] = comparison['account'].map(account_totals)
        
        # Calculate percentage
        comparison['competitor_pct'] = (comparison['competitor_spend'] / comparison['total_spend'] * 100)
        
        # Segment accounts
        comparison['Segment'] = pd.cut(
            comparison['competitor_pct'],
            bins=[0, 25, 50, 100],
            labels=['CU-Focused', 'Balanced', 'Competitor-Heavy'],
            include_lowest=True
        )
        
        # Store in dictionary
        competitor_spend_analysis[competitor] = comparison
    
    print(f"✓ Analysis complete for {len(competitor_spend_analysis)} competitors")
    
    # Quick summary
    total_heavy = sum(len(df[df['Segment'] == 'Competitor-Heavy']) for df in competitor_spend_analysis.values())
    total_balanced = sum(len(df[df['Segment'] == 'Balanced']) for df in competitor_spend_analysis.values())
    total_cu = sum(len(df[df['Segment'] == 'CU-Focused']) for df in competitor_spend_analysis.values())
    
    print(f"\nOverall Segmentation:")
    print(f"  • Competitor-Heavy accounts: {total_heavy:,}")
    print(f"  • Balanced accounts: {total_balanced:,}")
    print(f"  • CU-Focused accounts: {total_cu:,}")

print("="*120)


# ---- Competitor Analysis ----

# Summary

# ===========================================================================
# OVERALL SUMMARY
# ===========================================================================

print("\n" + "="*120)
print("COMPETITOR DETECTION SUMMARY")
print("="*120)

if len(all_competitor_data) > 0:
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('total_amount', ascending=False)
    
    # Format for display
    summary_display = summary_df.copy()
    summary_display['category'] = summary_display['category'].str.replace('_', ' ').str.title()
    summary_display['total_amount'] = summary_display['total_amount'].apply(lambda x: f"${x:,.0f}")
    summary_display['total_transactions'] = summary_display['total_transactions'].apply(lambda x: f"{x:,}")
    summary_display['unique_accounts'] = summary_display['unique_accounts'].apply(lambda x: f"{x:,}")
    
    summary_display.columns = ['Competitor', 'Category', 'Transactions', 'Unique Accounts', 'Total Amount']
    
    print(f"\n✓ Found {len(all_competitor_data)} competitors with transaction activity")
    print(f"Total Competitor Transactions: {summary_df['total_transactions'].sum():,}")
    print(f"Total Competitor Spend: ${summary_df['total_amount'].sum():,.2f}")
    print(f"Unique Accounts Using Competitors: {summary_df['unique_accounts'].sum():,}\n")
    
    display(summary_display.style.hide(axis='index'))
    
    # Category breakdown
    print("\n📊 BY CATEGORY:")
    category_summary = summary_df.groupby('category').agg({
        'total_transactions': 'sum',
        'unique_accounts': 'sum',
        'total_amount': 'sum',
        'competitor': 'count'
    }).sort_values('total_amount', ascending=False)
    
    category_summary.columns = ['Total Transactions', 'Total Accounts', 'Total Amount', 'Competitor Count']
    category_display = category_summary.copy()
    category_display.index = category_display.index.str.replace('_', ' ').str.title()
    category_display['Total Transactions'] = category_display['Total Transactions'].apply(lambda x: f"{x:,}")
    category_display['Total Accounts'] = category_display['Total Accounts'].apply(lambda x: f"{x:,}")
    category_display['Total Amount'] = category_display['Total Amount'].apply(lambda x: f"${x:,.0f}")
    
    display(category_display)
    
else:
    print("\n⚠ No competitor transactions found in dataset")

print("\n" + "="*120)
print("✓ Competitor detection complete - data stored in 'all_competitor_data' dictionary")
print("="*120)


# Competition Metrics

# ===========================================================================
# M6B-1: HIGH-LEVEL METRICS
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-1: HIGH-LEVEL COMPETITOR METRICS")
print("="*120)

if len(all_competitor_data) == 0:
    print("\n⚠ No competitor data to analyze")
else:
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('total_amount', ascending=False)
    
    total_competitor_trans = summary_df['total_transactions'].sum()
    total_competitor_spend = summary_df['total_amount'].sum()
    total_competitor_accounts = summary_df['unique_accounts'].sum()
    total_competitors_found = len(all_competitor_data)
    
    # Calculate as % of overall dataset
    total_all_trans = len(combined_df)
    total_all_spend = combined_df['amount'].sum()
    total_all_accounts = combined_df['primary_account_num'].nunique()
    
    pct_trans = (total_competitor_trans / total_all_trans * 100) if total_all_trans > 0 else 0
    pct_spend = (total_competitor_spend / total_all_spend * 100) if total_all_spend > 0 else 0
    pct_accounts = (total_competitor_accounts / total_all_accounts * 100) if total_all_accounts > 0 else 0
    
    metrics_summary = pd.DataFrame({
        'Metric': [
            'Competitors Found',
            '',
            'Total Competitor Transactions',
            '% of All Transactions',
            '',
            'Total Competitor Spend',
            '% of All Spend',
            '',
            'Unique Accounts Using Competitors',
            '% of All Accounts',
            '',
            'Avg Spend per Competitor Account',
            'Avg Transactions per Competitor Account'
        ],
        'Value': [
            f"{total_competitors_found:,}",
            '',
            f"{total_competitor_trans:,}",
            f"{pct_trans:.2f}%",
            '',
            f"${total_competitor_spend:,.2f}",
            f"{pct_spend:.2f}%",
            '',
            f"{total_competitor_accounts:,}",
            f"{pct_accounts:.2f}%",
            '',
            f"${total_competitor_spend / total_competitor_accounts:,.2f}" if total_competitor_accounts > 0 else "$0.00",
            f"{total_competitor_trans / total_competitor_accounts:.1f}" if total_competitor_accounts > 0 else "0.0"
        ]
    })
    
    display(metrics_summary.style.hide(axis='index'))

print("="*120)


# Top 20 Competitions by Spend and FinServ

# ===========================================================================
# M6B-2: TOP 20 COMPETITORS BY SPEND
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-2: TOP 20 COMPETITORS BY SPEND")
print("="*120)

if len(all_competitor_data) > 0:
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('total_amount', ascending=False)
    
    top_20 = summary_df.head(20).copy()
    top_20_display = top_20.copy()
    top_20_display['category'] = top_20_display['category'].str.replace('_', ' ').str.title()
    top_20_display['total_amount'] = top_20_display['total_amount'].apply(lambda x: f"${x:,.0f}")
    top_20_display['total_transactions'] = top_20_display['total_transactions'].apply(lambda x: f"{x:,}")
    top_20_display['unique_accounts'] = top_20_display['unique_accounts'].apply(lambda x: f"{x:,}")
    
    # Add average per account
    top_20_display['avg_per_account'] = top_20.apply(
        lambda row: f"${row['total_amount'] / row['unique_accounts']:,.2f}", 
        axis=1
    )
    
    top_20_display.columns = ['Competitor', 'Category', 'Transactions', 'Unique Accounts', 'Total Spend', 'Avg per Account']
    
    display(top_20_display.style.hide(axis='index'))

print("="*120)


# Competitor Category Breakdown

# ===========================================================================
# M6B-3: CATEGORY BREAKDOWN
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-3: BREAKDOWN BY CATEGORY")
print("="*120)

if len(all_competitor_data) > 0:
    summary_df = pd.DataFrame(summary_data)
    
    category_summary = summary_df.groupby('category').agg({
        'total_transactions': 'sum',
        'unique_accounts': 'sum',
        'total_amount': 'sum',
        'competitor': 'count'
    }).sort_values('total_amount', ascending=False)
    
    category_summary.columns = ['Total Transactions', 'Total Accounts', 'Total Spend', 'Competitor Count']
    
    # Add percentages
    category_summary['% of Competitor Spend'] = (
        category_summary['Total Spend'] / category_summary['Total Spend'].sum() * 100
    )
    category_summary['Avg per Competitor'] = (
        category_summary['Total Spend'] / category_summary['Competitor Count']
    )
    
    category_display = category_summary.copy()
    category_display.index = category_display.index.str.replace('_', ' ').str.title()
    category_display['Total Transactions'] = category_display['Total Transactions'].apply(lambda x: f"{int(x):,}")
    category_display['Total Accounts'] = category_display['Total Accounts'].apply(lambda x: f"{int(x):,}")
    category_display['Total Spend'] = category_display['Total Spend'].apply(lambda x: f"${x:,.0f}")
    category_display['% of Competitor Spend'] = category_display['% of Competitor Spend'].apply(lambda x: f"{x:.1f}%")
    category_display['Avg per Competitor'] = category_display['Avg per Competitor'].apply(lambda x: f"${x:,.0f}")
    
    display(category_display)

print("="*120)


# P/B Split

# ===========================================================================
# M6B-4: BUSINESS VS PERSONAL SPLIT
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-4: BUSINESS VS PERSONAL ACCOUNT SPLIT")
print("="*120)

if len(all_competitor_data) > 0:
    # Combine all competitor transactions
    all_competitor_trans = pd.concat(all_competitor_data.values(), ignore_index=True)
    
    if 'business_flag' in all_competitor_trans.columns:
        business_split = all_competitor_trans.groupby('business_flag').agg({
            'amount': ['sum', 'count', 'mean'],
            'primary_account_num': 'nunique'
        }).round(2)
        
        business_split.columns = ['Total Spend', 'Transaction Count', 'Avg Transaction', 'Unique Accounts']
        
        # Add percentages
        business_split['% of Competitor Spend'] = (
            business_split['Total Spend'] / business_split['Total Spend'].sum() * 100
        )
        business_split['% of Competitor Accounts'] = (
            business_split['Unique Accounts'] / business_split['Unique Accounts'].sum() * 100
        )
        
        business_display = business_split.copy()
        business_display.index = business_display.index.map({'Yes': '💼 Business Accounts', 'No': '👤 Personal Accounts'})
        business_display['Total Spend'] = business_display['Total Spend'].apply(lambda x: f"${x:,.2f}")
        business_display['Transaction Count'] = business_display['Transaction Count'].apply(lambda x: f"{int(x):,}")
        business_display['Avg Transaction'] = business_display['Avg Transaction'].apply(lambda x: f"${x:,.2f}")
        business_display['Unique Accounts'] = business_display['Unique Accounts'].apply(lambda x: f"{int(x):,}")
        business_display['% of Competitor Spend'] = business_display['% of Competitor Spend'].apply(lambda x: f"{x:.1f}%")
        business_display['% of Competitor Accounts'] = business_display['% of Competitor Accounts'].apply(lambda x: f"{x:.1f}%")
        
        display(business_display)
    else:
        print("\n⚠ No business_flag column found in competitor data")

print("="*120)


# Monthly Competition Spend

# ===========================================================================
# M6B-5: MONTHLY TREND ANALYSIS
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-5: MONTHLY TREND ANALYSIS")
print("="*120)

if len(all_competitor_data) > 0:
    # Combine all competitor transactions
    all_competitor_trans = pd.concat(all_competitor_data.values(), ignore_index=True)
    
    # Add year_month if not present
    if 'year_month' not in all_competitor_trans.columns:
        all_competitor_trans['year_month'] = pd.to_datetime(all_competitor_trans['transaction_date']).dt.to_period('M')
    
    monthly_trends = all_competitor_trans.groupby('year_month').agg({
        'amount': ['sum', 'count'],
        'primary_account_num': 'nunique'
    }).round(2)
    
    monthly_trends.columns = ['Total Spend', 'Transaction Count', 'Unique Accounts']
    monthly_trends = monthly_trends.sort_index()
    
    # Calculate month-over-month growth
    monthly_trends['Spend Growth %'] = monthly_trends['Total Spend'].pct_change() * 100
    monthly_trends['Transaction Growth %'] = monthly_trends['Transaction Count'].pct_change() * 100
    
    # Format for display
    monthly_display = monthly_trends.copy()
    monthly_display.index = monthly_display.index.astype(str)
    monthly_display['Total Spend'] = monthly_display['Total Spend'].apply(lambda x: f"${x:,.0f}")
    monthly_display['Transaction Count'] = monthly_display['Transaction Count'].apply(lambda x: f"{int(x):,}")
    monthly_display['Unique Accounts'] = monthly_display['Unique Accounts'].apply(lambda x: f"{int(x):,}")
    monthly_display['Spend Growth %'] = monthly_display['Spend Growth %'].apply(
        lambda x: f"{x:+.1f}%" if pd.notna(x) else "-"
    )
    monthly_display['Transaction Growth %'] = monthly_display['Transaction Growth %'].apply(
        lambda x: f"{x:+.1f}%" if pd.notna(x) else "-"
    )
    
    display(monthly_display)

print("="*120)


# ---- Competitive Risk Assessment ----

# ===========================================================================
# M6B-6: TOP COMPETITOR BY CATEGORY
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-6: TOP COMPETITOR IN EACH CATEGORY")
print("="*120)

if len(all_competitor_data) > 0:
    summary_df = pd.DataFrame(summary_data)
    
    # Get top competitor per category
    top_by_category = summary_df.loc[summary_df.groupby('category')['total_amount'].idxmax()].copy()
    
    # Add market context
    category_totals = summary_df.groupby('category')['total_amount'].sum()
    top_by_category['category_total'] = top_by_category['category'].map(category_totals)
    top_by_category['market_share_pct'] = (top_by_category['total_amount'] / top_by_category['category_total'] * 100)
    
    # Format for display
    display_df = top_by_category[['category', 'competitor', 'total_amount', 'unique_accounts', 'market_share_pct']].copy()
    display_df = display_df.sort_values('total_amount', ascending=False)
    
    display_df['category'] = display_df['category'].str.replace('_', ' ').str.title()
    display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"${x:,.0f}")
    display_df['unique_accounts'] = display_df['unique_accounts'].apply(lambda x: f"{x:,}")
    display_df['market_share_pct'] = display_df['market_share_pct'].apply(lambda x: f"{x:.1f}%")
    
    display_df.columns = ['Category', 'Top Competitor', 'Total Spend', 'Unique Accounts', '% of Category']
    
    print("\n")
    display(display_df.style.hide(axis='index'))
    
    print("\n💡 Insight: Shows the dominant competitor in each competitive category")

print("="*120)


# Bank Competetive Threat Assessment

# ===========================================================================
# M6B-6: BANK COMPETITIVE THREAT ASSESSMENT
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-6: BANK COMPETITIVE THREAT ASSESSMENT")
print("="*120)

if len(all_competitor_data) > 0:
    threat_data = []
    
    # ONLY assess threats from actual banks
    bank_categories = ['big_nationals', 'regionals', 'credit_unions', 'digital_banks']
    
    # Get total accounts for penetration calculation
    total_accounts = combined_df['primary_account_num'].nunique()
    
    for competitor, competitor_trans in all_competitor_data.items():
        category = competitor_trans['competitor_category'].iloc[0]
        
        # Skip if not a bank
        if category not in bank_categories:
            continue
        
        total_spend = competitor_trans['amount'].sum()
        unique_accounts = competitor_trans['primary_account_num'].nunique()
        
        # Account penetration (% of total accounts using this competitor)
        penetration_pct = (unique_accounts / total_accounts) * 100
        
        # Calculate recent growth (last 3 months vs previous 3 months)
        if 'year_month' not in competitor_trans.columns:
            competitor_trans['year_month'] = pd.to_datetime(competitor_trans['transaction_date']).dt.to_period('M')
        
        sorted_months = sorted(competitor_trans['year_month'].unique())
        
        if len(sorted_months) >= 6:
            recent_3 = sorted_months[-3:]
            previous_3 = sorted_months[-6:-3]
            
            recent_spend = competitor_trans[competitor_trans['year_month'].isin(recent_3)]['amount'].sum()
            previous_spend = competitor_trans[competitor_trans['year_month'].isin(previous_3)]['amount'].sum()
            
            growth_rate = ((recent_spend - previous_spend) / previous_spend * 100) if previous_spend > 0 else 0
        else:
            growth_rate = 0
        
        # Threat Score = Weighted combination
        # 40% = Account penetration (how many accounts they've captured)
        # 30% = Total spend (how much money is at risk)
        # 30% = Growth rate (are they gaining momentum?)
        
        threat_score = (
            (penetration_pct * 4) +  # Weight: 40%
            (total_spend / 100000) * 3 +  # Weight: 30%
            (max(growth_rate, 0) / 10) * 3  # Weight: 30% (only positive growth)
        )
        
        threat_data.append({
            'competitor': competitor,
            'category': category,
            'total_spend': total_spend,
            'unique_accounts': unique_accounts,
            'penetration_pct': penetration_pct,
            'growth_rate': growth_rate,
            'threat_score': threat_score
        })
    
    if len(threat_data) > 0:
        threat_df = pd.DataFrame(threat_data).sort_values('threat_score', ascending=False).head(15)
        
        # Format for display
        display_df = threat_df.copy()
        display_df['category'] = display_df['category'].str.replace('_', ' ').str.title()
        display_df['total_spend'] = display_df['total_spend'].apply(lambda x: f"${x:,.0f}")
        display_df['unique_accounts'] = display_df['unique_accounts'].apply(lambda x: f"{x:,}")
        display_df['penetration_pct'] = display_df['penetration_pct'].apply(lambda x: f"{x:.2f}%")
        display_df['growth_rate'] = display_df['growth_rate'].apply(lambda x: f"{x:+.1f}%")
        display_df['threat_score'] = display_df['threat_score'].apply(lambda x: f"{x:.1f}")
        
        display_df.columns = [
            'Bank', 'Category', 'Total Spend', 'Accounts', 
            'Penetration', 'Growth (6mo)', 'Threat Score'
        ]
        
        print("\nTop 15 Bank Competitive Threats:")
        print("Threat Score = 40% Penetration + 30% Total Spend + 30% Growth Rate")
        print("(Excludes wallets/P2P/BNPL - those are threats to banking itself, not direct competitors)\n")
        display(display_df.style.hide(axis='index'))
        
        print("\n💡 Highest threat = High account penetration + Large spend + Growing momentum")
    else:
        print("\n⚠ No bank competitors found in dataset")

print("="*120)


# Bank Threats - Account Penetration

# ===========================================================================
# M6B-6a: BANK THREATS BY ACCOUNT PENETRATION
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-6a: BANK THREATS BY ACCOUNT PENETRATION")
print("="*120)

if len(all_competitor_data) > 0:
    bank_categories = ['big_nationals', 'regionals', 'credit_unions', 'digital_banks']
    total_accounts = combined_df['primary_account_num'].nunique()
    
    penetration_data = []
    
    for competitor, competitor_trans in all_competitor_data.items():
        category = competitor_trans['competitor_category'].iloc[0]
        
        if category not in bank_categories:
            continue
        
        unique_accounts = competitor_trans['primary_account_num'].nunique()
        total_spend = competitor_trans['amount'].sum()
        transaction_count = len(competitor_trans)
        avg_spend_per_account = total_spend / unique_accounts if unique_accounts > 0 else 0
        
        penetration_pct = (unique_accounts / total_accounts) * 100
        
        penetration_data.append({
            'bank': competitor,
            'category': category,
            'unique_accounts': unique_accounts,
            'penetration_pct': penetration_pct,
            'total_spend': total_spend,
            'transaction_count': transaction_count,
            'avg_per_account': avg_spend_per_account
        })
    
    if len(penetration_data) > 0:
        pen_df = pd.DataFrame(penetration_data).sort_values('unique_accounts', ascending=False).head(15)
        
        display_df = pen_df.copy()
        display_df['category'] = display_df['category'].str.replace('_', ' ').str.title()
        display_df['unique_accounts'] = display_df['unique_accounts'].apply(lambda x: f"{x:,}")
        display_df['penetration_pct'] = display_df['penetration_pct'].apply(lambda x: f"{x:.2f}%")
        display_df['total_spend'] = display_df['total_spend'].apply(lambda x: f"${x:,.0f}")
        display_df['transaction_count'] = display_df['transaction_count'].apply(lambda x: f"{x:,}")
        display_df['avg_per_account'] = display_df['avg_per_account'].apply(lambda x: f"${x:,.0f}")
        
        display_df.columns = [
            'Bank', 'Category', 'Accounts', 'Penetration %', 
            'Total Spend', 'Transactions', 'Avg per Account'
        ]
        
        print("\nTop 15 Banks by Raw Account Penetration:")
        print("(Simple ranking by number of accounts captured)\n")
        display(display_df.style.hide(axis='index'))
        
        print("\n💡 Shows which banks have captured the most customer relationships")

print("="*120)


# Bank Threats - Total Spend

# ===========================================================================
# M6B-6b: BANK THREATS BY TOTAL SPEND
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-6b: BANK THREATS BY TOTAL SPEND")
print("="*120)

if len(all_competitor_data) > 0:
    bank_categories = ['big_nationals', 'regionals', 'credit_unions', 'digital_banks']
    
    spend_data = []
    
    for competitor, competitor_trans in all_competitor_data.items():
        category = competitor_trans['competitor_category'].iloc[0]
        
        if category not in bank_categories:
            continue
        
        total_spend = competitor_trans['amount'].sum()
        unique_accounts = competitor_trans['primary_account_num'].nunique()
        transaction_count = len(competitor_trans)
        avg_transaction = total_spend / transaction_count if transaction_count > 0 else 0
        
        spend_data.append({
            'bank': competitor,
            'category': category,
            'total_spend': total_spend,
            'unique_accounts': unique_accounts,
            'transaction_count': transaction_count,
            'avg_transaction': avg_transaction
        })
    
    if len(spend_data) > 0:
        spend_df = pd.DataFrame(spend_data).sort_values('total_spend', ascending=False).head(15)
        
        display_df = spend_df.copy()
        display_df['category'] = display_df['category'].str.replace('_', ' ').str.title()
        display_df['total_spend'] = display_df['total_spend'].apply(lambda x: f"${x:,.0f}")
        display_df['unique_accounts'] = display_df['unique_accounts'].apply(lambda x: f"{x:,}")
        display_df['transaction_count'] = display_df['transaction_count'].apply(lambda x: f"{x:,}")
        display_df['avg_transaction'] = display_df['avg_transaction'].apply(lambda x: f"${x:,.2f}")
        
        display_df.columns = [
            'Bank', 'Category', 'Total Spend', 'Accounts', 
            'Transactions', 'Avg Transaction'
        ]
        
        print("\nTop 15 Banks by Total Spend:")
        print("(Follow the money - where is the most spend going?)\n")
        display(display_df.style.hide(axis='index'))
        
        print("\n💡 Shows which banks are capturing the most transaction volume in dollars")

print("="*120)


# Bank Threats - Momentum

# ===========================================================================
# M6B-6c: FASTEST GROWING BANKS (MOMENTUM)
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-6c: FASTEST GROWING BANKS (MOMENTUM)")
print("="*120)

if len(all_competitor_data) > 0:
    bank_categories = ['big_nationals', 'regionals', 'credit_unions', 'digital_banks']
    
    growth_data = []
    
    for competitor, competitor_trans in all_competitor_data.items():
        category = competitor_trans['competitor_category'].iloc[0]
        
        if category not in bank_categories:
            continue
        
        # Ensure year_month exists
        if 'year_month' not in competitor_trans.columns:
            competitor_trans['year_month'] = pd.to_datetime(competitor_trans['transaction_date']).dt.to_period('M')
        
        sorted_months = sorted(competitor_trans['year_month'].unique())
        
        # Need at least 6 months to calculate growth
        if len(sorted_months) < 6:
            continue
        
        recent_3 = sorted_months[-3:]
        previous_3 = sorted_months[-6:-3]
        
        recent_spend = competitor_trans[competitor_trans['year_month'].isin(recent_3)]['amount'].sum()
        previous_spend = competitor_trans[competitor_trans['year_month'].isin(previous_3)]['amount'].sum()
        
        recent_accounts = competitor_trans[competitor_trans['year_month'].isin(recent_3)]['primary_account_num'].nunique()
        previous_accounts = competitor_trans[competitor_trans['year_month'].isin(previous_3)]['primary_account_num'].nunique()
        
        spend_growth = ((recent_spend - previous_spend) / previous_spend * 100) if previous_spend > 0 else 0
        account_growth = ((recent_accounts - previous_accounts) / previous_accounts * 100) if previous_accounts > 0 else 0
        
        # Only show positive growth
        if spend_growth > 0:
            growth_data.append({
                'bank': competitor,
                'category': category,
                'spend_growth': spend_growth,
                'account_growth': account_growth,
                'recent_spend': recent_spend,
                'recent_accounts': recent_accounts,
                'previous_spend': previous_spend
            })
    
    if len(growth_data) > 0:
        growth_df = pd.DataFrame(growth_data).sort_values('spend_growth', ascending=False).head(15)
        
        display_df = growth_df.copy()
        display_df['category'] = display_df['category'].str.replace('_', ' ').str.title()
        display_df['spend_growth'] = display_df['spend_growth'].apply(lambda x: f"{x:+.1f}%")
        display_df['account_growth'] = display_df['account_growth'].apply(lambda x: f"{x:+.1f}%")
        display_df['recent_spend'] = display_df['recent_spend'].apply(lambda x: f"${x:,.0f}")
        display_df['previous_spend'] = display_df['previous_spend'].apply(lambda x: f"${x:,.0f}")
        display_df['recent_accounts'] = display_df['recent_accounts'].apply(lambda x: f"{x:,}")
        
        display_df.columns = [
            'Bank', 'Category', 'Spend Growth', 'Account Growth', 
            'Recent Spend (3mo)', 'Accounts (Recent)', 'Previous Spend (3mo)'
        ]
        
        print("\nTop 15 Fastest Growing Banks:")
        print("(Last 3 months vs previous 3 months)\n")
        display(display_df.style.hide(axis='index'))
        
        print("\n💡 Shows which banks are gaining momentum - growing spend and accounts")
        print("⚠️ Note: Small banks can show high % growth from low base")
    else:
        print("\n⚠ Insufficient data to calculate growth rates (need 6+ months)")

print("="*120)


# Material Threats

# ===========================================================================
# M6B-6d: MATERIAL THREATS (BALANCED VIEW)
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-6d: MATERIAL THREATS (BALANCED VIEW)")
print("="*120)

if len(all_competitor_data) > 0:
    bank_categories = ['big_nationals', 'regionals', 'credit_unions', 'digital_banks']
    total_accounts = combined_df['primary_account_num'].nunique()
    
    # Set minimum thresholds for "material" threats
    MIN_ACCOUNTS = 100  # Must have at least 100 accounts
    MIN_SPEND = 50000   # Must have at least $50K in spend
    
    material_data = []
    
    for competitor, competitor_trans in all_competitor_data.items():
        category = competitor_trans['competitor_category'].iloc[0]
        
        if category not in bank_categories:
            continue
        
        unique_accounts = competitor_trans['primary_account_num'].nunique()
        total_spend = competitor_trans['amount'].sum()
        
        # Filter out immaterial competitors
        if unique_accounts < MIN_ACCOUNTS or total_spend < MIN_SPEND:
            continue
        
        penetration_pct = (unique_accounts / total_accounts) * 100
        
        # Calculate growth if enough data
        if 'year_month' not in competitor_trans.columns:
            competitor_trans['year_month'] = pd.to_datetime(competitor_trans['transaction_date']).dt.to_period('M')
        
        sorted_months = sorted(competitor_trans['year_month'].unique())
        
        if len(sorted_months) >= 6:
            recent_3 = sorted_months[-3:]
            previous_3 = sorted_months[-6:-3]
            
            recent_spend = competitor_trans[competitor_trans['year_month'].isin(recent_3)]['amount'].sum()
            previous_spend = competitor_trans[competitor_trans['year_month'].isin(previous_3)]['amount'].sum()
            
            growth_rate = ((recent_spend - previous_spend) / previous_spend * 100) if previous_spend > 0 else 0
        else:
            growth_rate = 0
        
        # Balanced threat score
        # 50% = Account penetration (market share)
        # 50% = Total spend (absolute dollars at risk)
        # Growth rate shown separately, not in score
        
        threat_score = (
            (penetration_pct * 5) +  # 50% weight
            (total_spend / 100000) * 5  # 50% weight
        )
        
        material_data.append({
            'bank': competitor,
            'category': category,
            'unique_accounts': unique_accounts,
            'penetration_pct': penetration_pct,
            'total_spend': total_spend,
            'growth_rate': growth_rate,
            'threat_score': threat_score
        })
    
    if len(material_data) > 0:
        material_df = pd.DataFrame(material_data).sort_values('threat_score', ascending=False).head(15)
        
        display_df = material_df.copy()
        display_df['category'] = display_df['category'].str.replace('_', ' ').str.title()
        display_df['unique_accounts'] = display_df['unique_accounts'].apply(lambda x: f"{x:,}")
        display_df['penetration_pct'] = display_df['penetration_pct'].apply(lambda x: f"{x:.2f}%")
        display_df['total_spend'] = display_df['total_spend'].apply(lambda x: f"${x:,.0f}")
        display_df['growth_rate'] = display_df['growth_rate'].apply(lambda x: f"{x:+.1f}%")
        display_df['threat_score'] = display_df['threat_score'].apply(lambda x: f"{x:.1f}")
        
        display_df.columns = [
            'Bank', 'Category', 'Accounts', 'Penetration', 
            'Total Spend', 'Growth (6mo)', 'Threat Score'
        ]
        
        print("\nTop 15 Material Bank Threats:")
        print(f"Minimum Thresholds: {MIN_ACCOUNTS:,} accounts AND ${MIN_SPEND:,} spend")
        print("Threat Score = 50% Penetration + 50% Total Spend (Growth shown separately)\n")
        display(display_df.style.hide(axis='index'))
        
        print("\n💡 Filters out small players - focuses on banks with meaningful market presence")
        print("   High score = Significant market share + Large absolute dollars at risk")
    else:
        print(f"\n⚠ No banks meet minimum thresholds ({MIN_ACCOUNTS} accounts, ${MIN_SPEND} spend)")

print("="*120)


# Non-Bank Threats

# ===========================================================================
# M6B-7: NON-BANK THREATS TO BANKING RELATIONSHIP
# ===========================================================================

print("\n" + "="*120)
print(" " * 40 + "M6B-7: NON-BANK THREATS TO BANKING RELATIONSHIP")
print("="*120)

if len(all_competitor_data) > 0:
    # These aren't competing banks - they're replacing banking functions
    non_bank_categories = ['wallets_p2p', 'bnpl']
    
    # Get total accounts
    total_accounts = combined_df['primary_account_num'].nunique()
    total_spend = combined_df['amount'].sum()
    
    non_bank_data = []
    
    for competitor, competitor_trans in all_competitor_data.items():
        category = competitor_trans['competitor_category'].iloc[0]
        
        # Only look at non-bank threats
        if category not in non_bank_categories:
            continue
        
        comp_spend = competitor_trans['amount'].sum()
        unique_accounts = competitor_trans['primary_account_num'].nunique()
        transaction_count = len(competitor_trans)
        
        # Penetration
        penetration_pct = (unique_accounts / total_accounts) * 100
        
        # % of total spend going through this service
        spend_share = (comp_spend / total_spend) * 100
        
        non_bank_data.append({
            'service': competitor,
            'category': category,
            'total_spend': comp_spend,
            'unique_accounts': unique_accounts,
            'transaction_count': transaction_count,
            'penetration_pct': penetration_pct,
            'spend_share': spend_share
        })
    
    if len(non_bank_data) > 0:
        non_bank_df = pd.DataFrame(non_bank_data).sort_values('total_spend', ascending=False)
        
        # Format for display
        display_df = non_bank_df.copy()
        display_df['category'] = display_df['category'].str.replace('_', ' ').str.title()
        display_df['total_spend'] = display_df['total_spend'].apply(lambda x: f"${x:,.0f}")
        display_df['unique_accounts'] = display_df['unique_accounts'].apply(lambda x: f"{x:,}")
        display_df['transaction_count'] = display_df['transaction_count'].apply(lambda x: f"{x:,}")
        display_df['penetration_pct'] = display_df['penetration_pct'].apply(lambda x: f"{x:.2f}%")
        display_df['spend_share'] = display_df['spend_share'].apply(lambda x: f"{x:.2f}%")
        
        display_df.columns = [
            'Service', 'Type', 'Total Spend', 'Accounts', 
            'Transactions', 'Account Penetration', '% of Total Spend'
        ]
        
        print("\nServices Replacing Traditional Banking Functions:\n")
        display(display_df.style.hide(axis='index'))
        
        # Summary stats
        total_non_bank_spend = non_bank_df['total_spend'].sum()
        total_non_bank_accounts = non_bank_df['unique_accounts'].sum()
        
        print(f"\n💡 KEY INSIGHTS:")
        print(f"   • Combined non-bank spend: ${total_non_bank_spend:,.0f}")
        print(f"   • Total account relationships: {total_non_bank_accounts:,}")
        print(f"   • These services handle payments, transfers, and credit traditionally done by banks")
        print(f"   • High penetration = customers finding alternatives to traditional banking")
    else:
        print("\n⚠ No non-bank services found in dataset")

print("="*120)


# ---- ACCOUNT-LEVEL ANALYSIS ----

# Competitor Account Segmentation

# ===========================================================================
# COMPETITOR SPEND ANALYSIS - ACCOUNT SEGMENTATION
# ===========================================================================
"""
## Creates competitor_spend_analysis dictionary for segmentation
Analyzes what % of each account's spend goes to each competitor
"""

print("\n" + "="*120)
print(" " * 40 + "ANALYZING COMPETITOR SPEND BY ACCOUNT")
print("="*120)

if len(all_competitor_data) == 0:
    print("\n⚠ No competitor data found - run M6A detection first!")
else:
    competitor_spend_analysis = {}
    
    # Get total spend per account (for percentage calculations)
    account_totals = combined_df.groupby('primary_account_num')['amount'].sum()
    
    print(f"\nAnalyzing spend patterns for {len(all_competitor_data)} competitors...")
    
    for competitor, competitor_trans in all_competitor_data.items():
        # Get spend per account for this competitor
        competitor_spend_by_account = competitor_trans.groupby('primary_account_num')['amount'].sum()
        
        # Create comparison dataframe
        comparison = pd.DataFrame({
            'account': competitor_spend_by_account.index,
            'competitor_spend': competitor_spend_by_account.values
        })
        
        # Add total spend for each account
        comparison['total_spend'] = comparison['account'].map(account_totals)
        
        # Calculate percentage
        comparison['competitor_pct'] = (comparison['competitor_spend'] / comparison['total_spend'] * 100)
        
        # Segment accounts
        comparison['Segment'] = pd.cut(
            comparison['competitor_pct'],
            bins=[0, 25, 50, 100],
            labels=['CU-Focused', 'Balanced', 'Competitor-Heavy'],
            include_lowest=True
        )
        
        # Store in dictionary
        competitor_spend_analysis[competitor] = comparison
    
    print(f"✓ Analysis complete for {len(competitor_spend_analysis)} competitors")
    
    # Quick summary
    total_heavy = sum(len(df[df['Segment'] == 'Competitor-Heavy']) for df in competitor_spend_analysis.values())
    total_balanced = sum(len(df[df['Segment'] == 'Balanced']) for df in competitor_spend_analysis.values())
    total_cu = sum(len(df[df['Segment'] == 'CU-Focused']) for df in competitor_spend_analysis.values())
    
    print(f"\nOverall Segmentation:")
    print(f"  • Competitor-Heavy accounts: {total_heavy:,}")
    print(f"  • Balanced accounts: {total_balanced:,}")
    print(f"  • CU-Focused accounts: {total_cu:,}")

print("="*120)


# Competiton Segment SUmmary

# ===========================================================================
# TABLE: COMPETITOR SEGMENTATION SUMMARY
# ===========================================================================
"""
## Competitor Analysis - Segmentation Summary Table
"""

# Aggregate segmentation data
segment_summary = []

for competitor, comparison in competitor_spend_analysis.items():
    segment_counts = comparison['Segment'].value_counts()
    total = len(comparison)
    
    segment_summary.append({
        'Competitor': competitor,
        'Total Accounts': total,
        'Competitor-Heavy': segment_counts.get('Competitor-Heavy', 0),
        'Balanced': segment_counts.get('Balanced', 0),
        'CU-Focused': segment_counts.get('CU-Focused', 0),
        '% Heavy': f"{segment_counts.get('Competitor-Heavy', 0) / total * 100:.1f}%",
        '% Balanced': f"{segment_counts.get('Balanced', 0) / total * 100:.1f}%",
        '% CU-Focused': f"{segment_counts.get('CU-Focused', 0) / total * 100:.1f}%"
    })

summary_df = pd.DataFrame(segment_summary)
summary_df = summary_df.sort_values('Total Accounts', ascending=False)

print("\n" + "="*120)
print(" " * 40 + "COMPETITOR SEGMENTATION SUMMARY")
print("="*120)

# Format for display
display_df = summary_df.copy()
display_df['Total Accounts'] = display_df['Total Accounts'].apply(lambda x: f"{x:,}")
display_df['Competitor-Heavy'] = display_df['Competitor-Heavy'].apply(lambda x: f"{x:,}")
display_df['Balanced'] = display_df['Balanced'].apply(lambda x: f"{x:,}")
display_df['CU-Focused'] = display_df['CU-Focused'].apply(lambda x: f"{x:,}")

display(display_df.style.hide(axis='index'))

print("\n📊 Segment Definitions:")
print("  • Competitor-Heavy: >50% of their spend goes to this competitor")
print("  • Balanced: 25-50% of their spend goes to this competitor")
print("  • CU-Focused: <25% of their spend goes to this competitor (mostly using your CU)")

print("\n💡 High 'Competitor-Heavy' % = More accounts at risk of leaving")
print("="*120)


# Viz - Top 15 Competitor Segmentation

# ===========================================================================
# VISUALIZATION: COMPETITOR SEGMENTATION SUMMARY
# ===========================================================================
"""
## Competitor Analysis - Segmentation Overview (All Competitors)
"""


# Aggregate segmentation data across all competitors
segment_summary = []

for competitor, comparison in competitor_spend_analysis.items():
    segment_counts = comparison['Segment'].value_counts()
    total = len(comparison)
    
    segment_summary.append({
        'competitor': competitor,
        'total_accounts': total,
        'competitor_heavy': segment_counts.get('Competitor-Heavy', 0),
        'balanced': segment_counts.get('Balanced', 0),
        'cu_focused': segment_counts.get('CU-Focused', 0)
    })

summary_df = pd.DataFrame(segment_summary)

# Calculate percentages
summary_df['heavy_pct'] = (summary_df['competitor_heavy'] / summary_df['total_accounts'] * 100)
summary_df['balanced_pct'] = (summary_df['balanced'] / summary_df['total_accounts'] * 100)
summary_df['cu_focused_pct'] = (summary_df['cu_focused'] / summary_df['total_accounts'] * 100)

# Sort by total accounts (show biggest threats first)
summary_df = summary_df.sort_values('total_accounts', ascending=False).head(15)

# Create stacked bar chart
fig, ax = plt.subplots(figsize=(14, 10))

y_pos = range(len(summary_df))
competitors = summary_df['competitor'].values

# Create stacked bars
p1 = ax.barh(y_pos, summary_df['heavy_pct'], 
             color='#FF6B6B', label='Competitor-Heavy', height=0.7)
p2 = ax.barh(y_pos, summary_df['balanced_pct'], 
             left=summary_df['heavy_pct'],
             color='#FFA500', label='Balanced', height=0.7)
p3 = ax.barh(y_pos, summary_df['cu_focused_pct'], 
             left=summary_df['heavy_pct'] + summary_df['balanced_pct'],
             color='#4ECDC4', label='CU-Focused', height=0.7)

# Customize
ax.set_yticks(y_pos)
ax.set_yticklabels(competitors)
ax.set_xlabel('Percentage of Accounts (%)', fontsize=12, fontweight='bold')
ax.set_title('Competitor Account Segmentation - Top 15 by Total Accounts', 
             fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='lower right', fontsize=10)
ax.set_xlim(0, 100)

# Add grid
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Add account counts as text on the right
for i, (idx, row) in enumerate(summary_df.iterrows()):
    ax.text(102, i, f"{int(row['total_accounts']):,}", 
            va='center', fontsize=9, fontweight='bold')

# Add column header for account counts
ax.text(102, len(summary_df), 'Accounts', 
        va='center', fontsize=9, fontweight='bold', style='italic')

plt.tight_layout()
plt.show()

print("\n📊 Segmentation Summary:")
print("="*80)
print(f"Total Competitors Analyzed: {len(competitor_spend_analysis)}")
print(f"Showing Top 15 by Account Count")
print("\nSegment Definitions:")
print("  🔴 Competitor-Heavy: >50% of spend goes to competitor")
print("  🟠 Balanced: 25-50% of spend goes to competitor")
print("  🔵 CU-Focused: <25% of spend goes to competitor")
print("="*80)


# Viz - Competiton Segmentation

# ===========================================================================
# VISUALIZATION: COMPETITOR SEGMENTATION BY CATEGORY
# ===========================================================================
"""
## Competitor Analysis - Segmentation by Category (Separate Charts)
"""

import matplotlib.pyplot as plt
import pandas as pd

# Group competitors by category
category_groups = {}

for competitor, comparison in competitor_spend_analysis.items():
    # Get category from the competitor data
    category = all_competitor_data[competitor]['competitor_category'].iloc[0]
    
    if category not in category_groups:
        category_groups[category] = []
    
    segment_counts = comparison['Segment'].value_counts()
    total = len(comparison)
    
    category_groups[category].append({
        'competitor': competitor,
        'total_accounts': total,
        'competitor_heavy': segment_counts.get('Competitor-Heavy', 0),
        'balanced': segment_counts.get('Balanced', 0),
        'cu_focused': segment_counts.get('CU-Focused', 0),
        'heavy_pct': segment_counts.get('Competitor-Heavy', 0) / total * 100,
        'balanced_pct': segment_counts.get('Balanced', 0) / total * 100,
        'cu_focused_pct': segment_counts.get('CU-Focused', 0) / total * 100
    })

# Create one chart per category
for category, competitors in category_groups.items():
    # Convert to DataFrame and sort by total accounts (descending)
    cat_df = pd.DataFrame(competitors)
    cat_df = cat_df.sort_values('total_accounts', ascending=True)  # Ascending for horizontal bars
    
    # Skip if no data
    if len(cat_df) == 0:
        continue
    
    # Take top 15 if more than 15
    if len(cat_df) > 15:
        cat_df = cat_df.tail(15)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, max(8, len(cat_df) * 0.5)))
    
    y_pos = range(len(cat_df))
    competitors = cat_df['competitor'].values
    
    # Create stacked bars
    p1 = ax.barh(y_pos, cat_df['heavy_pct'], 
                 color='#FF6B6B', label='Competitor-Heavy (>50%)', height=0.7)
    p2 = ax.barh(y_pos, cat_df['balanced_pct'], 
                 left=cat_df['heavy_pct'],
                 color='#FFA500', label='Balanced (25-50%)', height=0.7)
    p3 = ax.barh(y_pos, cat_df['cu_focused_pct'], 
                 left=cat_df['heavy_pct'] + cat_df['balanced_pct'],
                 color='#4ECDC4', label='CU-Focused (<25%)', height=0.7)
    
    # Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(competitors, fontsize=10)
    ax.set_xlabel('Percentage of Accounts (%)', fontsize=12, fontweight='bold')
    
    # Format category name for title
    category_title = category.replace('_', ' ').title()
    ax.set_title(f'{category_title} - Account Segmentation (Top {len(cat_df)} by Total Accounts)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.legend(loc='lower right', fontsize=9)
    ax.set_xlim(0, 100)
    
    # Add grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Add account counts as text on the right
    for i, (idx, row) in enumerate(cat_df.iterrows()):
        ax.text(102, i, f"{int(row['total_accounts']):,}", 
                va='center', fontsize=9, fontweight='bold')
    
    # Add column header for account counts
    ax.text(102, len(cat_df), 'Accounts', 
            va='center', fontsize=9, fontweight='bold', style='italic')
    
    plt.tight_layout()
    plt.show()
    
    # Print summary for this category
    print(f"\n📊 {category_title} Summary:")
    print("="*80)
    print(f"  Total competitors: {len(cat_df)}")
    print(f"  Total accounts: {cat_df['total_accounts'].sum():,}")
    print(f"  Avg accounts per competitor: {cat_df['total_accounts'].mean():.0f}")
    
    # Calculate category-wide risk
    total_heavy = cat_df['competitor_heavy'].sum()
    total_balanced = cat_df['balanced'].sum()
    total_cu = cat_df['cu_focused'].sum()
    total_all = total_heavy + total_balanced + total_cu
    
    print(f"\n  Segmentation across category:")
    print(f"    🔴 Competitor-Heavy: {total_heavy:,} ({total_heavy/total_all*100:.1f}%)")
    print(f"    🟠 Balanced: {total_balanced:,} ({total_balanced/total_all*100:.1f}%)")
    print(f"    🔵 CU-Focused: {total_cu:,} ({total_cu/total_all*100:.1f}%)")
    print("="*80)

print("\n✓ Category-specific segmentation visualizations complete")


# Viz - Competitor Segmentation Heatmap

# ===========================================================================
# VISUALIZATION: COMPETITOR SEGMENTATION HEATMAP (IMPROVED COLORS)
# ===========================================================================
"""
## Competitor Analysis - Segmentation Heatmap with Column-Specific Colors
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Group competitors by category
category_groups = {}

for competitor, comparison in competitor_spend_analysis.items():
    category = all_competitor_data[competitor]['competitor_category'].iloc[0]
    
    if category not in category_groups:
        category_groups[category] = []
    
    segment_counts = comparison['Segment'].value_counts()
    total = len(comparison)
    
    category_groups[category].append({
        'competitor': competitor,
        'total_accounts': total,
        'heavy_pct': segment_counts.get('Competitor-Heavy', 0) / total * 100,
        'balanced_pct': segment_counts.get('Balanced', 0) / total * 100,
        'cu_focused_pct': segment_counts.get('CU-Focused', 0) / total * 100
    })

# Create improved heatmap per category
for category, competitors in category_groups.items():
    cat_df = pd.DataFrame(competitors)
    cat_df = cat_df.sort_values('total_accounts', ascending=False)
    
    if len(cat_df) < 3:
        continue
    
    if len(cat_df) > 20:
        cat_df = cat_df.head(20)
    
    competitor_names = cat_df['competitor'].values
    data_matrix = cat_df[['heavy_pct', 'balanced_pct', 'cu_focused_pct']].values
    
    # Create figure with custom coloring - WIDER
    fig, ax = plt.subplots(figsize=(16, max(10, len(cat_df) * 0.5)))
    
    # Function to get color based on column and value
    def get_cell_color(col_idx, value):
        """
        Column 0 (Competitor-Heavy): Red scale - High is BAD
        Column 1 (Balanced): Orange scale - Neutral
        Column 2 (CU-Focused): Green scale - High is GOOD
        """
        if col_idx == 0:  # Competitor-Heavy (low is good)
            if value >= 20:
                return '#8B0000'  # Dark red - Very bad
            elif value >= 10:
                return '#CD5C5C'  # Light red - Bad
            elif value >= 5:
                return '#FFB6C1'  # Pink - Slightly bad
            else:
                return '#F0F0F0'  # Light gray - Good
        
        elif col_idx == 1:  # Balanced (neutral)
            if value >= 30:
                return '#FF8C00'  # Dark orange
            elif value >= 20:
                return '#FFA500'  # Orange
            elif value >= 10:
                return '#FFD700'  # Light orange/yellow
            else:
                return '#F0F0F0'  # Light gray
        
        else:  # CU-Focused (high is good)
            if value >= 90:
                return '#006400'  # Dark green - Excellent
            elif value >= 80:
                return '#228B22'  # Green - Very good
            elif value >= 70:
                return '#90EE90'  # Light green - Good
            else:
                return '#F0F0F0'  # Light gray - Not good
    
    # Create colored grid manually - WIDER CELLS
    for i in range(len(competitor_names)):
        for j in range(3):
            color = get_cell_color(j, data_matrix[i, j])
            rect = mpatches.Rectangle((j*2-0.9, i-0.45), 1.8, 0.9, 
                                      facecolor=color, edgecolor='white', linewidth=3)
            ax.add_patch(rect)
            
            # Determine text color for readability
            if color in ['#8B0000', '#006400', '#228B22']:
                text_color = 'white'
            else:
                text_color = 'black'
            
            # Add percentage text - LARGER & BOLDER
            ax.text(j*2, i, f'{data_matrix[i, j]:.0f}%',
                   ha="center", va="center", color=text_color, 
                   fontweight='bold', fontsize=18)
    
    # Set limits and ticks - ADJUSTED FOR WIDER CELLS
    ax.set_xlim(-1, 5)
    ax.set_ylim(-0.5, len(competitor_names)-0.5)
    
    ax.set_xticks([0, 2, 4])
    ax.set_yticks(np.arange(len(competitor_names)))
    ax.set_xticklabels(['🔴 Competitor-Heavy\n(>50%)', 
                        '🟠 Balanced\n(25-50%)', 
                        '🟢 CU-Focused\n(<25%)'], fontsize=14, fontweight='bold')
    ax.set_yticklabels(competitor_names, fontsize=13, fontweight='bold')
    
    # Format category name
    category_title = category.replace('_', ' ').title()
    ax.set_title(f'{category_title} - Account Segmentation (Top {len(cat_df)} by Accounts)', 
                 fontsize=17, fontweight='bold', pad=20)
    
    # Add account counts on the right - MUCH LARGER
    for i, (idx, row) in enumerate(cat_df.iterrows()):
        ax.text(5.5, i, f"n={int(row['total_accounts']):,}", 
                va='center', fontsize=14, fontweight='bold')
    
    ax.invert_yaxis()  # Top to bottom
    
    plt.tight_layout()
    plt.show()
    
    # Print legend
    print(f"\n{category_title} - Color Guide:")
    print("="*80)
    print("🔴 Competitor-Heavy Column (% at high risk):")
    print("   • Dark Red (≥20%) = 🚨 Very Bad - Many accounts at risk")
    print("   • Light Red (10-19%) = ⚠️ Bad - Significant risk")
    print("   • Pink (5-9%) = 🟡 Slight concern")
    print("   • Gray (<5%) = ✅ Good - Few at risk")
    print("\n🟢 CU-Focused Column (% loyal to you):")
    print("   • Dark Green (≥90%) = 🎯 Excellent - Very loyal")
    print("   • Green (80-89%) = ✅ Very Good - Strong loyalty")
    print("   • Light Green (70-79%) = 👍 Good - Decent loyalty")
    print("   • Gray (<70%) = ⚠️ Concerning - Low loyalty")
    print("="*80 + "\n")

print("\n✓ Improved heatmaps complete - Colors now match risk levels!")


# Lists - Account Level Summaries

# ===========================================================================
# CELL 3: ACCOUNT-LEVEL SUMMARY
# ===========================================================================
"""
## Competitor Analysis - Account Level Detail
"""

all_account_summaries = {}

for competitor, competitor_trans in all_competitor_data.items():
    print(f"\n{'='*100}")
    print(f"ACCOUNT ANALYSIS: {competitor}")
    print(f"{'='*100}\n")
    
    # Create account-level summary
    account_summary = competitor_trans.groupby('primary_account_num').agg({
        'amount': ['sum', 'count', 'mean', 'min', 'max'],
        'transaction_date': ['min', 'max']
    }).round(2)
    
    account_summary.columns = [
        'Total Amount', 
        'Transaction Count', 
        'Avg Amount', 
        'Min Amount', 
        'Max Amount',
        'First Transaction',
        'Last Transaction'
    ]
    
    account_summary = account_summary.sort_values('Total Amount', ascending=False)
    
    # Add frequency metrics
    account_summary['Days Active'] = (
        account_summary['Last Transaction'] - account_summary['First Transaction']
    ).dt.days
    
    account_summary['Recency (Days)'] = (
        pd.Timestamp.now() - account_summary['Last Transaction']
    ).dt.days
    
    # Format for display
    display_summary = account_summary.head(25).copy()
    display_summary['Total Amount'] = display_summary['Total Amount'].apply(lambda x: f"${x:,.2f}")
    display_summary['Avg Amount'] = display_summary['Avg Amount'].apply(lambda x: f"${x:,.2f}")
    display_summary['Min Amount'] = display_summary['Min Amount'].apply(lambda x: f"${x:,.2f}")
    display_summary['Max Amount'] = display_summary['Max Amount'].apply(lambda x: f"${x:,.2f}")
    display_summary['First Transaction'] = display_summary['First Transaction'].dt.strftime('%Y-%m-%d')
    display_summary['Last Transaction'] = display_summary['Last Transaction'].dt.strftime('%Y-%m-%d')
    
    print(f"Top 25 Accounts by Total Spend:")
    display(display_summary)
    
    # Store for export (keep numeric for export)
    all_account_summaries[competitor] = account_summary
    
    # Segmentation table
    segmentation = pd.DataFrame({
        'Segment': [
            'High Value (>$1,000)',
            'Medium Value ($500-$1,000)',
            'Lower Value (<$500)',
            '',
            'Frequent Users (5+ transactions)',
            'Recent Activity (last 30 days)',
            'Recent Activity (last 90 days)'
        ],
        'Account Count': [
            len(account_summary[account_summary['Total Amount'] > 1000]),
            len(account_summary[(account_summary['Total Amount'] >= 500) & (account_summary['Total Amount'] <= 1000)]),
            len(account_summary[account_summary['Total Amount'] < 500]),
            '',
            len(account_summary[account_summary['Transaction Count'] >= 5]),
            len(account_summary[account_summary['Recency (Days)'] <= 30]),
            len(account_summary[account_summary['Recency (Days)'] <= 90])
        ]
    })
    
    print(f"\nAccount Segmentation:")
    display(segmentation)


# EXPORT DETAILED RESULTS

# ===========================================================================
# VISUALIZATION: COMPETITOR SEGMENTATION HEATMAP (IMPROVED COLORS)
# ===========================================================================
"""
## Competitor Analysis - Segmentation Heatmap with Column-Specific Colors
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Group competitors by category
category_groups = {}

for competitor, comparison in competitor_spend_analysis.items():
    category = all_competitor_data[competitor]['competitor_category'].iloc[0]
    
    if category not in category_groups:
        category_groups[category] = []
    
    segment_counts = comparison['Segment'].value_counts()
    total = len(comparison)
    
    category_groups[category].append({
        'competitor': competitor,
        'total_accounts': total,
        'heavy_pct': segment_counts.get('Competitor-Heavy', 0) / total * 100,
        'balanced_pct': segment_counts.get('Balanced', 0) / total * 100,
        'cu_focused_pct': segment_counts.get('CU-Focused', 0) / total * 100
    })

# Create improved heatmap per category
for category, competitors in category_groups.items():
    cat_df = pd.DataFrame(competitors)
    cat_df = cat_df.sort_values('total_accounts', ascending=False)
    
    if len(cat_df) < 3:
        continue
    
    if len(cat_df) > 20:
        cat_df = cat_df.head(20)
    
    competitor_names = cat_df['competitor'].values
    data_matrix = cat_df[['heavy_pct', 'balanced_pct', 'cu_focused_pct']].values
    
    # Create figure with custom coloring - WIDER
    fig, ax = plt.subplots(figsize=(16, max(10, len(cat_df) * 0.5)))
    
    # Function to get color based on column and value
    def get_cell_color(col_idx, value):
        """
        Column 0 (Competitor-Heavy): Red scale - High is BAD
        Column 1 (Balanced): Orange scale - Neutral
        Column 2 (CU-Focused): Green scale - High is GOOD
        """
        if col_idx == 0:  # Competitor-Heavy (low is good)
            if value >= 20:
                return '#8B0000'  # Dark red - Very bad
            elif value >= 10:
                return '#CD5C5C'  # Light red - Bad
            elif value >= 5:
                return '#FFB6C1'  # Pink - Slightly bad
            else:
                return '#F0F0F0'  # Light gray - Good
        
        elif col_idx == 1:  # Balanced (neutral)
            if value >= 30:
                return '#FF8C00'  # Dark orange
            elif value >= 20:
                return '#FFA500'  # Orange
            elif value >= 10:
                return '#FFD700'  # Light orange/yellow
            else:
                return '#F0F0F0'  # Light gray
        
        else:  # CU-Focused (high is good)
            if value >= 90:
                return '#006400'  # Dark green - Excellent
            elif value >= 80:
                return '#228B22'  # Green - Very good
            elif value >= 70:
                return '#90EE90'  # Light green - Good
            else:
                return '#F0F0F0'  # Light gray - Not good
    
    # Create colored grid manually - WIDER CELLS
    for i in range(len(competitor_names)):
        for j in range(3):
            color = get_cell_color(j, data_matrix[i, j])
            rect = mpatches.Rectangle((j*2-0.9, i-0.45), 1.8, 0.9, 
                                      facecolor=color, edgecolor='white', linewidth=3)
            ax.add_patch(rect)
            
            # Determine text color for readability
            if color in ['#8B0000', '#006400', '#228B22']:
                text_color = 'white'
            else:
                text_color = 'black'
            
            # Add percentage text
            ax.text(j*2, i, f'{data_matrix[i, j]:.0f}%',
                   ha="center", va="center", color=text_color, 
                   fontweight='bold', fontsize=14)
    
    # Set limits and ticks - ADJUSTED FOR WIDER CELLS
    ax.set_xlim(-1, 5)
    ax.set_ylim(-0.5, len(competitor_names)-0.5)
    
    ax.set_xticks([0, 2, 4])
    ax.set_yticks(np.arange(len(competitor_names)))
    ax.set_xticklabels(['🔴 Competitor-Heavy\n(>50%)', 
                        '🟠 Balanced\n(25-50%)', 
                        '🟢 CU-Focused\n(<25%)'], fontsize=12, fontweight='bold')
    ax.set_yticklabels(competitor_names, fontsize=11)
    
    # Format category name
    category_title = category.replace('_', ' ').title()
    ax.set_title(f'{category_title} - Account Segmentation (Top {len(cat_df)} by Accounts)', 
                 fontsize=15, fontweight='bold', pad=20)
    
    # Add account counts on the right
    for i, (idx, row) in enumerate(cat_df.iterrows()):
        ax.text(5.5, i, f"n={int(row['total_accounts']):,}", 
                va='center', fontsize=10, fontweight='bold')
    
    ax.invert_yaxis()  # Top to bottom
    
    plt.tight_layout()
    plt.show()
    
    # Print legend
    print(f"\n{category_title} - Color Guide:")
    print("="*80)
    print("🔴 Competitor-Heavy Column (% at high risk):")
    print("   • Dark Red (≥20%) = 🚨 Very Bad - Many accounts at risk")
    print("   • Light Red (10-19%) = ⚠️ Bad - Significant risk")
    print("   • Pink (5-9%) = 🟡 Slight concern")
    print("   • Gray (<5%) = ✅ Good - Few at risk")
    print("\n🟢 CU-Focused Column (% loyal to you):")
    print("   • Dark Green (≥90%) = 🎯 Excellent - Very loyal")
    print("   • Green (80-89%) = ✅ Very Good - Strong loyalty")
    print("   • Light Green (70-79%) = 👍 Good - Decent loyalty")
    print("   • Gray (<70%) = ⚠️ Concerning - Low loyalty")
    print("="*80 + "\n")

print("\n✓ Improved heatmaps complete - Colors now match risk levels!")


# ===========================================================================
# CELL 4: EXPORT RESULTS
# ===========================================================================
"""
## Competitor Analysis - Export to CSV
"""

# Create output directory if needed
output_dir = BASE_PATH / "Analysis Outputs" / f"{CLIENT_ID} - {CLIENT_NAME}" / "Competitor Analysis"
output_dir.mkdir(parents=True, exist_ok=True)

export_summary = []

for competitor in all_account_summaries.keys():
    competitor_clean = competitor.replace(' ', '_').replace('/', '_')
    
    # Export 1: Account Summary
    account_summary = all_account_summaries[competitor]
    output_file_summary = output_dir / f"Competitor_{competitor_clean}_Account_Summary.csv"
    account_summary.to_csv(output_file_summary)
    export_summary.append(['Account Summary', output_file_summary.name, len(account_summary)])
    
    # Export 2: Transaction Detail
    competitor_trans = all_competitor_data[competitor]
    competitor_trans_export = competitor_trans[[
        'primary_account_num',
        'transaction_date',
        'merchant_name',
        'amount',
        'source_file'
    ]].sort_values(['primary_account_num', 'transaction_date'])
    
    output_file_detail = output_dir / f"Competitor_{competitor_clean}_Transaction_Detail.csv"
    competitor_trans_export.to_csv(output_file_detail, index=False)
    export_summary.append(['Transaction Detail', output_file_detail.name, len(competitor_trans_export)])
    
    # Export 3: Marketing List (Priority Accounts)
    marketing_list = pd.DataFrame({
        'Account_Number': account_summary.index,
        'Transaction_Count': account_summary['Transaction Count'].astype(int),
        'Total_Spend': account_summary['Total Amount'].round(2),
        'Avg_Transaction': account_summary['Avg Amount'].round(2),
        'Last_Transaction_Date': account_summary['Last Transaction'].dt.strftime('%Y-%m-%d'),
        'Recency_Days': account_summary['Recency (Days)'].astype(int),
        'First_Transaction_Date': account_summary['First Transaction'].dt.strftime('%Y-%m-%d'),
        'Days_Active': account_summary['Days Active'].astype(int)
    })
    
    output_file_list = output_dir / f"Competitor_{competitor_clean}_Marketing_List.csv"
    marketing_list.to_csv(output_file_list, index=False)
    export_summary.append(['Marketing List', output_file_list.name, len(marketing_list)])

# Display export summary
export_df = pd.DataFrame(export_summary, columns=['File Type', 'Filename', 'Row Count'])
print(f"\n✓ All exports complete!")
print(f"Files saved to: {output_dir}\n")
display(export_df)


# Viz: Top Accounts

# ===========================================================================
# CELL 5: VISUALIZATION - Top Accounts
# ===========================================================================
"""
## Competitor Analysis - Top 20 Accounts Chart
"""

for competitor, account_summary in all_account_summaries.items():
    fig, ax = plt.subplots(figsize=(12, 8))
    
    top_20 = account_summary.head(20).sort_values('Total Amount')
    
    bars = ax.barh(range(len(top_20)), top_20['Total Amount'], color='#FF6B6B')
    ax.set_yticks(range(len(top_20)))
    ax.set_yticklabels([f"Account {i+1}" for i in range(len(top_20))])
    ax.set_xlabel('Total Spend ($)', fontsize=12)
    ax.set_title(f'Top 20 Accounts by Spend - {competitor}', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top_20['Total Amount'])):
        ax.text(val, bar.get_y() + bar.get_height()/2, 
                f' ${val:,.0f}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.show()


# VIz: Transaction Count Distribution

# ===========================================================================
# CELL 6: VISUALIZATION - Transaction Count Distribution
# ===========================================================================
"""
## Competitor Analysis - Transaction Count Distribution
"""

for competitor, account_summary in all_account_summaries.items():
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.hist(account_summary['Transaction Count'], bins=30, color='#4ECDC4', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Number of Transactions per Account', fontsize=12)
    ax.set_ylabel('Number of Accounts', fontsize=12)
    ax.set_title(f'Transaction Count Distribution - {competitor}', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add summary stats
    mean_trans = account_summary['Transaction Count'].mean()
    median_trans = account_summary['Transaction Count'].median()
    ax.axvline(mean_trans, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_trans:.1f}')
    ax.axvline(median_trans, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_trans:.1f}')
    ax.legend()
    
    plt.tight_layout()
    plt.show()


# Viz: Recency Analysis

# ===========================================================================
# CELL 7: VISUALIZATION - Recency Analysis
# ===========================================================================
"""
## Competitor Analysis - Recency Distribution
"""

for competitor, account_summary in all_account_summaries.items():
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.hist(account_summary['Recency (Days)'], bins=30, color='#FFA500', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Days Since Last Transaction', fontsize=12)
    ax.set_ylabel('Number of Accounts', fontsize=12)
    ax.set_title(f'Recency Distribution - {competitor}', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add reference lines
    ax.axvline(30, color='red', linestyle='--', linewidth=2, label='30 days')
    ax.axvline(90, color='darkred', linestyle='--', linewidth=2, label='90 days')
    ax.axvline(180, color='purple', linestyle='--', linewidth=2, label='180 days')
    ax.legend()
    
    # Add stats annotation
    recent_30 = len(account_summary[account_summary['Recency (Days)'] <= 30])
    recent_90 = len(account_summary[account_summary['Recency (Days)'] <= 90])
    total = len(account_summary)
    
    stats_text = f'Last 30 days: {recent_30:,} ({recent_30/total*100:.1f}%)\nLast 90 days: {recent_90:,} ({recent_90/total*100:.1f}%)'
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, 
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.show()


# VIz: Spend vs Frequency

# ===========================================================================
# CELL 8: VISUALIZATION - Spend vs Frequency
# ===========================================================================
"""
## Competitor Analysis - Spend vs Transaction Frequency
"""

for competitor, account_summary in all_account_summaries.items():
    fig, ax = plt.subplots(figsize=(12, 6))
    
    scatter = ax.scatter(account_summary['Transaction Count'], 
                        account_summary['Total Amount'], 
                        alpha=0.6, 
                        c=account_summary['Recency (Days)'],
                        cmap='RdYlGn_r',
                        s=100,
                        edgecolors='black',
                        linewidth=0.5)
    
    ax.set_xlabel('Transaction Count', fontsize=12)
    ax.set_ylabel('Total Spend ($)', fontsize=12)
    ax.set_title(f'Spend vs Transaction Frequency - {competitor}', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Days Since Last Transaction', rotation=270, labelpad=20)
    
    # Identify high-value quadrants
    median_count = account_summary['Transaction Count'].median()
    median_spend = account_summary['Total Amount'].median()
    
    ax.axvline(median_count, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(median_spend, color='gray', linestyle='--', alpha=0.5)
    
    # Add quadrant labels
    ax.text(0.75, 0.95, 'High Value\nFrequent', transform=ax.transAxes, 
            ha='center', va='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    ax.text(0.25, 0.95, 'High Value\nInfrequent', transform=ax.transAxes, 
            ha='center', va='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    
    plt.tight_layout()
    plt.show()


# Total Spend vs Competitor Spend

# ===========================================================================
# CELL 9: TOTAL SPEND vs COMPETITOR SPEND ANALYSIS
# ===========================================================================
"""
## Competitor Analysis - Total Spend vs Competitor Spend
"""

competitor_spend_analysis = {}

for competitor, competitor_trans in all_competitor_data.items():
    print(f"\n{'='*100}")
    print(f"SPEND ANALYSIS: {competitor}")
    print(f"{'='*100}\n")
    
    # Get list of accounts with competitor transactions
    competitor_accounts = competitor_trans['primary_account_num'].unique()
    
    # Get ALL transactions for these accounts
    all_spend_for_accounts = combined_df[
        combined_df['primary_account_num'].isin(competitor_accounts)
    ].copy()
    
    # Calculate total spend by account
    total_spend_summary = all_spend_for_accounts.groupby('primary_account_num').agg({
        'amount': ['sum', 'count'],
        'transaction_date': ['min', 'max']
    }).round(2)
    
    total_spend_summary.columns = ['total_spend', 'total_transactions', 'first_date', 'last_date']
    
    # Get competitor spend by account (from our earlier analysis)
    account_summary = all_account_summaries[competitor]
    
    # Merge to compare
    comparison = pd.DataFrame({
        'Total_Spend': total_spend_summary['total_spend'],
        'Total_Transactions': total_spend_summary['total_transactions'],
        'Competitor_Spend': account_summary['Total Amount'],
        'Competitor_Transactions': account_summary['Transaction Count']
    })
    
    # Calculate other (non-competitor) spend
    comparison['Other_Spend'] = comparison['Total_Spend'] - comparison['Competitor_Spend']
    comparison['Other_Transactions'] = comparison['Total_Transactions'] - comparison['Competitor_Transactions']
    
    # Calculate percentages
    comparison['Competitor_Pct'] = (comparison['Competitor_Spend'] / comparison['Total_Spend'] * 100).round(1)
    comparison['Other_Pct'] = (comparison['Other_Spend'] / comparison['Total_Spend'] * 100).round(1)
    
    # Sort by total spend
    comparison = comparison.sort_values('Total_Spend', ascending=False)
    
    # Create segments
    comparison['Segment'] = 'Mixed'
    comparison.loc[comparison['Competitor_Pct'] >= 80, 'Segment'] = 'Competitor-Heavy (80%+)'
    comparison.loc[comparison['Competitor_Pct'] < 20, 'Segment'] = 'Minimal Competitor (<20%)'
    comparison.loc[(comparison['Competitor_Pct'] >= 20) & (comparison['Competitor_Pct'] < 80), 'Segment'] = 'Mixed (20-80%)'
    
    # Display top 25
    display_comparison = comparison.head(25).copy()
    display_comparison['Total_Spend'] = display_comparison['Total_Spend'].apply(lambda x: f"${x:,.2f}")
    display_comparison['Competitor_Spend'] = display_comparison['Competitor_Spend'].apply(lambda x: f"${x:,.2f}")
    display_comparison['Other_Spend'] = display_comparison['Other_Spend'].apply(lambda x: f"${x:,.2f}")
    display_comparison['Competitor_Pct'] = display_comparison['Competitor_Pct'].apply(lambda x: f"{x:.1f}%")
    display_comparison['Other_Pct'] = display_comparison['Other_Pct'].apply(lambda x: f"{x:.1f}%")
    
    print("Top 25 Accounts - Total vs Competitor Spend:")
    display(display_comparison[['Total_Spend', 'Total_Transactions', 'Competitor_Spend', 
                                'Competitor_Transactions', 'Other_Spend', 'Other_Transactions', 
                                'Competitor_Pct', 'Segment']])
    
    # Segment summary
    segment_summary = comparison.groupby('Segment').agg({
        'Total_Spend': ['count', 'sum', 'mean'],
        'Competitor_Spend': ['sum', 'mean'],
        'Other_Spend': ['sum', 'mean']
    }).round(2)
    
    segment_summary.columns = ['Account_Count', 'Total_Spend_Sum', 'Total_Spend_Avg',
                               'Competitor_Spend_Sum', 'Competitor_Spend_Avg',
                               'Other_Spend_Sum', 'Other_Spend_Avg']
    
    segment_summary = segment_summary.reset_index()
    
    # Format for display
    display_segments = segment_summary.copy()
    for col in ['Total_Spend_Sum', 'Total_Spend_Avg', 'Competitor_Spend_Sum', 
                'Competitor_Spend_Avg', 'Other_Spend_Sum', 'Other_Spend_Avg']:
        display_segments[col] = display_segments[col].apply(lambda x: f"${x:,.2f}")
    
    print(f"\nSegment Summary:")
    display(display_segments)
    
    # Key insights
    competitor_heavy = len(comparison[comparison['Competitor_Pct'] >= 80])
    minimal_competitor = len(comparison[comparison['Competitor_Pct'] < 20])
    total_accounts = len(comparison)
    
    insights = pd.DataFrame({
        'Insight': [
            'Total Accounts Analyzed',
            'Competitor-Heavy (80%+ at competitor)',
            'Minimal Competitor (<20% at competitor)',
            'Mixed Spending (20-80%)',
            '',
            'AT RISK: High competitor spend',
            'OPPORTUNITY: Low competitor spend'
        ],
        'Value': [
            f"{total_accounts:,}",
            f"{competitor_heavy:,} ({competitor_heavy/total_accounts*100:.1f}%)",
            f"{minimal_competitor:,} ({minimal_competitor/total_accounts*100:.1f}%)",
            f"{len(comparison[(comparison['Competitor_Pct'] >= 20) & (comparison['Competitor_Pct'] < 80)]):,}",
            '',
            f"{competitor_heavy:,} accounts to retain",
            f"{minimal_competitor:,} accounts to grow"
        ]
    })
    
    print(f"\nKey Insights:")
    display(insights)
    
    # Store for export and visualization
    competitor_spend_analysis[competitor] = comparison


# Viz - Competitor Spend vs All

# ===========================================================================
# CELL 10: VISUALIZATION - Competitor vs Other Spend
# ===========================================================================
"""
## Competitor Analysis - Spend Comparison Chart
"""

for competitor, comparison in competitor_spend_analysis.items():
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Get top 20 by total spend
    top_20 = comparison.head(20).sort_values('Total_Spend')
    
    # Create stacked bar chart
    bars1 = ax.barh(range(len(top_20)), top_20['Other_Spend'], 
                    label='Other Spend', color='#4ECDC4')
    bars2 = ax.barh(range(len(top_20)), top_20['Competitor_Spend'], 
                    left=top_20['Other_Spend'], label='Competitor Spend', color='#FF6B6B')
    
    ax.set_yticks(range(len(top_20)))
    ax.set_yticklabels([f"Account {i+1}" for i in range(len(top_20))])
    ax.set_xlabel('Total Spend ($)', fontsize=12)
    ax.set_title(f'Top 20 Accounts: Competitor vs Other Spend - {competitor}', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    
    # Add total value labels
    for i, (idx, row) in enumerate(top_20.iterrows()):
        total = row['Total_Spend']
        comp_pct = row['Competitor_Pct']
        ax.text(total, i, f' ${total:,.0f} ({comp_pct:.0f}%)', 
                va='center', fontsize=9)
    
    plt.tight_layout()
    plt.show()


# Viz - Competitor Segment Distribution

# ===========================================================================
# CELL 11: VISUALIZATION - Segment Distribution
# ===========================================================================
"""
## Competitor Analysis - Account Segment Pie Chart
"""

for competitor, comparison in competitor_spend_analysis.items():
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Count by segment
    segment_counts = comparison['Segment'].value_counts()
    
    colors = ['#FF6B6B', '#FFA500', '#4ECDC4']
    explode = [0.1 if i == 0 else 0 for i in range(len(segment_counts))]    
    
    wedges, texts, autotexts = ax.pie(segment_counts.values, 
                                       labels=segment_counts.index,
                                       autopct='%1.1f%%',
                                       colors=colors,
                                       explode=explode,
                                       startangle=90,
                                       textprops={'fontsize': 12})
    
    # Bold the percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)
    
    ax.set_title(f'Account Segmentation by Competitor Spend % - {competitor}', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add legend with counts
    legend_labels = [f"{label}: {count:,} accounts" 
                    for label, count in zip(segment_counts.index, segment_counts.values)]
    ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    plt.show()


# VIz - Competitor Heavy Spend

for competitor, comparison in competitor_spend_analysis.items():
    print(f"{competitor}: {comparison.columns.tolist()}")
    break


# ===========================================================================
# CELL 10A: VISUALIZATION - AT RISK Accounts (Competitor-Heavy)
# ===========================================================================
"""
## Competitor Analysis - AT RISK Accounts (80%+ at Competitor)
"""

for competitor, comparison in competitor_spend_analysis.items():
    # The columns in competitor_spend_analysis are:
    # 'account', 'competitor_spend', 'total_spend', 'competitor_pct', 'Segment'
    
    # Filter to EXTREME RISK accounts only (80%+ at competitor)
    at_risk = comparison[comparison['Competitor_Pct'] >= 80].copy()
    
    if len(at_risk) == 0:
        continue  # Skip competitors with no extreme risk accounts
    
    # Sort by total spend to show biggest accounts first
    at_risk = at_risk.sort_values('total_spend', ascending=False)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Get top 20 AT RISK accounts by total spend
    top_20_risk = at_risk.head(20).sort_values('total_spend')
    
    # Calculate "your bank" spend (other spend)
    top_20_risk['your_bank_spend'] = top_20_risk['total_spend'] - top_20_risk['competitor_spend']
    
    # Create stacked bar chart
    bars1 = ax.barh(range(len(top_20_risk)), top_20_risk['your_bank_spend'], 
                    label='Your CU Spend', color='#4ECDC4')
    bars2 = ax.barh(range(len(top_20_risk)), top_20_risk['competitor_spend'], 
                    left=top_20_risk['your_bank_spend'], 
                    label=f'{competitor} Spend', color='#FF6B6B')
    
    ax.set_yticks(range(len(top_20_risk)))
    ax.set_yticklabels([f"Account {i+1}" for i in range(len(top_20_risk))], fontsize=11)
    ax.set_xlabel('Total Spend ($)', fontsize=13, fontweight='bold')
    ax.set_title(f'⚠️ Top 20 EXTREME RISK Accounts (80%+ at {competitor})', 
                 fontsize=15, fontweight='bold', color='#8B0000')
    ax.legend(loc='lower right', fontsize=11)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Add total value labels with competitor percentage
    for i, (idx, row) in enumerate(top_20_risk.iterrows()):
        total = row['total_spend']
        comp_pct = row['competitor_pct']
        ax.text(total + (total * 0.02), i, f'${total:,.0f} ({comp_pct:.0f}%)', 
                va='center', fontsize=10, fontweight='bold')
    
    # Add summary box
    total_at_risk = len(at_risk)
    total_at_risk_spend = at_risk['total_spend'].sum()
    total_competitor_spend = at_risk['competitor_spend'].sum()
    avg_pct = at_risk['competitor_pct'].mean()
    
    summary_text = f'🚨 EXTREME RISK ACCOUNTS (80%+ at {competitor})\n'
    summary_text += f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
    summary_text += f'Total Accounts: {total_at_risk:,}\n'
    summary_text += f'Total Spend: ${total_at_risk_spend:,.0f}\n'
    summary_text += f'Competitor Spend: ${total_competitor_spend:,.0f}\n'
    summary_text += f'Avg % at Competitor: {avg_pct:.1f}%\n'
    summary_text += f'Your CU Spend: ${total_at_risk_spend - total_competitor_spend:,.0f}'
    
    ax.text(0.02, 0.98, summary_text, transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='#FFE5E5', alpha=0.95, edgecolor='#8B0000', linewidth=2),
            fontsize=11, fontweight='bold', family='monospace')
    
    plt.tight_layout()
    plt.show()
    
    print(f"\n⚠️ {competitor}: {total_at_risk:,} accounts are EXTREME RISK (80%+ spend at competitor)")
    print(f"   Showing top 20 by total spend")
    print("-"*80)

print("\n✓ AT RISK visualization complete")


# Viz - Competitor Spend Scatter

# ===========================================================================
# M6C: BUILD COMPETITOR SPEND ANALYSIS FROM TAGGED DATA
# ===========================================================================
# Requires: combined_df with competitor_category and competitor_match columns
# ===========================================================================

TRUE_COMPETITORS = ['big_nationals', 'regionals', 'credit_unions', 'digital_banks']

# Get only true competitor transactions
comp_txns = combined_df[combined_df['competitor_category'].isin(TRUE_COMPETITORS)].copy()

# Build per-account total spend
account_total_spend = combined_df.groupby('primary_account_num')['amount'].sum().reset_index()
account_total_spend.columns = ['primary_account_num', 'total_spend']

# Build competitor_spend_analysis dict keyed by competitor_match
competitor_spend_analysis = {}

for comp_name, grp in comp_txns.groupby('competitor_match'):
    acct_comp = grp.groupby('primary_account_num')['amount'].sum().reset_index()
    acct_comp.columns = ['primary_account_num', 'competitor_spend']

    merged = acct_comp.merge(account_total_spend, on='primary_account_num', how='left')
    merged['competitor_pct'] = (merged['competitor_spend'] / merged['total_spend'] * 100).clip(0, 100)
    merged['your_cu_spend'] = merged['total_spend'] - merged['competitor_spend']

    # Segment
    merged['Segment'] = pd.cut(
        merged['competitor_pct'],
        bins=[0, 20, 50, 80, 100],
        labels=['Low Risk', 'Moderate', 'High Risk', 'Extreme Risk'],
        include_lowest=True
    )

    merged['competitor_name'] = comp_name
    merged['competitor_category'] = grp['competitor_category'].iloc[0]
    competitor_spend_analysis[comp_name] = merged

print(f"✓ Built competitor_spend_analysis for {len(competitor_spend_analysis)} competitors")
print(f"  Columns: {list(next(iter(competitor_spend_analysis.values())).columns)}")

# Quick summary
for comp, df in sorted(competitor_spend_analysis.items(),
                       key=lambda x: x[1]['competitor_spend'].sum(), reverse=True)[:10]:
    print(f"  • {comp:30s} {len(df):>5,} accounts  ${df['competitor_spend'].sum():>12,.0f}")


# ===========================================================================
# M6C-2: VISUALIZATION - AT RISK Accounts (80%+ at Competitor)
# ===========================================================================

# Only show for competitors with enough at-risk accounts to be meaningful
for competitor, comparison in competitor_spend_analysis.items():
    at_risk = comparison[comparison['competitor_pct'] >= 80].copy()

    if len(at_risk) == 0:
        continue

    at_risk = at_risk.sort_values('total_spend', ascending=False)

    fig, ax = plt.subplots(figsize=(14, min(10, max(4, len(at_risk.head(20)) * 0.5 + 2))))

    top_n = at_risk.head(20).sort_values('total_spend')
    n = len(top_n)

    # Stacked bars: CU spend + competitor spend
    bars1 = ax.barh(range(n), top_n['your_cu_spend'],
                    label='Your CU Spend', color='#4ECDC4',
                    edgecolor='black', linewidth=0.5)
    bars2 = ax.barh(range(n), top_n['competitor_spend'],
                    left=top_n['your_cu_spend'],
                    label=f'{competitor} Spend', color='#FF6B6B',
                    edgecolor='black', linewidth=0.5)

    ax.set_yticks(range(n))
    ax.set_yticklabels([f"Account {i+1}" for i in range(n)], fontsize=10)
    ax.set_xlabel('Total Spend ($)', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {n} EXTREME RISK Accounts (80%+ at {competitor})',
                 fontsize=14, fontweight='bold', color='#8B0000')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Value labels
    for i, (_, row) in enumerate(top_n.iterrows()):
        total = row['total_spend']
        pct = row['competitor_pct']
        ax.text(total + total * 0.02, i,
                f'${total:,.0f} ({pct:.0f}%)',
                va='center', fontsize=9, fontweight='bold')

    # Summary box
    total_at_risk = len(at_risk)
    total_at_risk_spend = at_risk['total_spend'].sum()
    total_competitor_spend = at_risk['competitor_spend'].sum()
    avg_pct = at_risk['competitor_pct'].mean()

    summary_text = (
        f'EXTREME RISK ACCOUNTS (80%+ at {competitor})\n'
        f'{"━" * 42}\n'
        f'Total Accounts: {total_at_risk:,}\n'
        f'Total Spend: ${total_at_risk_spend:,.0f}\n'
        f'Competitor Spend: ${total_competitor_spend:,.0f}\n'
        f'Avg % at Competitor: {avg_pct:.1f}%\n'
        f'Your CU Spend: ${total_at_risk_spend - total_competitor_spend:,.0f}'
    )

    ax.text(0.02, 0.98, summary_text, transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='#FFE5E5', alpha=0.95,
                      edgecolor='#8B0000', linewidth=2),
            fontsize=10, fontweight='bold', family='monospace')

    plt.tight_layout()
    plt.show()

    print(f"\n  {competitor}: {total_at_risk:,} extreme risk accounts (80%+ spend at competitor)")
    print("-" * 80)

print("\n✓ At-risk visualization complete")


# ===========================================================================
# M6C-3: VISUALIZATION - Spend Distribution Scatter
# ===========================================================================

for competitor, comparison in competitor_spend_analysis.items():
    if len(comparison) < 5:
        continue  # skip competitors with too few accounts for a meaningful scatter

    fig, ax = plt.subplots(figsize=(14, 10))

    scatter = ax.scatter(
        comparison['your_cu_spend'],
        comparison['competitor_spend'],
        s=120, alpha=0.7,
        c=comparison['competitor_pct'],
        cmap='RdYlGn_r',
        edgecolors='black', linewidth=0.8,
        vmin=0, vmax=100
    )

    ax.set_xlabel('Your CU Spend ($)', fontsize=14, fontweight='bold')
    ax.set_ylabel(f'{competitor} Spend ($)', fontsize=14, fontweight='bold')
    ax.set_title(f'Spend Distribution Analysis - {competitor}',
                 fontsize=16, fontweight='bold', pad=20)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('% of Spend at Competitor', rotation=270, labelpad=25,
                   fontsize=12, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)

    # 50/50 diagonal
    max_val = max(comparison['your_cu_spend'].max(), comparison['competitor_spend'].max())
    ax.plot([0, max_val], [0, max_val], 'r--', alpha=0.6, linewidth=3,
            label='50/50 Split Line')

    # Median reference lines
    median_cu = comparison['your_cu_spend'].median()
    median_comp = comparison['competitor_spend'].median()
    ax.axvline(median_cu, color='blue', linestyle=':', alpha=0.4, linewidth=2,
               label=f'Median CU Spend: ${median_cu:,.0f}')
    ax.axhline(median_comp, color='red', linestyle=':', alpha=0.4, linewidth=2,
               label=f'Median Competitor Spend: ${median_comp:,.0f}')

    # Quadrant labels
    ax.text(0.97, 0.97, 'HIGH RISK\n\nHigh Competitor\nLow Your CU\n\n(Losing them)',
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='#FF6B6B', alpha=0.9,
                      edgecolor='darkred', linewidth=2),
            fontweight='bold', fontsize=10)

    ax.text(0.03, 0.03, 'LOW VALUE\n\nLow Both\n\n(Small accounts)',
            transform=ax.transAxes, ha='left', va='bottom',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8,
                      edgecolor='gray', linewidth=2),
            fontsize=9)

    ax.text(0.97, 0.03, 'HIGH VALUE\n\nHigh Both\n\n(Big spenders)',
            transform=ax.transAxes, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8,
                      edgecolor='blue', linewidth=2),
            fontsize=9)

    ax.text(0.03, 0.97, 'WINNING\n\nLow Competitor\nHigh Your CU\n\n(Loyal & Active)',
            transform=ax.transAxes, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='#4ECDC4', alpha=0.9,
                      edgecolor='darkgreen', linewidth=2),
            fontweight='bold', fontsize=10)

    # Stats box
    total_accounts = len(comparison)
    avg_cu_spend = comparison['your_cu_spend'].mean()
    avg_comp_spend = comparison['competitor_spend'].mean()
    avg_comp_pct = comparison['competitor_pct'].mean()

    stats_text = (
        f'SUMMARY\n'
        f'{"━" * 22}\n'
        f'Accounts: {total_accounts:,}\n'
        f'Avg CU Spend: ${avg_cu_spend:,.0f}\n'
        f'Avg Competitor: ${avg_comp_spend:,.0f}\n'
        f'Avg % at Competitor: {avg_comp_pct:.1f}%'
    )

    ax.text(0.50, 0.97, stats_text, transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.95,
                      edgecolor='black', linewidth=2),
            fontsize=10, fontweight='bold', family='monospace')

    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    plt.tight_layout()
    plt.show()

    # Quadrant counts
    high_risk = len(comparison[(comparison['competitor_spend'] > median_comp) &
                               (comparison['your_cu_spend'] < median_cu)])
    winning = len(comparison[(comparison['competitor_spend'] < median_comp) &
                             (comparison['your_cu_spend'] > median_cu)])
    high_value = len(comparison[(comparison['competitor_spend'] > median_comp) &
                                (comparison['your_cu_spend'] > median_cu)])
    low_value = len(comparison[(comparison['competitor_spend'] < median_comp) &
                               (comparison['your_cu_spend'] < median_cu)])

    print(f"\n  {competitor} Scatter Analysis:")
    print(f"  {'─' * 60}")
    print(f"    High Risk:  {high_risk:>5,} accounts ({high_risk/total_accounts*100:5.1f}%)")
    print(f"    Winning:    {winning:>5,} accounts ({winning/total_accounts*100:5.1f}%)")
    print(f"    High Value: {high_value:>5,} accounts ({high_value/total_accounts*100:5.1f}%)")
    print(f"    Low Value:  {low_value:>5,} accounts ({low_value/total_accounts*100:5.1f}%)")
    print(f"  {'─' * 60}")

print("\n✓ Scatter plot analysis complete")


# ===========================================================================
# CELL 12: VISUALIZATION - Spend Distribution Scatter
# ===========================================================================
"""
## Competitor Analysis - Competitor vs Your CU Spend Scatter
"""

for competitor, comparison in competitor_spend_analysis.items():
    # Calculate "your bank" spend
    comparison['your_cu_spend'] = comparison['total_spend'] - comparison['competitor_spend']
    
    # Skip if no data
    if len(comparison) == 0:
        continue
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create scatter plot
    scatter = ax.scatter(comparison['your_cu_spend'], 
                        comparison['competitor_spend'],
                        s=120,
                        alpha=0.7,
                        c=comparison['competitor_pct'],
                        cmap='RdYlGn_r',
                        edgecolors='black',
                        linewidth=0.8,
                        vmin=0,
                        vmax=100)
    
    ax.set_xlabel('Your CU Spend ($)', fontsize=14, fontweight='bold')
    ax.set_ylabel(f'{competitor} Spend ($)', fontsize=14, fontweight='bold')
    ax.set_title(f'Spend Distribution Analysis - {competitor}', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('% of Spend at Competitor', rotation=270, labelpad=25, fontsize=12, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)
    
    # Add diagonal line (50/50 split)
    max_val = max(comparison['your_cu_spend'].max(), comparison['competitor_spend'].max())
    ax.plot([0, max_val], [0, max_val], 'r--', alpha=0.6, linewidth=3, label='50/50 Split Line')
    
    # Add reference lines (medians)
    median_cu = comparison['your_cu_spend'].median()
    median_comp = comparison['competitor_spend'].median()
    ax.axvline(median_cu, color='blue', linestyle=':', alpha=0.4, linewidth=2, label=f'Median CU Spend: ${median_cu:,.0f}')
    ax.axhline(median_comp, color='red', linestyle=':', alpha=0.4, linewidth=2, label=f'Median Competitor Spend: ${median_comp:,.0f}')
    
    # Add quadrant labels with better styling
    ax.text(0.97, 0.97, '🚨 HIGH RISK\n\nHigh Competitor\nLow Your CU\n\n(Losing them)', 
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='#FF6B6B', alpha=0.9, edgecolor='darkred', linewidth=2),
            fontweight='bold', fontsize=11)
    
    ax.text(0.03, 0.03, '📉 LOW VALUE\n\nLow Both\n\n(Small accounts)', 
            transform=ax.transAxes, ha='left', va='bottom',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8, edgecolor='gray', linewidth=2),
            fontsize=10)
    
    ax.text(0.97, 0.03, '💰 HIGH VALUE\n\nHigh Both\n\n(Big spenders)', 
            transform=ax.transAxes, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8, edgecolor='blue', linewidth=2),
            fontsize=10)
    
    ax.text(0.03, 0.97, '✅ WINNING\n\nLow Competitor\nHigh Your CU\n\n(Loyal & Active)', 
            transform=ax.transAxes, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='#4ECDC4', alpha=0.9, edgecolor='darkgreen', linewidth=2),
            fontweight='bold', fontsize=11)
    
    # Add statistics box
    total_accounts = len(comparison)
    avg_cu_spend = comparison['your_cu_spend'].mean()
    avg_comp_spend = comparison['competitor_spend'].mean()
    avg_comp_pct = comparison['competitor_pct'].mean()
    
    stats_text = f'📊 SUMMARY STATS\n'
    stats_text += f'━━━━━━━━━━━━━━━━━━━━\n'
    stats_text += f'Total Accounts: {total_accounts:,}\n'
    stats_text += f'Avg CU Spend: ${avg_cu_spend:,.0f}\n'
    stats_text += f'Avg Competitor: ${avg_comp_spend:,.0f}\n'
    stats_text += f'Avg % at Competitor: {avg_comp_pct:.1f}%'
    
    ax.text(0.50, 0.97, stats_text, transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='black', linewidth=2),
            fontsize=10, fontweight='bold', family='monospace')
    
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    plt.tight_layout()
    plt.show()
    
    # Print insights
    print(f"\n📊 {competitor} Scatter Analysis:")
    print("="*80)
    
    # Count accounts in each quadrant
    high_risk = len(comparison[(comparison['competitor_spend'] > median_comp) & 
                                (comparison['your_cu_spend'] < median_cu)])
    winning = len(comparison[(comparison['competitor_spend'] < median_comp) & 
                              (comparison['your_cu_spend'] > median_cu)])
    high_value = len(comparison[(comparison['competitor_spend'] > median_comp) & 
                                 (comparison['your_cu_spend'] > median_cu)])
    low_value = len(comparison[(comparison['competitor_spend'] < median_comp) & 
                                (comparison['your_cu_spend'] < median_cu)])
    
    print(f"  🚨 High Risk (top-right): {high_risk:,} accounts ({high_risk/total_accounts*100:.1f}%)")
    print(f"  ✅ Winning (top-left): {winning:,} accounts ({winning/total_accounts*100:.1f}%)")
    print(f"  💰 High Value (bottom-right): {high_value:,} accounts ({high_value/total_accounts*100:.1f}%)")
    print(f"  📉 Low Value (bottom-left): {low_value:,} accounts ({low_value/total_accounts*100:.1f}%)")
    print("="*80)

print("\n✓ Scatter plot analysis complete")


# ===========================================================================
# DEBUG: Check Category Spend Aggregation
# ===========================================================================

print("="*100)
print("DEBUGGING CATEGORY SPEND DATA")
print("="*100)

# Check a sample competitor
sample_competitor = list(competitor_spend_analysis.keys())[0]
sample_data = competitor_spend_analysis[sample_competitor]

print(f"\n📋 Sample Competitor: {sample_competitor}")
print(f"Columns in competitor_spend_analysis:")
print(list(sample_data.columns))
print(f"\nFirst 5 rows:")
print(sample_data.head())

print("\n" + "="*100)

# Check how many accounts per category
category_account_counts = {}

for competitor, comparison in competitor_spend_analysis.items():
    category = all_competitor_data[competitor]['competitor_category'].iloc[0]
    
    if category not in category_account_counts:
        category_account_counts[category] = {
            'accounts': set(),
            'competitors': []
        }
    
    # Add unique accounts
    category_account_counts[category]['accounts'].update(comparison['account'].values)
    category_account_counts[category]['competitors'].append(competitor)

print("\n📊 Accounts Per Category (UNIQUE):")
print("-"*100)
for category, data in category_account_counts.items():
    print(f"{category.replace('_', ' ').title()}")
    print(f"  • Unique accounts: {len(data['accounts']):,}")
    print(f"  • Competitors: {len(data['competitors'])}")
    print(f"  • Competitor names: {', '.join(data['competitors'][:5])}")
    if len(data['competitors']) > 5:
        print(f"    ... and {len(data['competitors']) - 5} more")
    print()

print("="*100)

# Check if an account appears in multiple competitors within same category
print("\n🔍 Checking for account overlap within categories...")

for category, data in category_account_counts.items():
    # Get all competitors in this category
    competitors_in_cat = data['competitors']
    
    if len(competitors_in_cat) <= 1:
        continue
    
    # Check if any account uses multiple competitors in this category
    account_competitor_map = {}
    
    for competitor in competitors_in_cat:
        comparison = competitor_spend_analysis[competitor]
        for account in comparison['account'].values:
            if account not in account_competitor_map:
                account_competitor_map[account] = []
            account_competitor_map[account].append(competitor)
    
    # Find accounts using multiple competitors in this category
    multi_competitor = {acc: comps for acc, comps in account_competitor_map.items() if len(comps) > 1}
    
    if len(multi_competitor) > 0:
        print(f"\n⚠️ {category.replace('_', ' ').title()}: {len(multi_competitor):,} accounts use MULTIPLE competitors in this category")
        print(f"   Example: Account {list(multi_competitor.keys())[0]} uses: {', '.join(multi_competitor[list(multi_competitor.keys())[0]])}")
    else:
        print(f"\n✓ {category.replace('_', ' ').title()}: No accounts use multiple competitors")

print("\n" + "="*100)


# ===========================================================================
# CELL 12: VISUALIZATION - Spend Distribution by Category (Aggregated)
# ===========================================================================
"""
## Competitor Analysis - Category-Level Spend Distribution
Shows one scatter plot per competitor category (not per competitor)
"""

import matplotlib.pyplot as plt
import numpy as np

# Group all competitor data by category
category_spend_data = {}

for competitor, comparison in competitor_spend_analysis.items():
    # Get category
    category = all_competitor_data[competitor]['competitor_category'].iloc[0]
    
    if category not in category_spend_data:
        category_spend_data[category] = []
    
    # Add each account's data with category tag
    for idx, row in comparison.iterrows():
        category_spend_data[category].append({
            'account': row['account'],
            'competitor_spend': row['competitor_spend'],
            'total_spend': row['total_spend'],
            'competitor_pct': row['competitor_pct'],
            'competitor_name': competitor
        })

# Create one scatter plot per category
for category, accounts in category_spend_data.items():
    cat_df = pd.DataFrame(accounts)
    
    # Skip small categories
    if len(cat_df) < 10:
        continue
    
    # Calculate your CU spend
    cat_df['your_cu_spend'] = cat_df['total_spend'] - cat_df['competitor_spend']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Create scatter plot
    scatter = ax.scatter(cat_df['your_cu_spend'], 
                        cat_df['competitor_spend'],
                        s=80,
                        alpha=0.6,
                        c=cat_df['competitor_pct'],
                        cmap='RdYlGn_r',
                        edgecolors='black',
                        linewidth=0.5,
                        vmin=0,
                        vmax=100)
    
    # Format category name
    category_title = category.replace('_', ' ').title()
    
    ax.set_xlabel('Your CU Spend ($)', fontsize=15, fontweight='bold')
    ax.set_ylabel(f'{category_title} Spend ($)', fontsize=15, fontweight='bold')
    ax.set_title(f'Spend Distribution - {category_title} Category', 
                 fontsize=18, fontweight='bold', pad=25)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('% of Spend at Competitor', rotation=270, labelpad=30, fontsize=13, fontweight='bold')
    cbar.ax.tick_params(labelsize=11)
    
    # Add diagonal line (50/50 split)
    max_val = max(cat_df['your_cu_spend'].max(), cat_df['competitor_spend'].max())
    if max_val > 0:
        ax.plot([0, max_val], [0, max_val], 'r--', alpha=0.6, linewidth=3, label='50/50 Split Line')
    
    # Add reference lines (medians)
    median_cu = cat_df['your_cu_spend'].median()
    median_comp = cat_df['competitor_spend'].median()
    ax.axvline(median_cu, color='blue', linestyle=':', alpha=0.4, linewidth=2.5)
    ax.axhline(median_comp, color='red', linestyle=':', alpha=0.4, linewidth=2.5)
    
    # Add quadrant labels
    ax.text(0.97, 0.97, '🚨 HIGH RISK\n\nHigh Competitor\nLow Your CU', 
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='#FF6B6B', alpha=0.9, edgecolor='darkred', linewidth=2),
            fontweight='bold', fontsize=12)
    
    ax.text(0.03, 0.03, '📉 LOW VALUE\n\nLow Both', 
            transform=ax.transAxes, ha='left', va='bottom',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8, edgecolor='gray', linewidth=2),
            fontsize=11)
    
    ax.text(0.97, 0.03, '💰 HIGH VALUE\n\nHigh Both', 
            transform=ax.transAxes, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8, edgecolor='blue', linewidth=2),
            fontsize=11)
    
    ax.text(0.03, 0.97, '✅ WINNING\n\nLow Competitor\nHigh Your CU', 
            transform=ax.transAxes, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='#4ECDC4', alpha=0.9, edgecolor='darkgreen', linewidth=2),
            fontweight='bold', fontsize=12)
    
    # Calculate statistics
    total_accounts = len(cat_df)
    unique_competitors = cat_df['competitor_name'].nunique()
    avg_cu_spend = cat_df['your_cu_spend'].mean()
    avg_comp_spend = cat_df['competitor_spend'].mean()
    avg_comp_pct = cat_df['competitor_pct'].mean()
    total_category_spend = cat_df['competitor_spend'].sum()
    
    # Stats box
    stats_text = f'📊 {category_title.upper()} SUMMARY\n'
    stats_text += f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
    stats_text += f'Total Accounts: {total_accounts:,}\n'
    stats_text += f'Competitors in Category: {unique_competitors}\n'
    stats_text += f'Avg CU Spend: ${avg_cu_spend:,.0f}\n'
    stats_text += f'Avg Competitor: ${avg_comp_spend:,.0f}\n'
    stats_text += f'Avg % at Competitor: {avg_comp_pct:.1f}%\n'
    stats_text += f'Total Category Spend: ${total_category_spend:,.0f}'
    
    ax.text(0.50, 0.97, stats_text, transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='black', linewidth=2.5),
            fontsize=11, fontweight='bold', family='monospace')
    
    plt.tight_layout()
    plt.show()
    
    # Print detailed quadrant analysis
    print(f"\n📊 {category_title} - Quadrant Analysis:")
    print("="*100)
    
    # Count accounts in each quadrant
    high_risk = len(cat_df[(cat_df['competitor_spend'] > median_comp) & 
                            (cat_df['your_cu_spend'] < median_cu)])
    winning = len(cat_df[(cat_df['competitor_spend'] < median_comp) & 
                          (cat_df['your_cu_spend'] > median_cu)])
    high_value = len(cat_df[(cat_df['competitor_spend'] > median_comp) & 
                             (cat_df['your_cu_spend'] > median_cu)])
    low_value = len(cat_df[(cat_df['competitor_spend'] < median_comp) & 
                            (cat_df['your_cu_spend'] < median_cu)])
    
    print(f"  🚨 High Risk (top-right):    {high_risk:,} accounts ({high_risk/total_accounts*100:.1f}%) - Using competitor MORE")
    print(f"  ✅ Winning (top-left):       {winning:,} accounts ({winning/total_accounts*100:.1f}%) - Loyal to your CU")
    print(f"  💰 High Value (bottom-right): {high_value:,} accounts ({high_value/total_accounts*100:.1f}%) - Big spenders everywhere")
    print(f"  📉 Low Value (bottom-left):   {low_value:,} accounts ({low_value/total_accounts*100:.1f}%) - Small/inactive accounts")
    
    print(f"\n  Top 5 Competitors in {category_title}:")
    top_5_in_category = cat_df.groupby('competitor_name')['competitor_spend'].sum().sort_values(ascending=False).head(5)
    for i, (comp, spend) in enumerate(top_5_in_category.items(), 1):
        print(f"    {i}. {comp}: ${spend:,.0f}")
    
    print("="*100)

print("\n✓ Category-level scatter plot analysis complete")
print("\n💡 Shows aggregated spend patterns across entire competitor categories")
print("   Much cleaner than 47 individual scatter plots!")


# Export Lists

# ===========================================================================
# CELL 13: EXPORT SPEND ANALYSIS
# ===========================================================================
"""
## Competitor Analysis - Export Spend Comparison
"""

for competitor, comparison in competitor_spend_analysis.items():
    competitor_clean = competitor.replace(' ', '_').replace('/', '_')
    
    # Export full spend comparison
    export_comparison = comparison.copy()
    export_comparison = export_comparison.reset_index()
    export_comparison.columns = ['Account_Number', 'Total_Spend', 'Total_Transactions',
                                 'Competitor_Spend', 'Competitor_Transactions',
                                 'Other_Spend', 'Other_Transactions',
                                 'Competitor_Pct', 'Other_Pct', 'Segment']
    
    output_file = output_dir / f"Competitor_{competitor_clean}_Spend_Comparison.csv"
    export_comparison.to_csv(output_file, index=False)
    
    # Export AT RISK accounts (80%+ competitor)
    at_risk = export_comparison[export_comparison['Competitor_Pct'] >= 80].copy()
    at_risk = at_risk.sort_values('Total_Spend', ascending=False)
    
    output_risk = output_dir / f"Competitor_{competitor_clean}_AT_RISK_Accounts.csv"
    at_risk.to_csv(output_risk, index=False)
    
    # Export OPPORTUNITY accounts (<20% competitor)
    opportunity = export_comparison[export_comparison['Competitor_Pct'] < 20].copy()
    opportunity = opportunity.sort_values('Total_Spend', ascending=False)
    
    output_opp = output_dir / f"Competitor_{competitor_clean}_OPPORTUNITY_Accounts.csv"
    opportunity.to_csv(output_opp, index=False)
    
    print(f"✓ Exported for {competitor}:")
    print(f"  - Full spend comparison: {output_file.name}")
    print(f"  - AT RISK accounts (80%+ competitor): {output_risk.name} ({len(at_risk):,} accounts)")
    print(f"  - OPPORTUNITY accounts (<20% competitor): {output_opp.name} ({len(opportunity):,} accounts)")
    print()

print("\n✓ All spend analysis exports complete!")
