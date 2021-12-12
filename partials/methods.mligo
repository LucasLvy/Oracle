#include "types.mligo"
#include "errors.mligo"
// -----------------
// --  CONSTANTS  --
// -----------------

let no_operation : operation list = []
let oracle_price : tez = 1000mutez

// -----------------
// --  INTERNALS  --
// -----------------
[@inline]
let send_data (contract: pair contract) (data: pair) : operation = Tezos.transaction (data) 0mutez (contract)

[@inline]
let xtz_transfer (to_ : address) (amount_ : tez) : operation =
    let to_contract : unit contract =
    match (Tezos.get_contract_opt to_ : unit contract option) with
    | None -> (failwith invalid_address : unit contract)
    | Some c -> c
    in
    Tezos.transaction () amount_ to_contract
// ------------------
// -- ENTRY POINTS --
// ------------------

let harvest_xtz (s : storage) (to_ : address) : return =
    let op : operation = xtz_transfer (to_) (Tezos.balance) in
    ([op], s)

let whitelist_user (s: storage) (user: address) : return =
    let admin_address : address = s.admin in
    let _check_if_admin : unit = assert_with_error (Tezos.sender = admin_address) only_admin in
    let _check_if_no_tez : unit = assert_with_error (Tezos.amount = 0tez) amount_must_be_zero_tez in
    let whitelist : address set = s.whitelist in
    let _check_if_already_whitelisted : unit = assert_with_error (not (Set.mem user whitelist)) already_whitelisted in
    let final_storage = { s with whitelist = Set.add user whitelist } in
    (no_operation, final_storage)

let blacklist_user(s: storage) (user: address) : return =
    let admin_address : address = s.admin in
    let _check_if_admin : unit = assert_with_error (Tezos.sender = admin_address) only_admin in
    let _check_if_no_tez : unit = assert_with_error (Tezos.amount = 0tez) amount_must_be_zero_tez in
    let whitelist : address set = s.whitelist in
    let _check_if_already_blacklisted : unit = assert_with_error (Set.mem user whitelist) already_blacklisted in
    let final_storage = { s with whitelist = Set.remove user whitelist } in
    (no_operation, final_storage)

let whitelist_pair (s: storage) (pair: string) : return =
    let admin_address : address = s.admin in
    let _check_if_admin : unit = assert_with_error (Tezos.sender = admin_address) only_admin in
    let _check_if_no_tez : unit = assert_with_error (Tezos.amount = 0tez) amount_must_be_zero_tez in
    let supported_pairs : string set = s.supported_pairs in
    let _check_if_already_supported : unit = assert_with_error (not (Set.mem pair supported_pairs)) already_supported in
    let final_storage = { s with supported_pairs = Set.add pair supported_pairs } in
    (no_operation, final_storage)

let blacklist_pair(s: storage) (pair: string) : return =
    let admin_address : address = s.admin in
    let _check_if_admin : unit = assert_with_error (Tezos.sender = admin_address) only_admin in
    let _check_if_no_tez : unit = assert_with_error (Tezos.amount = 0tez) amount_must_be_zero_tez in
    let supported_pairs : string set = s.supported_pairs in
    let _check_if_already_not_supported : unit = assert_with_error (Set.mem pair supported_pairs) pair_not_supported in
    let final_storage = { s with supported_pairs = Set.remove pair supported_pairs } in
    (no_operation, final_storage)

let set_admin (s : storage) (new_admin : address) : return =
    let admin_address : address = s.admin in
    let _check_if_admin : unit = assert_with_error (Tezos.sender = admin_address) only_admin in
    let _check_if_no_tez : unit = assert_with_error (Tezos.amount = 0tez) amount_must_be_zero_tez in
    let final_storage = { s with admin = new_admin } in
    (no_operation, final_storage)

let get_price (s : storage) (params : get_price_params) : return =
    let _check_if_tez : unit = assert_with_error (Tezos.amount = oracle_price) amount_must_be_oracle_price in
    let pair : string = params.pair in
    let _check_if_pair_supported : unit = assert_with_error (Set.mem pair s.supported_pairs) pair_not_supported in
    let prices : (string, pair) map = s.prices in
    let should_update : bool = match Map.find_opt params.pair prices with
    | Some val -> not (val.update_time >= Tezos.now)
    | None -> true
    in
    let user_request : request = {
        pair = pair;
        target_address = params.target_address;
        target_entrypoint = params.target_entrypoint;
        status = not (should_update)
    } in
    let counter : nat = s.counter in
    let requests : (nat, request) big_map = s.requests in
    let request_opt : request option = Big_map.find_opt counter s.requests in
    let requests_final : (nat, request) big_map = match request_opt with 
    | None -> Big_map.add counter user_request s.requests
    | Some(val) -> (failwith request_already_exists : (nat, request) big_map)
    in
    if not should_update then 
        let data : pair = match Big_map.find_opt params.pair prices with
        | Some val -> val
        | None -> (failwith data_not_found : pair)
        in
        let op : operation = send_data params.target data in
        let final_storage = { s with requests = requests_final; counter = abs(counter + 1)  } in
        ([op], final_storage)
    else let final_storage = { s with requests = requests_final; counter = abs(counter + 1)  } in
    (no_operation, final_storage)

let update (s : storage) (params : update_params) : return =
    let _check_if_whitelisted : unit = assert_with_error (Set.mem Tezos.sender s.whitelist) not_whitelisted in
    let pair : string = params.pair in
    let _check_if_pair_supported : unit = assert_with_error (Set.mem pair s.supported_pairs) pair_not_supported in
    let prices : (string, pair) map = s.prices in
    let request_id : nat = params.request_id in
    let requests : (nat, request) big_map = s.requests in
    let new_pair : pair = {
        pair = pair;
        update_time = Tezos.now;
        open_time = params.open_time;
        close_time = params.close_time;
        last_price = params.last_price;
        low_price = params.low_price;
        high_price = params.high_price;
        volume = params.volume;
        quote_volume = params.quote_volume
    } in
    let pair_opt : pair option = Map.find_opt pair prices in
    let prices_final : (string, pair) map = match pair_opt with
    | Some val -> Big_map.update (pair) (Some(new_pair)) prices
    | None -> Big_map.add (pair) (new_pair) prices
    in
    let user_request : request = match Big_map.find_opt request_id requests with
    | Some val -> { val with status = true}
    | None -> (failwith request_not_found : request)
    in
    let target : pair contract = params.target in
    let op : operation = send_data target new_pair in
    let final_requests : (nat, request) big_map = Big_map.update (request_id) (Some(user_request)) requests in
    let final_storage : storage = { s with requests = final_requests; prices = prices_final } in
    ([op], final_storage)