import time

import requests
from ontology.rpc.define import *
import json
from ontology.core.transaction import Sig
from ontology.account.account import Account
from ontology.crypto.KeyType import KeyType
from ontology.crypto.SignatureScheme import SignatureScheme
from ontology.common.address import Address
from ontology.crypto.encrypt import get_random_bytes
from ontology.smart_contract.native_contract import asset,ontid
import base64
from binascii import b2a_hex, a2b_hex

rpc_address = "http://polaris1.ont.io:20336"
rest_address = "http://polaris1.ont.io:20334"


class HttpRequest(object):
    _timeout = 10

    @staticmethod
    def set_timeout(timeout=10):
        HttpRequest._timeout = timeout

    @staticmethod
    def request(method, url, payload):
        header = {'Content-type': 'application/json'}
        if method == "post":
            res = requests.post(url, json=payload, headers=header, timeout=HttpRequest._timeout)
            return res
        elif method == "get":
            res = requests.get(url, params=json.dumps(payload), timeout=HttpRequest._timeout)
            return res


class RpcClient(object):
    def __init__(self, qid=0, addr=""):
        self.qid = qid
        self.addr = addr

    def set_address(self, addr):
        self.addr = addr

    def set_json_rpc_version(self, method, param=[]):
        JsonRpcRequest["jsonrpc"] = JSON_RPC_VERSION
        JsonRpcRequest["id"] = "1"
        JsonRpcRequest["method"] = method
        JsonRpcRequest["params"] = param
        return JsonRpcRequest

    def get_version(self) -> str:
        rpc_struct = self.set_json_rpc_version(RPC_GET_VERSION, [])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_block_by_hash(self, hash: str):
        rpc_struct = self.set_json_rpc_version(RPC_GET_BLOCK, [hash, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_block_by_height(self, height):
        rpc_struct = self.set_json_rpc_version(RPC_GET_BLOCK, [height, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_block_count(self):
        rpc_struct = self.set_json_rpc_version(RPC_GET_BLOCK_COUNT)
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_current_block_hash(self):
        rpc_struct = self.set_json_rpc_version(RPC_GET_CURRENT_BLOCK_HASH)
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_block_hash_by_height(self, height):
        rpc_struct = self.set_json_rpc_version(RPC_GET_BLOCK_HASH, [height, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_balance(self, addr):
        rpc_struct = self.set_json_rpc_version(RPC_GET_BALANCE, [addr, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_storage(self, addr, key):
        rpc_struct = self.set_json_rpc_version(RPC_GET_STORAGE, [addr, key, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        s = json.loads(r.content.decode())["result"]
        s = bytearray.fromhex(s)
        res = (s[0]) | (s[1]) << 8 | (s[2]) << 16 | (s[3]) << 24 | (s[4]) << 32 | (s[5]) << 40 | (s[6]) << 48 | (
            s[7]) << 56
        return res

    def get_smart_contract_event_by_txhash(self, tx_hash):
        rpc_struct = self.set_json_rpc_version(RPC_GET_SMART_CONTRACT_EVENT, [tx_hash, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_smart_contract_event_by_block(self, height):
        rpc_struct = self.set_json_rpc_version(RPC_GET_SMART_CONTRACT_EVENT, [height, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_raw_transaction(self, tx_hash):
        rpc_struct = self.set_json_rpc_version(RPC_GET_TRANSACTION, [tx_hash, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_smart_contract(self, contract_addr):
        rpc_struct = self.set_json_rpc_version(RPC_GET_SMART_CONTRACT, [contract_addr, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_generate_block_time(self):
        rpc_struct = self.set_json_rpc_version(RPC_GET_GENERATE_BLOCK_TIME)
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def get_merkle_proof(self, tx_hash):
        rpc_struct = self.set_json_rpc_version(RPC_GET_MERKLE_PROOF, [tx_hash, 1])
        r = HttpRequest.request("post", self.addr, rpc_struct)
        res = json.loads(r.content.decode())["result"]
        return res

    def transfer(self, gas_price: int, gas_limit: int, asset: str, from_account, to_addr, amount: int):
        tx = new_transfer_transaction(gas_price, gas_limit, asset, from_account.get_address().to_array(), to_addr,
                                      amount)
        tx = self.sign_to_transaction(tx, from_account)
        self.send_raw_transaction(tx)
        return tx
    def registry_ontid(self, account: Account,gas_limit: int, gas_price: int):
        did = "did:ont:"+account.get_address_base58()
        print(did)
        tx = new_registry_ontid_transaction( did,account.get_public_key(),gas_limit, gas_price)
        tx = self.sign_to_transaction(tx, account)
        return tx
    def get_ddo(self, did: str):
        tx = new_get_ddo_transaction(did)
        p = Address.decodeBase58("AKFMnJT1u5pyPhzGRuauD1KkyUvqjQsmGs").to_array()
        tx.payer = str(p)
        return tx
    def sign_to_transaction(self, tx, signer: Account):
        tx.payer = signer.get_address().to_array()
        tx_hash = tx.hash256()
        sig_data = signer.generateSignature(tx_hash, SignatureScheme.SHA256withECDSA)
        sig = [Sig([signer.get_public_key()], 1, [sig_data])]
        tx.sigs = sig
        return tx

    def send_raw_transaction(self, tx):
        buf = tx.serialize()
        tx_data = buf.hex()
        rpc_struct = self.set_json_rpc_version(RPC_SEND_TRANSACTION, [tx_data])
        print(rpc_struct)
        r = HttpRequest.request("post", self.addr, rpc_struct)
        print(r.content.decode())
        res = json.loads(r.content.decode())["result"]
        return res
    def send_raw_transaction_preexec(self, tx):
        buf = tx.serialize()
        tx_data = buf.hex()
        rpc_struct = self.set_json_rpc_version(RPC_SEND_TRANSACTION, [tx_data,1])
        print(rpc_struct)
        r = HttpRequest.request("post", self.addr, rpc_struct)
        print(r.content.decode())
        res = json.loads(r.content.decode())["result"]
        if res["State"] == 0:
            print(res)
            raise RuntimeError
        return res["Result"]

if __name__ == '__main__':
    cli = RpcClient(0,rpc_address)
    private_key = "523c5fcf74823831756f0bcb3634234f10b3beb1c05595058534577752ad2d9f"
    acc = Account(private_key, SignatureScheme.SHA256withECDSA)
    print(acc.get_address_base58())
    print(acc.get_public_key().hex())
    if False :
        tx = asset.new_transfer_transaction( "ont", acc.get_address().to_base58(), "AKFMnJT1u5pyPhzGRuauD1KkyUvqjQsmGs",1, 20000, 500)
        tx = cli.sign_to_transaction(tx, acc)
        print(tx.hash256().hex())
        print(tx.serialize().hex())
        cli.send_raw_transaction(tx)
    if False:
        toAddr = Address.decodeBase58("AKFMnJT1u5pyPhzGRuauD1KkyUvqjQsmGs")
        print(toAddr.to_array())
        tx = asset.new_get_balance_transaction("ont", "AKFMnJT1u5pyPhzGRuauD1KkyUvqjQsmGs")
        result = cli.send_raw_transaction_preexec(tx)
        print(result)
    if True:
        did = "did:ont:" + acc.get_address_base58()
        tx = ontid.new_registry_ontid_transaction(did, acc.get_public_key(), 20000, 500)
        tx = cli.sign_to_transaction(tx, acc)
        print(tx.hash256().hex())
        print(tx.serialize().hex())
        cli.send_raw_transaction(tx)
    if False:
        did = "did:ont:"+acc.get_address_base58()
        tx = ontid.new_get_ddo_transaction(did)
        ddo = cli.send_raw_transaction_preexec(tx)
        print(ontid.parse_ddo(did,ddo))
