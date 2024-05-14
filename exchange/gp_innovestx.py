from os import getcwd, getenv
from dotenv import load_dotenv
import sys

sys.path.append(getcwd())
from helper.filter_avg_price import find_min_amount
from config.config_all import LOG_INVX, MIN_AMOUNT_INNOVESTX
from helper.logger import Logger
import asyncio
import websockets
import json
from pandas import DataFrame, concat
from ast import literal_eval


########### Local Import ###########


logger = Logger(LOG_INVX)


async def connect_websocket(url, message):
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
    return response


def parse_depth_response(response):
    column_data = [
        "Col1",
        "Col2",
        "Col3",
        "Col4",
        "Col5",
        "Col6",
        "price",
        "Col8",
        "amount",
        "side",
    ]
    response_data = literal_eval(json.loads(response).get("o"))
    data = DataFrame(response_data, columns=column_data)

    depth = DataFrame()
    depth["ask_price"] = data.loc[data["side"] == 1, "price"].reset_index(drop=True)
    depth["ask_amount"] = data.loc[data["side"] == 1, "amount"].reset_index(drop=True)
    depth["bid_price"] = data.loc[data["side"] == 0, "price"].reset_index(drop=True)
    depth["bid_amount"] = data.loc[data["side"] == 0, "amount"].reset_index(drop=True)

    dtypes = {
        "ask_price": float,
        "ask_amount": float,
        "bid_price": float,
        "bid_amount": float,
    }
    depth = depth.astype(dtypes).reset_index(drop=True)
    return depth


insId_mapping = {
    "1": "BTC",
    "2": "ETH",
    "6": "BNB",
}


async def gp_innovestx(symbol: str = None):
    if symbol in insId_mapping:
        symbol_name = insId_mapping[symbol]
        try:
            url = "wss://api-digitalassets.scbs.com/WSGateway"
            subscription_message = {
                "m": 0,
                "i": 18,
                "n": "SubscribeLevel2",
                "o": f'{{"OMSId":1,"InstrumentId":{symbol},"Depth":50}}',
            }

            response = await connect_websocket(url, subscription_message)
            depth = parse_depth_response(response)
            # เพิ่ม column "symbol" ใน DataFrame และกำหนดค่าเป็น symbol_name
            return depth.assign(symbol=symbol_name)
        except Exception as err:
            logger.warn(f"Error from gp_innovestx : {err}")
            return DataFrame([])


insId = ["1", "2", "6"]


async def get_innovestx_crypto():
    dept_data_list = []
    for symbol in insId:
        depth_data = await gp_innovestx(symbol)
        dept_data_list.append(depth_data)
    return dept_data_list


async def final_price_invx():
    try:
        results = []
        p2p_data_invx_list = await get_innovestx_crypto()

        for p2p_data_invx in p2p_data_invx_list:
            if not p2p_data_invx.empty:
                bid_price, ask_price = find_min_amount(
                    depth=p2p_data_invx, maxi=MIN_AMOUNT_INNOVESTX
                )

                for price, trade_type, symbol in [
                    (bid_price, "buy", p2p_data_invx["symbol"].iloc[0]),
                    (ask_price, "sell", p2p_data_invx["symbol"].iloc[0]),
                ]:
                    update_values = {
                        "exchange_id": int(2),
                        "shop_p2p_name": str("invx"),
                        "trade_type": str(trade_type),
                        "symbol": str(symbol) + "_THB",
                        "price": round(float(price), 3),
                        "min_amount_order": float(MIN_AMOUNT_INNOVESTX),
                        "max_amount_order": 0,
                        "complete_rate": 0,
                    }

                    results.append(DataFrame([update_values]))

        if results:
            final_result = concat(results, ignore_index=True)
            # print(final_result)
            return final_result
    except Exception as err:
        logger.warn(f"Error from gp_innovestx : {err}")
        return DataFrame([])


async def main():
    await final_price_invx()


# Run the event loop
asyncio.run(main())
