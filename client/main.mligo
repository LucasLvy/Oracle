type pair = {
    pair: string;
    update_time: timestamp;
    open_time: timestamp;
    close_time: timestamp;
    last_price: nat;
    low_price: nat;
    high_price: nat;
    volume: nat;
    quote_volume: nat;
}
type get_price_params = {
    pair: string;
    target: pair contract;
    target_address: address;
    target_entrypoint: string
}

type storage = {
    oracle_address: address;
    pair: pair;
    query_price: tez;
}
type return = operation list * storage
type entrypoint =
    | Receive_price of (pair)
    | Query_price of (string)

let no_operation : operation list = []


// -----------------
// --  INTERNALS  --
// -----------------
[@inline]
let send_query (contract: get_price_params contract) (data: get_price_params) (query_price: tez) : operation = 
Tezos.transaction (data) query_price (contract)

let query_price (s : storage) (params : string) : return =
    let _check_if_tez : unit = assert_with_error (Tezos.amount = s.query_price) "not the right amount of tez" in
    let entrypoint_opt : get_price_params contract option = Tezos.get_entrypoint_opt "%get_price" s.oracle_address in
    let entrypoint : get_price_params contract =
    match entrypoint_opt with
      | None -> (failwith "invalid address" : get_price_params contract)
      | Some c -> c
    in
    let target_opt: pair contract option = Tezos.get_entrypoint_opt "%receive_price" Tezos.self_address in
    let target : pair contract = match target_opt with
      | Some c -> c
      | None -> (failwith "fail": pair contract)
    in
    let get_price_params: get_price_params = {
        pair = params;
        target = target;
        target_address = Tezos.self_address;
        target_entrypoint = "receive_price";
    } in
    let op: operation = send_query entrypoint get_price_params s.query_price in
    ([op], s)

let receive_price (s : storage) (params: pair) : return =
    (no_operation, {s with pair = params})


let main (action, storage : entrypoint * storage) : return =
    match action with
    | Query_price(string)     -> query_price        storage string
    | Receive_price(pair)     -> receive_price      storage pair