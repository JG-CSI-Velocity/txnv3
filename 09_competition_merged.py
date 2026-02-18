# 09_competition_merged.py
# M6A: COMPETITOR CONFIGURATION & DETECTION (MERGED)
# Client: 1453 - Connex Credit Union (Connecticut)
# Market: New Haven, Hartford, Middlesex, Fairfield counties
# ===========================================================================
#
# MATCHING STRATEGY (three-tier, ordered by confidence):
#   1. exact:       merchant name matches exactly (short/ambiguous terms)
#   2. starts_with: merchant name begins with pattern (primary method)
#   3. contains:    pattern appears anywhere in name (use sparingly)
#
# Consolidated from revised tiered config + original flat-list config.
# Nothing removed unless exact duplicate.
# ===========================================================================

import pandas as pd

# ===========================================================================
# COMPETITOR CONFIGURATION
# ===========================================================================

COMPETITOR_MERCHANTS = {

    # =======================================================================
    # BIG NATIONALS -- Major banks with significant CT branch presence
    # =======================================================================
    'big_nationals': {
        'starts_with': [
            # Bank of America (83 CT branches)
            'BANK OF AMERICA', 'BANKOFAMERICA', 'B OF A', 'BOA ',
            'BK OF AMERICA', 'BK OF AMER',

            # Wells Fargo (47 CT branches)
            'WELLS FARGO', 'WELLS FARGO BANK', 'WF BANK', 'WF HOME',
            'WELLSFARGO',

            # JPMorgan Chase (63 CT branches)
            'CHASE BANK', 'CHASE BK', 'CHASE CREDIT', 'CHASE CARD',
            'CHASE HOME', 'CHASE AUTO', 'CHASE MTG',
            'JPMORGAN', 'JPMORGAN CHASE', 'JP MORGAN',

            # Citibank (12 CT branches)
            'CITIBANK', 'CITI BANK', 'CITI CARD', 'CITICORP',
            'CITI MORTGAGE', 'CITIMORTGAGE',

            # TD Bank (53 CT branches)
            'TD BANK', 'TD BK', 'TD BANKNORTH', 'TDBANK',

            # Citizens Bank (30 CT branches)
            'CITIZENS BANK', 'CITIZENS BK', 'CITIZENS FINANCIAL',

            # Santander (13 CT branches)
            'SANTANDER', 'SANTANDER BANK',

            # KeyBank (47 CT branches)
            'KEYBANK', 'KEY BANK', 'KEY BK',

            # M&T Bank (117 CT branches -- largest in state)
            'M&T BANK', 'M&T BK', 'M AND T BANK', 'M AND T BK',
            'MANUFACTURERS AND TRADERS',

            # US Bank
            'US BANK', 'U.S. BANK', 'US BK', 'USB ',

            # Capital One (banking arm)
            'CAPITAL ONE BK', 'CAPITAL ONE BANK', 'CAPITAL ONE 360',
            'CAP ONE BANK', 'CAPITALONE BK',

            # PNC Bank
            'PNC BANK', 'PNC BK',
        ],
        'exact': [
            'CHASE', 'KEYBANK', 'SANTANDER', 'BOA', 'CITI', 'CITIZENS',
        ],
    },

    # =======================================================================
    # REGIONALS -- CT community/savings banks in Connex's footprint
    # =======================================================================
    'regionals': {
        'starts_with': [
            # Webster Bank (95 CT branches -- 2nd largest)
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

            # Dime Bank
            'DIME BANK',

            # SI Financial
            'SI FINANCIAL',

            # Washington Trust
            'WASHINGTON TRUST',

            # Savings Bank of Walpole
            'SAVINGS BANK OF WALPOLE',

            # Peoples United
            'PEOPLES UNITED',

            # First National Bank CT
            'FIRST NATIONAL BANK CT', 'PATRIOT NATIONAL',
        ],
        'exact': [
            'BANKWELL',
        ],
    },

    # =======================================================================
    # CREDIT UNIONS -- Local/regional CUs competing in Connex's market
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
            'NUTMEG STATE FCU',
            'FINEX CREDIT UNION', 'FINEX CU', 'FINEX FCU',
            'WESTERN CT FCU', 'WESTERN CONNECTICUT FCU',
            'ISLAND FEDERAL CU', 'ISLAND FEDERAL CREDIT',

            # National CUs with CT presence
            'NAVY FEDERAL', 'NAVY FED', 'NFCU',
            'GOLDEN 1 CREDIT', 'GOLDEN 1 CU',
            'PENTAGON FEDERAL', 'PENTAGON FCU', 'PENFED',
            'STATE EMPLOYEES CU', 'SECU ',
            'USAA',
            'ALLIANT CREDIT',
            'DIGITAL FCU',

            # From original config
            'AMERICAN EAGLE FCU',
            'CHARTER OAK FCU',
            'SIKORSKY FCU',
            'TEACHERS FCU',
            'YALE FEDERAL',
        ],
    },

    # =======================================================================
    # DIGITAL BANKS -- Online-only banks (universal, no location customization)
    # =======================================================================
    'digital_banks': {
        'starts_with': [
            # Pure digital banks
            'ALLY BANK', 'ALLY BK', 'ALLY FINANCIAL',
            'DISCOVER BANK', 'DISCOVER BK', 'DISCOVER SAVINGS',
            'SOFI BANK', 'SOFI MONEY', 'SOFI LENDING', 'SOFI CREDIT',
            'SOFI',
            'CHIME BANK', 'CHIME FINANCIAL',
            'VARO BANK', 'VARO MONEY',
            'GO2BANK',
            'GREEN DOT BANK', 'GREEN DOT BK', 'GREENDOT',

            # Neobank / BaaS infrastructure banks
            'THE BANCORP', 'BANCORP BANK',
            'STRIDE BANK',
            'COASTAL COMMUNITY BK',

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

            # Fintech lending
            'DAVE INC', 'DAVE APP',
            'EARNIN',
            'BRIGIT',
            'POSSIBLE FINANCE',
            'CURRENT CARD',
        ],
        'contains': [
            'CHIME',
            'VARO',
            'GREEN DOT',
            'SYNCHRONY',
        ],
        'exact': [
            'CHIME', 'REVOLUT', 'BETTERMENT', 'WEALTHFRONT',
            'SOFI', 'ROBINHOOD', 'MARCUS',
        ],
    },

    # =======================================================================
    # WALLETS & P2P -- Payment platforms (universal)
    # =======================================================================
    'wallets_p2p': {
        'starts_with': [
            'PAYPAL',
            'VENMO',
            'CASH APP', 'CASHAPP',
            'APPLE CASH', 'APPLE CARD', 'APPLE PAY CASH',
            'GOOGLE PAY', 'GOOGLEPAY',
            'ZELLE',
            'SQ *',
        ],
        'contains': [
            'PAYPAL',
            'VENMO',
            'CASH APP', 'CASHAPP',
            'APPLE CASH',
            'GOOGLE PAY',
            'ZELLE',
        ],
        'exact': [
            'PAYPAL', 'VENMO',
        ],
    },

    # =======================================================================
    # BNPL -- Buy Now Pay Later (universal)
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
        'contains': [
            'AFTERPAY',
            'KLARNA',
            'AFFIRM',
            'SEZZLE',
            'ZIP PAY',
            'QUADPAY',
        ],
        'exact': [
            'KLARNA', 'AFTERPAY', 'SEZZLE',
        ],
    },

    # =======================================================================
    # ALT FINANCE -- Alternative financial services
    # =======================================================================
    'alt_finance': {
        'starts_with': [
            'FLEX FINANCE', 'FLEXFINANCE',
            'MONEYLION',
            'ALBERT SAVINGS',
            'EMPOWER FINANCE',
        ],
    },
}

