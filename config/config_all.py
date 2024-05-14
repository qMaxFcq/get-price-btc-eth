# --------- Logger ---------
LOG_MAIN = "log_main"
LOG_UPDATE_PRICE = "log_update_price"
LOG_BINANCE = "log_binance"
LOG_BITKUB = "log_bitkub"
LOG_BINANCE_USDT = "log_binance_usdt"
LOG_GOOGLE = "log_googlefi"
LOG_INVX = "log_invx"
LOG_OKX = "log_okx"
LOG_Z = "log_z"
LOG_PLUS = "log_plus"

# --------- Shop Name ---------
OURS_SHOP = [
    "MoneySwap",
    "MookieGoldenMonkey",
    "Money quick",
    "Never Sleep",
    "เฮงเฮงเฮง",
    "TestTest",
    "WGroup",
    "19TECH",
]

# --------- Exchange ---------
EXCHANGE = {"Binance": 1, "Innovestx": 2, "Bitkub": 3, "Bitazza": 4, "Okx": 5, "Z": 6}

# --------- Rate Name ---------
COMPLETE_RATE = 0.950  # 95%

# --------- Coin ---------
ASSETS = ["btc", "eth", "bnb"]
ASSETS_CRYPTO_USDT = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
TRADE_TYPES = ["buy", "sell"]

# --------- Condition ---------
MIN_AMOUNT_BITKUB = 50000
MIN_AMOUNT_INNOVESTX = 50000
MIN_AMOUNT_BNTH = 500000


# --------- Limit Price ---------
FILTER_LIMIT_PRICE = {
    "btc": {
        "day": {
            "1": {
                "row1": {"min": 50000},
                "row2": {"min": 10000},
            },
            "2": {
                "row1": {"min": 20000},
                "row2": {"min": 10000},
            },
            "3": {
                "row1": {"min": 10000},
                "row2": {"min": 10000},
            },
            "4": {
                "row1": {"min": 10000},
                "row2": {"min": 10000},
            },
            "5": {
                "row1": {"min": 5000},
                "row2": {"min": 5000},
            },
        },
        "night": {
            "1": {
                "row1": {"min": 10000},
                "row2": {"min": 10000},
            },
            "2": {
                "row1": {"min": 1000},
                "row2": {"min": 1000},
            },
        },
    },
    "eth": {
        "day": {
            "1": {
                "row1": {"min": 1000},
                "row2": {"min": 1000},
            },
        },
        "night": {
            "2": {
                "row1": {"min": 1000},
                "row2": {"min": 1000},
            },
        },
    },
    "bnb": {
        "day": {
            "1": {
                "row1": {"min": 1000},
                "row2": {"min": 1000},
            },
        },
        "night": {
            "2": {
                "row1": {"min": 1000},
                "row2": {"min": 1000},
            },
        },
    },
}
