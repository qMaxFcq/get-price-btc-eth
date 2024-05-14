from os import getcwd
from sys import path

path.append(getcwd())
from helper.filter_avg_price import find_min_amount
from helper.logger import Logger
from config.config_all import LOG_BITKUB, MIN_AMOUNT_BITKUB
import aiohttp
import asyncio
from pandas import DataFrame, Series, concat

logger = Logger(LOG_BITKUB)


async def gp_bitkub(symbol: str) -> DataFrame:
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = "https://api.bitkub.com/api/market/depth"
            params = {"sym": symbol, "lmt": 100}
            response = await session.get(url, params=params)
            data: list = await response.json()
            depth: DataFrame = DataFrame(data)
            if depth.empty:
                raise Exception("Can Get Depth Data from bitkub")
            depth = depth.apply(Series.explode, axis=1)
            depth.columns = ("ask_price", "ask_amount", "bid_price", "bid_amount")

            return depth

    except Exception as err:
        logger.warn("Error from gp_bitkub")
        return DataFrame([])


symbol_name = ["THB_BTC", "THB_ETH", "THB_BNB"]


async def final_price_bitkub():
    try:
        results = []

        for symbol in symbol_name:
            p2p_data_bitkub = await gp_bitkub(symbol=symbol)
            result_list = []

            if not p2p_data_bitkub.empty:
                bid_price, ask_price = find_min_amount(
                    depth=p2p_data_bitkub, maxi=MIN_AMOUNT_BITKUB
                )
                symbol = symbol.split("_")[1]
                for price, trade_type in [(bid_price, "buy"), (ask_price, "sell")]:
                    update_values = {
                        "exchange_id": int(3),
                        "shop_p2p_name": str("bitkub"),
                        "trade_type": str(trade_type),
                        "symbol": str(symbol) + "_THB",
                        "price": round(float(price), 3),
                        "min_amount_order": float(MIN_AMOUNT_BITKUB),
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
        logger.warn(f"Error from gp_bitkub : {err}")
        return DataFrame([])


async def main():
    await final_price_bitkub()


# Run the event loop
asyncio.run(main())
