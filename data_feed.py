from pytezos import *
from time import sleep, time
from requests import get

# admin setup to be able to execute transactions
admin = pytezos.using(shell='https://hangzhounet.smartpy.io',
                      key="")
id: int = 84085

contract = admin.contract("KT1HJmhtdDw88kCEEiyaw6iYwzPsTphxzzRz")  # set the contract
counter = int(contract.storage['counter']())

while True:
    try:  # try catch if the rpc node is down
        print(int(contract.storage['counter']()), counter)
        if int(contract.storage['counter']()) > counter:
            try:

                request = get(url=f"https://api.hangzhounet.tzkt.io/v1/bigmaps/{id}/keys/{counter}").json()["value"]
                print(request)
                if request['status']:
                    break
                pair: str = "BTCETH"
                res: dict = get(
                    url=f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}").json()  # get the api data from binance
                data: dict = {
                    "pair": pair,
                    "open_time": int(int(res["openTime"])/1000),
                    "close_time": int(int(res["closeTime"])/1000),
                    "last_price": int(float(res["lastPrice"]) * 10 ** 8),
                    "low_price": int(float(res["lowPrice"]) * 10 ** 8),
                    "high_price": int(float(res["highPrice"]) * 10 ** 8),
                    "volume": int(float(res["volume"]) * 10 ** 8),
                    "quote_volume": int(float(res["quoteVolume"]) * 10 ** 8),
                    "request_id": int(counter),
                    "target": f"{request['target_address']}%{request['target_entrypoint']}"
                }
                print(data)
                tx = contract.update(data).send(min_confirmations=1)
                counter = int(contract.storage['counter']())
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
        sleep(20)
    sleep(100)
