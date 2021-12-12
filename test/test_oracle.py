from unittest import TestCase
from contextlib import contextmanager
from copy import deepcopy
from pytezos import ContractInterface, MichelsonRuntimeError, pytezos
from datetime import datetime
from pytezos.michelson.types.big_map import big_map_diff_to_lazy_diff
from pytezos.michelson.types.option import OptionType
from pytezos.michelson.types.option import SomeLiteral, NoneLiteral


def date_to_string(date: int) -> str:
    return str(datetime.utcfromtimestamp(date).strftime('%Y-%m-%dT%H:%M:%SZ'))


entrypoint_doesnt_exist = "Entrypoint doesn't exist"
only_admin = "Only admin"
amount_must_be_zero_tez = "Amount must be 0"
already_whitelisted = "User is already whitelisted"
already_blacklisted = "User is already blacklisted"
data_not_found = "Pair not found"
request_already_exists = "Request already exists"
not_whitelisted = "User isn't whitelisted"
request_not_found = "Request not found"
invalid_address = "Invalid address"
already_supported = "This pair is already supported"
pair_not_supported = "This pair isn't supported"

contract_address = "KT1BEqzn5Wx8uJrZNvuS9DVHmLvG9td3fDLi"
receive = "receive"
alice = 'tz1hNVs94TTjZh6BZ1PM5HL83A7aiZXkQ8ur'
admin = 'tz1fABJ97CJMSP2DKrQx2HAFazh6GgahQ7ZK'
bob = 'tz1c6PPijJnZYjKiSQND4pMtGMg6csGeAiiF'
oscar = 'tz1Phy92c2n817D17dUGzxNgw1qCkNSTWZY2'
fox = 'tz1XH5UyhRCUmCdUUbqD4tZaaqRTgGaFXt7q'

compiled_contract_path = "Oracle.tz"

JET_LAG = 3600

btc_high_price = 10_000
btc_low_price = 5
volume = 500
last_price = 1_000
quote_volume = 100_000
open_timestamp = 0
close_timestamp = 100
update_timestamp = 0

open_time = date_to_string(open_timestamp)
close_time = date_to_string(close_timestamp)
update_time = date_to_string(update_timestamp)

initial_storage = ContractInterface.from_file(compiled_contract_path).storage.dummy()
initial_storage["admin"] = admin
initial_storage["counter"] = 0
initial_storage["supported_pairs"] = ["BTCETH"]
initial_storage["prices"] = {
    "BTCETH": {
        "pair": "BTCETH",
        "update_time": update_timestamp,
        "open_time": open_timestamp,
        "close_time": close_timestamp,
        "last_price": last_price,
        "low_price": btc_low_price,
        "high_price": btc_high_price,
        "volume": volume,
        "quote_volume": quote_volume
    }
}


class OracleContractTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = ContractInterface.from_file(compiled_contract_path)
        cls.maxDiff = None

    @contextmanager
    def raisesMichelsonError(self, error_message):
        with self.assertRaises(MichelsonRuntimeError) as r:
            yield r

        error_msg = r.exception.format_stdout()
        if "FAILWITH" in error_msg:
            self.assertEqual(f"FAILWITH: '{error_message}'", r.exception.format_stdout())
        else:
            self.assertEqual(f"'{error_message}': ", r.exception.format_stdout())

    #######################
    # Tests for set_admin #
    #######################

    def test_set_admin_should_work(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        res = self.oracle.set_admin(bob).interpret(storage=init_storage, sender=admin)
        self.assertEqual(bob, res.storage["admin"])
        self.assertEqual([], res.operations)

    def test_set_admin_not_admin_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(only_admin):
            self.oracle.set_admin(bob).interpret(storage=init_storage, sender=alice)

    def test_set_admin_sending_XTZ_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(amount_must_be_zero_tez):
            self.oracle.set_admin(bob).interpret(storage=init_storage, sender=admin, amount=1)

    ##################
    # Whitelist user #
    ##################
    def test_whitelist_user_should_work(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        res = self.oracle.whitelist_user(bob).interpret(storage=init_storage, sender=admin)
        self.assertEqual(bob, res.storage["whitelist"].pop())
        self.assertEqual([], res.operations)

    def test_whitelist_user_not_admin_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(only_admin):
            self.oracle.whitelist_user(bob).interpret(storage=init_storage, sender=alice)

    def test_whitelist_user_sending_XTZ_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(amount_must_be_zero_tez):
            self.oracle.whitelist_user(bob).interpret(storage=init_storage, sender=admin, amount=1)

    def test_whitelist_user_already_whitelisted_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        init_storage["whitelist"] = [bob]
        # Execute entrypoint
        with self.raisesMichelsonError(already_whitelisted):
            self.oracle.whitelist_user(bob).interpret(storage=init_storage, sender=admin)

    ##################
    # Blacklist user #
    ##################
    def test_blacklist_user_should_work(self):
        # Init
        init_storage = deepcopy(initial_storage)
        init_storage["whitelist"] = [bob]
        # Execute entrypoint
        res = self.oracle.blacklist_user(bob).interpret(storage=init_storage, sender=admin)
        self.assertEqual([], res.storage["whitelist"])
        self.assertEqual([], res.operations)

    def test_blacklist_user_not_admin_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(only_admin):
            self.oracle.blacklist_user(bob).interpret(storage=init_storage, sender=alice)

    def test_blacklist_user_sending_XTZ_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(amount_must_be_zero_tez):
            self.oracle.blacklist_user(bob).interpret(storage=init_storage, sender=admin, amount=1)

    def test_blacklist_user_already_blacklisted_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(already_blacklisted):
            self.oracle.blacklist_user(bob).interpret(storage=init_storage, sender=admin)

    ##################
    # Whitelist pair #
    ##################
    def test_whitelist_pair_should_work(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        res = self.oracle.whitelist_pair("BTCXTZ").interpret(storage=init_storage, sender=admin)
        self.assertEqual("BTCXTZ", res.storage["supported_pairs"].pop())
        self.assertEqual([], res.operations)

    def test_whitelist_pair_not_admin_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(only_admin):
            self.oracle.whitelist_pair("BTCXTZ").interpret(storage=init_storage, sender=alice)

    def test_whitelist_pair_sending_XTZ_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(amount_must_be_zero_tez):
            self.oracle.whitelist_pair("BTCXTZ").interpret(storage=init_storage, sender=admin, amount=1)

    def test_whitelist_pair_already_whitelisted_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(already_supported):
            self.oracle.whitelist_pair("BTCETH").interpret(storage=init_storage, sender=admin)

    ##################
    # Blacklist pair #
    ##################
    def test_blacklist_pair_should_work(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        res = self.oracle.blacklist_pair("BTCETH").interpret(storage=init_storage, sender=admin)
        self.assertEqual([], res.storage["supported_pairs"])
        self.assertEqual([], res.operations)

    def test_blacklist_pair_not_admin_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(only_admin):
            self.oracle.blacklist_pair("BTCETH").interpret(storage=init_storage, sender=alice)

    def test_blacklist_pair_sending_XTZ_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(amount_must_be_zero_tez):
            self.oracle.blacklist_pair("BTCETH").interpret(storage=init_storage, sender=admin, amount=1)

    def test_blacklist_pair_already_blacklisted_should_fail(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        with self.raisesMichelsonError(pair_not_supported):
            self.oracle.blacklist_pair("BTCXTZ").interpret(storage=init_storage, sender=admin)
    # TODO: faire les tests
    # TODO: faire les tests
    # TODO: faire les tests
    # TODO: faire les tests
    # TODO: faire les tests
    ###############
    # harvest XTZ #
    ###############
    def test_harvest_xtz_admin_should_work(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        res = self.oracle.harvest_xtz(admin).interpret(storage=init_storage, sender=admin, amount=3)
        print()

    # TODO: faire les tests
    # TODO: faire les tests
    # TODO: faire les tests
    # TODO: faire les tests
    # TODO: faire les tests
    # TODO: faire les tests
    # TODO: faire les tests

    #############
    # get price #
    #############
    def test_get_price_should_work_and_respond(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        params = {
            "pair": "BTCETH",
            "target": "KT1BEqzn5Wx8uJrZNvuS9DVHmLvG9td3fDLi%receive",
            "target_address": contract_address,
            "target_entrypoint": receive
        }
        expected_requests = {
            0: {
                "pair": "BTCETH",
                "target_address": contract_address,
                "target_entrypoint": receive,
                "status": True
            }
        }

        res = self.oracle.get_price(params).interpret(storage=init_storage, sender=bob, amount=1000)
        self.assertDictEqual(expected_requests, res.storage["requests"])
        self.assertEqual(1, res.storage["counter"])
        # Verify transaction
        self.assertEqual(contract_address, res.operations[0]["source"])
        self.assertEqual(contract_address, res.operations[0]["destination"])
        self.assertEqual(receive, res.operations[0]["parameters"]["entrypoint"])
        self.assertEqual(quote_volume, int(res.operations[0]["parameters"]["value"]["args"][0]["args"][2]["int"]))
        self.assertEqual('BTCETH', res.operations[0]["parameters"]["value"]["args"][0]["args"][1]["args"][1]["string"])
        self.assertEqual(open_time, res.operations[0]["parameters"]["value"]["args"][0]["args"][1]["args"][0]["string"])
        self.assertEqual(close_time,
                         res.operations[0]["parameters"]["value"]["args"][0]["args"][0]["args"][0]["args"][0]["string"])
        self.assertEqual(update_time, res.operations[0]["parameters"]["value"]["args"][0]["args"][3]["string"])
        self.assertEqual(btc_low_price,
                         int(res.operations[0]["parameters"]["value"]["args"][0]["args"][0]["args"][2]["int"]))
        self.assertEqual(btc_high_price, int(
            res.operations[0]["parameters"]["value"]["args"][0]["args"][0]["args"][0]["args"][1]["int"]))
        self.assertEqual(last_price,
                         int(res.operations[0]["parameters"]["value"]["args"][0]["args"][0]["args"][1]["int"]))
        self.assertEqual(volume, int(res.operations[0]["parameters"]["value"]["args"][1]["int"]))

    def test_get_price_should_work_and_not_respond(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        params = {
            "pair": "BTCETH",
            "target": "KT1BEqzn5Wx8uJrZNvuS9DVHmLvG9td3fDLi%receive",
            "target_address": contract_address,
            "target_entrypoint": receive
        }
        expected_requests = {
            0: {
                "pair": "BTCETH",
                "target_address": contract_address,
                "target_entrypoint": receive,
                "status": False
            }
        }

        res = self.oracle.get_price(params).interpret(storage=init_storage, sender=bob, amount=1000, now=31)
        self.assertEqual(1, res.storage["counter"])
        self.assertDictEqual(expected_requests, res.storage["requests"])
        self.assertEqual([], res.operations)

    def test_get_price_not_supported_currency_should_not_work(self):
        # Init
        init_storage = deepcopy(initial_storage)
        # Execute entrypoint
        params = {
            "pair": "BTCXTZ",
            "target": "KT1BEqzn5Wx8uJrZNvuS9DVHmLvG9td3fDLi%receive",
            "target_address": contract_address,
            "target_entrypoint": receive
        }
        with self.raisesMichelsonError(pair_not_supported):
            self.oracle.get_price(params).interpret(storage=init_storage, sender=bob, amount=1000)
    ##########
    # update #
    ##########

    def test_update_whitelisted_should_work(self):
        # Init
        init_storage = deepcopy(initial_storage)
        init_storage["whitelist"] = [bob]
        init_storage["requests"] = {
            0: {
                "pair": "BTCETH",
                "target_address": contract_address,
                "target_entrypoint": receive,
                "status": False
            }
        }
        update_open_timestamp = 15
        update_close_timestamp = 30
        update_last_price = 1003
        update_low_price = 40
        update_volume = 400
        update_high_price = 19_000
        update_quote_volume = 900

        # Execute entrypoint
        update_params = {
            "pair": "BTCETH",
            "open_time": update_open_timestamp,
            "close_time": update_close_timestamp,
            "last_price": update_last_price,
            "low_price": update_low_price,
            "high_price": update_high_price,
            "volume": update_volume,
            "quote_volume": update_quote_volume,
            "request_id": 0,
            "target": f"{contract_address}%{receive}"
        }
        expected_prices = {
            "BTCETH": {
                "open_time": update_open_timestamp,
                "close_time": update_close_timestamp,
                "last_price": update_last_price,
                "low_price": update_low_price,
                "high_price": update_high_price,
                "volume": update_volume,
                "quote_volume": update_quote_volume,
                "update_time": 60,
                "pair": "BTCETH",
            }
        }
        res = self.oracle.update(update_params).interpret(storage=init_storage, sender=bob, now=60)
        self.assertDictEqual(expected_prices, res.storage["prices"])
        self.assertTrue(res.storage["requests"][0]["status"])

        self.assertEqual(contract_address, res.operations[0]["source"])
        self.assertEqual(contract_address, res.operations[0]["destination"])
        self.assertEqual(receive, res.operations[0]["parameters"]["entrypoint"])
        self.assertEqual(update_quote_volume, int(res.operations[0]["parameters"]["value"]["args"][0]["args"][2]["int"]))
        self.assertEqual('BTCETH', res.operations[0]["parameters"]["value"]["args"][0]["args"][1]["args"][1]["string"])
        self.assertEqual(date_to_string(update_open_timestamp), res.operations[0]["parameters"]["value"]["args"][0]["args"][1]["args"][0]["string"])
        self.assertEqual(date_to_string(update_close_timestamp),
                         res.operations[0]["parameters"]["value"]["args"][0]["args"][0]["args"][0]["args"][0]["string"])
        self.assertEqual(date_to_string(60), res.operations[0]["parameters"]["value"]["args"][0]["args"][3]["string"])
        self.assertEqual(update_low_price,
                         int(res.operations[0]["parameters"]["value"]["args"][0]["args"][0]["args"][2]["int"]))
        self.assertEqual(update_high_price, int(
            res.operations[0]["parameters"]["value"]["args"][0]["args"][0]["args"][0]["args"][1]["int"]))
        self.assertEqual(update_last_price,
                         int(res.operations[0]["parameters"]["value"]["args"][0]["args"][0]["args"][1]["int"]))
        self.assertEqual(update_volume, int(res.operations[0]["parameters"]["value"]["args"][1]["int"]))

    def update_blacklisted_should_not_work(self):
        # Init
        init_storage = deepcopy(initial_storage)
        update_open_timestamp = 15
        update_close_timestamp = 30
        update_last_price = 1003
        update_low_price = 40
        update_volume = 400
        update_high_price = 19_000
        update_quote_volume = 900

        # Execute entrypoint
        update_params = {
            "pair": "BTCETH",
            "open_time": update_open_timestamp,
            "close_time": update_close_timestamp,
            "last_price": update_last_price,
            "low_price": update_low_price,
            "high_price": update_high_price,
            "volume": update_volume,
            "quote_volume": update_quote_volume,
            "request_id": 0,
            "target": f"{contract_address}%{receive}"
        }
        # Execute entrypoint
        with self.raisesMichelsonError(not_whitelisted):
            self.oracle.update(update_params).interpret(storage=init_storage, sender=bob)
