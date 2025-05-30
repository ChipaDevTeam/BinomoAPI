"""
Constants for BinomoAPI
"""

# API Endpoints
LOGIN_URL = "https://api.binomo.com/passport/v2/sign_in?locale=en"
BALANCE_URL = "https://api.binomo.com/bank/v1/read?locale=en"

# Default values
DEFAULT_DEVICE_ID = "1b6290ce761c82f3a97189d35d2ed138"
DEFAULT_ASSET_RIC = "EURO"
DEFAULT_LOCALE = "en"

# WebSocket topics
WS_TOPICS = {
    "ACCOUNT": "account",
    "USER": "user", 
    "BASE": "base",
    "CFD_ZERO_SPREAD": "cfd_zero_spread",
    "MARATHON": "marathon",
    "BINARY_OPTIONS": "bo"
}

# Option types
OPTION_TYPES = {
    "TURBO": "turbo",
    "CLASSIC": "classic"
}

# Trade directions
TRADE_DIRECTIONS = {
    "CALL": "call",
    "PUT": "put"
}

# Account types
ACCOUNT_TYPES = {
    "DEMO": "demo",
    "REAL": "real"
}

# HTTP Headers template
DEFAULT_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache, no-store, must-revalidate',
    'content-type': 'application/json',
    'device-type': 'web',
    'origin': 'https://binomo.com',
    'referer': 'https://binomo.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0'
}
