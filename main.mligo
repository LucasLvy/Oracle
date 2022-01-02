#import "partials/methods.mligo" "ORACLE"

let main (action, storage : ORACLE.entrypoint * ORACLE.storage) : ORACLE.return =
    match action with
    | Harvest_xtz(user)             -> ORACLE.harvest_xtz               storage user
    | Change_request_price(tez)     -> ORACLE.change_request_price      storage tez
    | Whitelist_user(user)          -> ORACLE.whitelist_user            storage user
    | Blacklist_user(user)          -> ORACLE.blacklist_user            storage user
    | Whitelist_pair(pair)          -> ORACLE.whitelist_pair            storage pair
    | Blacklist_pair(pair)          -> ORACLE.blacklist_pair            storage pair
    | Set_admin(user)               -> ORACLE.set_admin                 storage user
    | Get_price(value)              -> ORACLE.get_price                 storage value
    | Update(value)                 -> ORACLE.update                    storage value