from pytezos import *
from time import sleep, time
from requests import get
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--private-key', help="Admin's private key")
args = parser.parse_args()

# admin setup to be able to execute transactions
admin = pytezos.using(shell='https://mainnet.smartpy.io',
                      key=args.private_key)
id:int = 0

contract = admin.contract("KT19jdR8FkMygj6Ch1tpNnqQWPpDDwGPeKUq")  # set the contract
counter = int(contract.storage['counter']())

while True:

    try:  # try catch if the rpc node is down
        if int(contract.storage['counter']()) > counter:
            try:
                request: dict = get(url=f"https://api.tzkt.io/v1/bigmaps/{id}/keys/{counter}").json()["value"]
                pair: str = "XTZUSDT"
                res: dict = get(
                    url=f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}").json()  # get the api data from binance
                data: dict = {
                    "pair": pair,
                    "open_time":res["openTime"],
                    "close_time": res["closeTime"],
                    "last_price": res["lastPrice"],
                    "low_price": res["lowPrice"],
                    "high_price": res["highPrice"],
                    "volume": res["volume"],
                    "quote_volume": res["quoteVolume"],
                    "request_id": counter,
                    "target": f"{request['target_address']}%{request['target_entrypoint']}"
                }
                
                tx = contract.update(data).send(min_confirmations=1)
                counter = int(contract.storage['counter']())
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
        sleep(20)
    sleep(100)