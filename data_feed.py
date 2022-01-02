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

contract = admin.contract("KT19jdR8FkMygj6Ch1tpNnqQWPpDDwGPeKUq")  # set the contract
counter = int(contract.storage['counter']())

while True:

    try:  # try catch if the rpc node is down
        if int(contract.storage['counter']()) > counter:
            try:
                res = get(
                    url="https://api.binance.com/api/v3/ticker/24hr?symbol=XTZUSDT").json()  # get the api data from binance
#                     {
#     pair: string;
#     open_time: timestamp;
#     close_time: timestamp;
#     last_price: nat;
#     low_price: nat;
#     high_price: nat;
#     volume: nat;
#     quote_volume: nat;
#     request_id: nat;
#     target: pair contract
# }
                
                tx = contract.selectWinner(winner).send(min_confirmations=1)  # select the winner
                counter = int(contract.storage['counter']())
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
        sleep(20)
    sleep(100)