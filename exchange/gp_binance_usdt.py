from os import getcwd
from sys import path

path.append(getcwd())
from config.config_all import LOG_BINANCE_USDT
from config.config_all import (
    ASSETS_CRYPTO_USDT,
)
import aiohttp
import asyncio
from pandas import DataFrame, concat, to_numeric
from itertools import product
from helper.logger import Logger
import json
from ast import literal_eval

logger = Logger(LOG_BINANCE_USDT)


async def fetch_spot_binance(session, symbol: str):
    try:
        url = "https://api.binance.com/api/v1/depth"
        params = {"symbol": symbol, "limit": 50}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return data
    except Exception as err:
        logger.warn(f"An error occurred in fetch_spot_binance: {err}")
        return None


async def get_spot_binance(symbol: str):
    try:
        column_data = ["price", "amount"]
        response = await fetch_spot_binance(None, symbol)
        if response:
            bid_data = response.get("bids", [])
            ask_data = response.get("asks", [])

            bid_df = DataFrame(bid_data, columns=column_data).add_prefix("bid_")
            ask_df = DataFrame(ask_data, columns=column_data).add_prefix("ask_")
            data = concat([bid_df, ask_df], axis=1)
            return data
    except Exception as err:
        logger.warn(f"An error occurred in get_spot_binance: {err}")
        return None


async def final_price_binance_crypto_usdt():
    try:
        results = []
        for symbol in ASSETS_CRYPTO_USDT:
            data = await get_spot_binance(symbol)
            data["bid_amount"] = to_numeric(data["bid_amount"])
            data["ask_amount"] = to_numeric(data["ask_amount"])
            filtered_data = data[
                (data["bid_amount"] > 0.03) | (data["ask_amount"] > 0.03)
            ]

            row = filtered_data.iloc[0]
            formatted_symbol = symbol.replace("USDT", "_USDT")

            # print(
            #     f"Symbol: {formatted_symbol}, Bid Price: {row['bid_price']}, Ask Price: {row['ask_price']}"
            # )

            for price, trade_type, symbol in [
                (row["bid_price"], "buy", formatted_symbol),
                (row["ask_price"], "sell", formatted_symbol),
            ]:
                update_values = {
                    "exchange_id": int(1),
                    "shop_p2p_name": str("binance_spot"),
                    "trade_type": str(trade_type),
                    "symbol": str(symbol),
                    "price": round(float(price), 3),
                    "min_amount_order": 0,
                    "max_amount_order": 0,
                    "complete_rate": 0,
                }

                results.append(DataFrame([update_values]))
        if results:
            final_result = concat(results, ignore_index=True)
            # print(final_result)
            return final_result

    except Exception as err:
        logger.warn(f"An error occurred in final_price_binance_crypto_usdt: {err}")
        return DataFrame([])


async def main():
    await final_price_binance_crypto_usdt()


asyncio.run(main())
