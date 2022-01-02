type pair = {
    pair: string;
    update_time: timestamp;
    open_time: timestamp;
    close_time: timestamp;
    last_price: nat;
    low_price: nat;
    high_price: nat;
    volume: nat;
    quote_volume: nat
}

type request = {
    pair: string;
    status: bool;
    target_address: address;
    target_entrypoint: string
}

type update_params = {
    pair: string;
    open_time: timestamp;
    close_time: timestamp;
    last_price: nat;
    low_price: nat;
    high_price: nat;
    volume: nat;
    quote_volume: nat;
    request_id: nat;
    target: pair contract
}

type get_price_params = {
    pair: string;
    target: pair contract;
    target_address: address;
    target_entrypoint: string
}

type storage = {
    admin: address;
    counter: nat;
    prices: (string, pair) map;
    whitelist: address set;
    requests: (nat,  request) big_map;
    request_price: tez;
    supported_pairs: string set;
}

type return = operation list * storage
type entrypoint =
    | Harvest_xtz of (address)
    | Change_request_price of (tez)
    | Whitelist_user of (address)
    | Blacklist_user of (address)
    | Whitelist_pair of (string)
    | Blacklist_pair of (string)
    | Set_admin of (address)
    | Get_price of (get_price_params)
    | Update of (update_params)   