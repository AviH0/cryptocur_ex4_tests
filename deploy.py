from web3 import Web3
import solcx  # type: ignore
from typing import Any
import pytest
from commit import *

GANACHE_PORT = 7545


# run the line below to install the compiler ->  only once is needed.
solcx.install_solc(version='latest')


def compile(file_name: str) -> Any:
    # set the version
    solcx.set_solc_version('0.8.14')

    # compile
    compiled_sol = solcx.compile_files(
        [file_name], output_values=['abi', 'bin'])

    # retrieve the contract interface
    contract_id, contract_interface = compiled_sol.popitem()
    return contract_interface['bin'], contract_interface['abi']


bytecode, abi = compile("RPS.sol")


# Connect to the blockchain: (Ganache should be running at this port)
w3 = Web3(Web3.HTTPProvider(f"http://127.0.0.1:{GANACHE_PORT}"))


def deploy_rps(account_number, reveal_delay):
    # deploy the contract
    RPS = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Submit the transaction that deploys the contract. It is deployed by accounts[0] which is the first of the 10 pre-made accounts created by ganache.
    tx_hash = RPS.constructor(reveal_delay).transact(
        {'from': w3.eth.accounts[account_number]})
    # Wait for the transaction to be mined, and get the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # get a contract instance
    rps = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
    return rps

@pytest.fixture
def rps_1_block_delay():
    rps =  deploy_rps(0, 1)
    for i in range(10):
        tx_hash = w3.eth.send_transaction({
        'to': rps.address,
        'from': w3.eth.accounts[i],
        'value': 10**16
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return rps

@pytest.fixture
def rps_5_block_delay():
    rps = deploy_rps(0, 5)
    for i in range(10):
        tx_hash = w3.eth.send_transaction({
        'to': rps.address,
        'from': w3.eth.accounts[i],
        'value': 10**16
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return rps

@pytest.fixture
def user_1():
    return w3.eth.accounts[1]

@pytest.fixture
def user_2():
    return w3.eth.accounts[2]

@pytest.fixture
def user_3():
    return w3.eth.accounts[3]

@pytest.fixture
def key_1():
    return gen_key()

@pytest.fixture
def key_2():
    return gen_key()