# Reporting category groupings
TRUE_COMPETITORS = ['big_nationals', 'regionals', 'credit_unions', 'digital_banks']
PAYMENT_ECOSYSTEMS = ['wallets_p2p', 'bnpl']

# Financial MCC codes for unmatched discovery
FINANCIAL_MCC_CODES = [
    6010,  # Financial Institution -- Manual Cash Disbursements
    6011,  # Financial Institution -- Automated Cash Disbursements (ATMs)
    6012,  # Financial Institution -- Merchandise and Services
    6051,  # Non-Financial Institutions -- Foreign Currency, Money Orders
    6211,  # Security Brokers/Dealers
    6300,  # Insurance
]

# False positive exclusions
FALSE_POSITIVES = [
    'TOWING', 'TOW SERVICE', 'BODY SHOP',
    'AUTO REPAIR', 'AUTO PARTS', 'AUTOZONE', 'AUTO TRADER',
    'TRADER JOE',
    'CHASE OUTDOORS',
    'CURRENT ELECTRIC',
]


# ===========================================================================
# MATCHING FUNCTIONS
# ===========================================================================

def classify_competitor(merchant_name, config=COMPETITOR_MERCHANTS):
    """
    Classify a merchant as a competitor using three-tier matching.

    Priority: exact -> starts_with -> contains
    Returns: (category, matched_pattern) or (None, None)
    """
    if not merchant_name or not isinstance(merchant_name, str):
        return None, None

    name = merchant_name.upper().strip()

    # Check false positives first
    for fp in FALSE_POSITIVES:
        if fp in name:
            return None, None

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

    # Pass 3: Contains matches (use sparingly -- higher false positive risk)
    for category, rules in config.items():
        for pattern in rules.get('contains', []):
            if pattern in name:
                return category, pattern

    return None, None


