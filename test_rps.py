import pytest
from deploy import *
from commit import *

from web3.exceptions import ContractLogicError

NO_GAME = 0
MOVE1 = 1
MOVE2 = 2
REVEAL1 = 3
LATE = 4


def test_deploy_0_delay():
    with pytest.raises(ContractLogicError) as e_info:
         deploy_rps(0, 0)

def test_deploy_1(rps_1_block_delay):
    assert True

def test_happy_flow(rps_1_block_delay, user_1, user_2, key_1, key_2):
    rps = rps_1_block_delay
    user_1_init_balance = rps.functions.balanceOf(user_1).call()
    user_2_init_balance = rps.functions.balanceOf(user_2).call()

    move_1 = 1 # Rock
    move_2 = 2 # Paper

    move_1_hidden = get_commit(move_1, key_1)
    move_2_hidden = get_commit(move_2, key_2)

    game_id = 1

    bet_amount = 50

    assert rps.functions.get_game_state(game_id).call() == NO_GAME

    tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_1})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    user_1_new_balance = rps.functions.balanceOf(user_1).call()
    assert user_1_init_balance - user_1_new_balance == bet_amount

    assert rps.functions.get_game_state(game_id).call() == MOVE1

    tx_hash = rps.functions.make_move(game_id, 0, move_2_hidden).transact({'from': user_2})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    user_2_new_balance = rps.functions.balanceOf(user_2).call()
    assert user_2_init_balance - user_2_new_balance == bet_amount

    assert rps.functions.get_game_state(game_id).call() == MOVE2

    

    tx_hash = rps.functions.reveal_move(game_id, move_1, key_1).transact({'from': user_1})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == REVEAL1


    tx_hash = rps.functions.reveal_move(game_id, move_2, key_2).transact({'from': user_2})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)


    assert rps.functions.get_game_state(game_id).call() == NO_GAME

    assert rps.functions.balanceOf(user_2).call() == user_2_init_balance + bet_amount

    assert rps.functions.balanceOf(user_1).call() == user_1_init_balance - bet_amount

def test_make_move_twice(rps_1_block_delay, user_1, user_2, key_1, key_2):
    rps = rps_1_block_delay
    user_1_init_balance = rps.functions.balanceOf(user_1).call()
    user_2_init_balance = rps.functions.balanceOf(user_2).call()

    move_1 = 1 # Rock
    move_2 = 2 # Paper

    move_1_hidden = get_commit(move_1, key_1)
    move_2_hidden = get_commit(move_2, key_2)

    game_id = 1

    bet_amount = 50

    assert rps.functions.get_game_state(game_id).call() == NO_GAME

    tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_1})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == MOVE1

    
    with pytest.raises(ContractLogicError) as e_info:
        # user 1 cannot make a move again
        tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_1})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == MOVE1
    
    # user 2 can still make a move
    tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_2})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == MOVE2

def test_make_move_third_player(rps_1_block_delay, user_1, user_2, user_3, key_1, key_2):
    rps = rps_1_block_delay
    user_1_init_balance = rps.functions.balanceOf(user_1).call()
    user_2_init_balance = rps.functions.balanceOf(user_2).call()

    move_1 = 1 # Rock
    move_2 = 2 # Paper

    move_1_hidden = get_commit(move_1, key_1)
    move_2_hidden = get_commit(move_2, key_2)

    game_id = 1

    bet_amount = 50

    assert rps.functions.get_game_state(game_id).call() == NO_GAME

    tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_1})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)



    assert rps.functions.get_game_state(game_id).call() == MOVE1
    
    # user 2 can still make a move
    tx_hash = rps.functions.make_move(game_id, bet_amount, move_2_hidden).transact({'from': user_2})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == MOVE2
    
    with pytest.raises(ContractLogicError) as e_info:
        # user 3 cannot make a move
        tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_3})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

def test_users_bet_more_then_they_have(rps_1_block_delay, user_1, user_2, key_1, key_2):
    rps = rps_1_block_delay
    user_1_init_balance = rps.functions.balanceOf(user_1).call()
    user_2_init_balance = rps.functions.balanceOf(user_2).call()

    move_1 = 1 # Rock
    move_2 = 2 # Paper

    move_1_hidden = get_commit(move_1, key_1)
    move_2_hidden = get_commit(move_2, key_2)

    game_id = 1

    bet_amount = user_1_init_balance + 50

    assert rps.functions.get_game_state(game_id).call() == NO_GAME
    
    with pytest.raises(ContractLogicError) as e_info:
        # user 1 cannot make a move again
        tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_1})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == NO_GAME
    
    bet_amount = 50

    tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_1})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == MOVE1

    # empty user 2 balance:
    tx_hash = rps.functions.withdraw(user_2_init_balance).transact({'from': user_2})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    with pytest.raises(ContractLogicError) as e_info:
        tx_hash = rps.functions.make_move(game_id, bet_amount, move_2_hidden).transact({'from': user_2})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == MOVE1

