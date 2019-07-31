#!/usr/bin/env python3
"""
@summary: testing send.py

@version: v46 (03/January/2019)
@since:   1/December/2018
@organization: 
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer for updates
"""

import hammer.deploy as deploy
import hammer.send as send
import os
import json
from pprint import pprint
from web3.utils import datatypes

# web3 connection and nodetype
from hammer.config import RPCaddress, FILE_CONTRACT_SOURCE, FILE_LAST_EXPERIMENT
from hammer.clienttools import web3connection
answer = web3connection(RPCaddress=RPCaddress)
global w3, NODENAME, NODETYPE, NODEVERSION, CONSENSUS, NETWORKID, CHAINNAME, CHAINID
w3, chainInfos = answer
NODENAME, NODETYPE, NODEVERSION, CONSENSUS, NETWORKID, CHAINNAME, CHAINID = chainInfos

deploy.w3 = send.w3 = w3

# current path one up?
# unfortunately path if different depending on how py.test is called
path = os.path.abspath(os.curdir)
if os.path.split(path)[-1] == "tests":
    os.chdir("..")


# fixture: create a contract that every test here can be using
solfile = os.path.join("hammer", FILE_CONTRACT_SOURCE)
_, interface, address = deploy.contract_CompileDeploySave(solfile)
contract = deploy.contractObject(address, interface["abi"])
abi = interface["abi"]


def test_initialize_fromAddress():
    contract = send.initialize_fromAddress()
    print(contract)
    assert ("%s" % contract).startswith(
        "<web3.utils.datatypes.Contract object")


def test_contract_set_via_web3():
    latitude = 4624644
    longitude = 1435776
    direction = 0
    speed = 232
    acceleration = 1
    stored = send.try_contract_set_via_web3(
        contract, latitude, longitude, direction, speed, acceleration)


def test_contract_method_ID():
    methodname = "get"
    answer = send.contract_method_ID(methodname, abi)
    print(answer)
    assert answer == "0x6d4ce63c"


def test_argument_encoding():
    # TODO: make this "set" flexible for any method name
    method_ID = send.contract_method_ID("set", abi)
    data = send.argument_encoding(method_ID, arg=42)
    print(data)
    assert data == "0x60fe47b1000000000000000000000000000000000000000000000000000000000000002a"


def test_contract_set_via_RPC():
    arg = 1001
    tx = send.contract_set_via_RPC(contract, arg=arg)
    print(tx)
    assert tx.startswith("0x")
    tx_receipt = w3.eth.waitForTransactionReceipt(tx)
    stored = contract.functions.get().call()
    assert arg == stored


def assert_ReturnedTransactionsOK(txs, numTx):
    print(txs)
    assert len(txs) == numTx
    assert txs[0].startswith("0x")
    assert txs[numTx-1].startswith("0x")


def test_many_transactions_consecutive():
    numTx = 10
    txs = send.many_transactions_consecutive(contract, numTx)
    assert_ReturnedTransactionsOK(txs, numTx)


def test_many_transactions_threaded():
    numTx = 10
    txs = send.many_transactions_threaded(contract, numTx=numTx)
    assert_ReturnedTransactionsOK(txs, numTx)


def test_many_transactions_threaded():
    numTx = 10
    txs = send.many_transactions_threaded_Queue(
        contract, numTx=numTx, num_worker_threads=3)
    assert_ReturnedTransactionsOK(txs, numTx)


def test_many_transactions_threaded_in_batches():
    numTx = 10
    txs = send.many_transactions_threaded_in_batches(
        contract, numTx=numTx, batchSize=3)
    assert_ReturnedTransactionsOK(txs, numTx)


def test_controlSample_transactionsSuccessful():
    numTx = 10
    txs = send.many_transactions_consecutive(contract, numTx)
    success = send.controlSample_transactionsSuccessful(
        txs, sampleSize=15, timeout=30)
    assert success


def test_when_last_ones_mined__give_range_of_block_numbers():
    numTx = 10
    txs = send.many_transactions_consecutive(contract, numTx)
    block_from, block_to = send.when_last_ones_mined__give_range_of_block_numbers(
        txs)
    assert block_from <= block_to


def setGlobalVariables():
    send.NODENAME = NODENAME
    send.NODETYPE = NODETYPE
    send.NODEVERSION = NODEVERSION
    send.CONSENSUS = CONSENSUS
    send.NETWORKID = NETWORKID
    send.CHAINNAME = CHAINNAME
    send.CHAINID = CHAINID


def test_store_experiment_data():
    setGlobalVariables()

    dummy = "not real, file created by tests/test_send.py"
    data = {"send": {
        "block_first": 1, "block_last": 2, "empty_blocks": 3,
        "num_txs": dummy,
        "sample_txs_successful": False}
    }
    send.store_experiment_data(
        success=False, num_txs=dummy, block_from=1, block_to=2, empty_blocks=3)
    with open(FILE_LAST_EXPERIMENT, "r") as f:
        data2 = json.load(f)
    assert data["send"] == data2["send"]


def test_wait_some_blocks():
    send.wait_some_blocks(waitBlocks=0)


def test_check_CLI_or_syntax_info_and_exit():
    try:
        send.check_CLI_or_syntax_info_and_exit()
    except SystemExit:
        pass


def test_sendmany_HowtoTestThisNoIdea():
    # answer = send.sendmany()
    # how to test this? Please make suggestions
    pass
