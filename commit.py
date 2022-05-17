from hexbytes import HexBytes
from web3 import Web3
import secrets


def get_commit(data: int, key: HexBytes) -> HexBytes:
    return HexBytes(Web3.solidityKeccak(['int256', 'bytes32'], [data, key]))

def gen_key():
    return HexBytes(secrets.token_bytes(32))