def test_withdraw(rps_1_block_delay, user_1):
    rps = rps_1_block_delay
    user_1_init_balance = rps.functions.balanceOf(user_1).call()

    tx_hash = rps.functions.withdraw(user_1_init_balance // 2).transact({'from': user_1})
    w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.balanceOf(user_1).call() == user_1_init_balance//2

    with pytest.raises(ContractLogicError) as e_info:
        tx_hash = rps.functions.withdraw(user_1_init_balance).transact({'from': user_1})
        w3.eth.wait_for_transaction_receipt(tx_hash)

def test_first_player_can_cancel(rps_1_block_delay, user_1, key_1):
    rps = rps_1_block_delay
    user_1_init_balance = rps.functions.balanceOf(user_1).call()

    move_1 = 1 # Rock

    move_1_hidden = get_commit(move_1, key_1)

    game_id = 1

    bet_amount = 50

    assert rps.functions.get_game_state(game_id).call() == NO_GAME

    tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_1})
    w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == MOVE1
    tx_hash = rps.functions.cancel_game(game_id).transact({'from': user_1})
    w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == NO_GAME

    assert rps.functions.balanceOf(user_1).call() == user_1_init_balance

def test_other_player_cancel(rps_1_block_delay, user_1, user_2, user_3, key_1, key_2):
    rps = rps_1_block_delay
    user_1_init_balance = rps.functions.balanceOf(user_1).call()
    user_2_init_balance = rps.functions.balanceOf(user_2).call()

    move_1 = 1 # Rock
    move_2 = 2 # Paper

    move_1_hidden = get_commit(move_1, key_1)
    move_2_hidden = get_commit(move_2, key_2)

    game_id = 1

    bet_amount = 50

    assert rps.functions.get_game_state(game_id).call() == NO_GAME

    tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_1})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == MOVE1
    

    with pytest.raises(ContractLogicError) as e_info:
        # user 2 cannot cancel
        tx_hash = rps.functions.cancel_game(game_id).transact({'from': user_2})
        w3.eth.wait_for_transaction_receipt(tx_hash)

    tx_hash = rps.functions.make_move(game_id, bet_amount, move_2_hidden).transact({'from': user_2})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Now nobody can cancel:
    with pytest.raises(ContractLogicError) as e_info:
        # user 2 cannot cancel
        tx_hash = rps.functions.cancel_game(game_id).transact({'from': user_2})
        w3.eth.wait_for_transaction_receipt(tx_hash)
    with pytest.raises(ContractLogicError) as e_info:
        # user 1 cannot cancel
        tx_hash = rps.functions.cancel_game(game_id).transact({'from': user_1})
        w3.eth.wait_for_transaction_receipt(tx_hash)

def test_player_invalid_move(rps_1_block_delay, user_1, user_2, user_3, key_1, key_2):
    rps = rps_1_block_delay
    user_1_init_balance = rps.functions.balanceOf(user_1).call()
    user_2_init_balance = rps.functions.balanceOf(user_2).call()

    move_1 = 1 # Rock
    move_2 = 2 # Paper

    move_1_hidden = get_commit(move_1, key_1)
    move_2_hidden = get_commit(move_2, key_2)

    game_id = 1

    bet_amount = 50

    assert rps.functions.get_game_state(game_id).call() == NO_GAME

    tx_hash = rps.functions.make_move(game_id, bet_amount, move_1_hidden).transact({'from': user_1})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    user_1_new_balance = rps.functions.balanceOf(user_1).call()
    assert user_1_init_balance - user_1_new_balance == bet_amount

    assert rps.functions.get_game_state(game_id).call() == MOVE1

    tx_hash = rps.functions.make_move(game_id, 0, move_2_hidden).transact({'from': user_2})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    user_2_new_balance = rps.functions.balanceOf(user_2).call()
    assert user_2_init_balance - user_2_new_balance == bet_amount

    assert rps.functions.get_game_state(game_id).call() == MOVE2

    
    with pytest.raises(ContractLogicError) as e_info:
        # user_1 did not play move_2
        tx_hash = rps.functions.reveal_move(game_id, move_2, key_1).transact({'from': user_1})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert rps.functions.get_game_state(game_id).call() == MOVE2

    with pytest.raises(ContractLogicError) as e_info:
        # user_2 did not use key_1
        tx_hash = rps.functions.reveal_move(game_id, move_2, key_1).transact({'from': user_2})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    with pytest.raises(ContractLogicError) as e_info:
        # user_2 did not use key_1
        tx_hash = rps.functions.reveal_move(game_id, move_1, key_1).transact({'from': user_2})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)