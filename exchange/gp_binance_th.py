from os import getcwd
from sys import path

path.append(getcwd())
from helper.filter_avg_price import find_min_amount
from helper.logger import Logger
from config.config_all import LOG_BITKUB, MIN_AMOUNT_BNTH, ASSETS_CRYPTO_USDT
import aiohttp
import asyncio
from pandas import DataFrame, Series, concat

logger = Logger(LOG_BITKUB)


async def gp_binance_th(symbol: str) -> DataFrame:
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = "https://api.binance.th/api/v1/depth"
            params = {"symbol": symbol, "limit": 50}
            response = await session.get(url, params=params)
            data: list = await response.json()
            depth: DataFrame = DataFrame(data)
            depth.drop(columns=["lastUpdateId"], inplace=True)
            if depth.empty:
                raise Exception("Can Get Depth Data from binanceth")
            depth = depth.apply(Series.explode, axis=1)
            depth.columns = ("ask_price", "ask_amount", "bid_price", "bid_amount")
            depth = depth.astype(float)
            return depth

    except Exception as err:
        print(f"Error from gp_binance_th : {err}")
        return None


symbol_name = ["btcthb", "eththb"]
# symbol_name = ["eththb"]


async def final_binance_th():
    try:
        results = []

        for symbol in symbol_name:
            p2p_data_binance_th = await gp_binance_th(symbol=symbol)
            result_list = []

            if not p2p_data_binance_th.empty:
                bid_price, ask_price = find_min_amount(
                    depth=p2p_data_binance_th, maxi=MIN_AMOUNT_BNTH
                )

                for price, trade_type in [(bid_price, "buy"), (ask_price, "sell")]:
                    symbol_formatted = f"{symbol[:3].upper()}_{symbol[-3:].upper()}"
                    update_values = {
                        "exchange_id": int(9),
                        "shop_p2p_name": str("binance_th"),
                        "trade_type": str(trade_type),
                        "symbol": symbol_formatted,
                        "price": round(float(price), 3),
                        "min_amount_order": float(MIN_AMOUNT_BNTH),
                        "max_amount_order": 0,
                        "complete_rate": 0,
                    }

                    result_list.append(DataFrame([update_values]))

            if result_list:
                final_result = concat(result_list, ignore_index=True)
                results.append(final_result)

        if results:
            final_result_all = concat(results, ignore_index=True)
            # print(final_result_all)
            return final_result_all
    except Exception as err:
        logger.warn(f"Error from gp_binance_th : {err}")
        return DataFrame([])


async def main():
    await final_binance_th()


# Run the event loop
asyncio.run(main())

# async def final_binance_th():
#     try:
#         p2p_data_binance_th = await gp_binance_th(symbol="usdtthb")
#         result_list = []
#         if not p2p_data_binance_th.empty:
#             ask_price = p2p_data_binance_th.iloc[0]["ask_price"]
#             bid_price = p2p_data_binance_th.iloc[0]["bid_price"]

#             for price, trade_type in [
#                 (bid_price, "buy"),
#                 (ask_price, "sell"),
#             ]:
#                 update_values = {
#                     "exchange_id": int(8),
#                     "shop_p2p_name": str("binance_th"),
#                     "trade_type": str(trade_type),
#                     "symbol": SYMBOL,
#                     "price": round(float(price), 3),
#                     "min_amount_order": float(MIN_AMOUNT_BNTH),
#                     "max_amount_order": 0,
#                     "complete_rate": 0,
#                 }

#                 result_list.append(DataFrame([update_values]))

#         if result_list:
#             final_result = concat(result_list, ignore_index=True)
#             return final_result
#     except Exception as err:
#         logger.warn(f"Error from final_binance_th : {err}")
#         return DataFrame([])
