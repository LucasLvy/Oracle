import { InMemorySigner } from '@taquito/signer';
import { TezosToolkit, MichelsonMap } from '@taquito/taquito';
import oracle from './Oracle.json';
import client from './Client.json';


const rpc = "https://hangzhounet.smartpy.io/"
const pk: string = "";
const Tezos = new TezosToolkit(rpc);
const signer = new InMemorySigner(pk);
Tezos.setProvider({ signer: signer })

async function origOracle() {
    const store = {
        admin : "tz1c6PPijJnZYjKiSQND4pMtGMg6csGeAiiF",
        counter : 0,
        prices : new MichelsonMap(),
        whitelist : ["tz1c6PPijJnZYjKiSQND4pMtGMg6csGeAiiF"],
        requests : new MichelsonMap(),
        request_price : 1000,
        supported_pairs : ['ETHBTC']
    }

    try {
        const originated = await Tezos.contract.originate({
            code: oracle,
            storage: store,
        })
        console.log(`Waiting for oracle ${originated.contractAddress} to be confirmed...`);
        await originated.confirmation(2);
        console.log('confirmed oracle: ', originated.contractAddress);
        await origClient(originated.contractAddress)

    } catch (error: any) {
        console.log(error)
    }
}
async function origClient(oracleAdd?: string) {
    const pair = {
        update_time: new Date(),
        open_time: new Date(),
        close_time: new Date(),
        last_price: 10,
        high_price: 10,
        low_price: 10,
        volume: 10,
        quote_volume: 10,
        pair: "ETHBTC"
    }
    const store = {
        'oracle_address' : oracleAdd || "",
        'pair' : pair,
        'query_price' : 1000,
    }

    try {
        const originated = await Tezos.contract.originate({
            code: client,
            storage: store,
        })
        console.log(`Waiting for client ${originated.contractAddress} to be confirmed...`);
        await originated.confirmation(2);
        console.log('confirmed client: ', originated.contractAddress);
    } catch (error: any) {
        console.log(error)
    }
}

origOracle();