def tag_competitors(df, merchant_col='merchant_consolidated'):
    """
    Tag all transactions with competitor category and matched pattern.
    Adds two columns: competitor_category, competitor_match

    Parameters:
        df: DataFrame with merchant names
        merchant_col: column name containing merchant names

    Returns:
        DataFrame with competitor_category and competitor_match columns added
    """
    results = df[merchant_col].apply(
        lambda x: classify_competitor(x) if pd.notna(x) else (None, None)
    )
    df['competitor_category'] = results.apply(lambda x: x[0])
    df['competitor_match'] = results.apply(lambda x: x[1])
    return df


def discover_unmatched_financial(df, merchant_col='merchant_consolidated',
                                 mcc_col='mcc_code'):
    """
    Find merchants with financial MCC codes that weren't matched as competitors.
    These are candidates to ADD to the config.

    Returns a DataFrame of unmatched financial merchants sorted by spend.
    """
    untagged = df[df['competitor_category'].isna()].copy()

    if mcc_col in untagged.columns:
        financial = untagged[untagged[mcc_col].isin(FINANCIAL_MCC_CODES)]
    else:
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
        print("No unmatched financial merchants found.")
        return pd.DataFrame()

    summary = financial.groupby(merchant_col).agg(
        transaction_count=('amount', 'count'),
        total_spend=('amount', 'sum'),
        unique_accounts=('primary_account_num', 'nunique'),
    ).sort_values('total_spend', ascending=False)

    return summary


def print_config_summary(config=COMPETITOR_MERCHANTS):
    """Print a summary of the competitor configuration."""
    print("=" * 80)
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
            print(f"    contains:    {n_contains:3d} patterns")

    print(f"\n{'=' * 80}")
    print(f"  Total categories: {len(config)}")
    print(f"  Total patterns:   {total_patterns}")
    print("=" * 80)


# ===========================================================================
# ITEMS REQUIRING REVIEW
# ===========================================================================
# SUTTON     - Original had in wallets_p2p, not a wallet. Move to regionals?
# LINCOLN SAVINGS - Original had in wallets_p2p, not a wallet. Move to regionals?
# CURRENT    - Bare "CURRENT" matches "CURRENT ELECTRIC". Using "CURRENT CARD".
# ZIP        - Bare "ZIP" too generic. Using "ZIP PAY"/"ZIPPAY".
# SQ*        - Square payments. Using "SQ *" (with space) for starts_with.
# MARCUS     - Bare "MARCUS" could match non-Goldman. Added as exact only.
# GOLDMAN SACHS - Expanded to "GOLDMAN SACHS BANK" in starts_with.
# ===========================================================================
