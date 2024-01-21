import time, json, discord
import database.mariadb as db
from models.balance import Balance, Transaction
import cogs.economy.database_queries as queries
from cogs.economy.exceptions import NotEnoughMoney
   
BALANCE_JSON = '{"transactions":{}}'

def insert_user(user_id, guild_id) -> Balance:
    STARTING_COPIUM = 100
    db.execute(queries.INSERT, (user_id, guild_id, STARTING_COPIUM, BALANCE_JSON))
    return Balance(user_id, guild_id, STARTING_COPIUM, BALANCE_JSON)

def get_user_balance(user_id, guild_id) -> Balance:
    balance = db.select_one(queries.GET_ECONOMY, (user_id,guild_id))
    if not balance:
        return insert_user(user_id, guild_id)
    return Balance(balance[0], balance[1], balance[2], balance[3])

def get_user_currency(balance, currency) -> int:
    if currency.lower() == 'copium':
        return balance.copium
    return 0

def pay(sender_id, receiver_id, guild_id, amount, currency):
    sender_balance = get_user_balance(sender_id, guild_id)
    receiver_balance = get_user_balance(receiver_id, guild_id)
    if sender_balance.copium < amount:
        raise NotEnoughMoney
    sender_balance.copium -= amount
    receiver_balance.copium += amount
    sender_balance.transactions.append(Transaction(time.time(), 'pay', receiver_id, currency, amount))
    receiver_balance.transactions.append(Transaction(time.time(), 'receive', sender_id, currency, amount))
    sender_transactions = Transaction.join_transactions(sender_balance.transactions)
    receiver_transactions = Transaction.join_transactions(receiver_balance.transactions)
    sender_transactions = BALANCE_JSON.replace('{}',f'{{{sender_transactions}}}')
    receiver_transactions = BALANCE_JSON.replace('{}',f'{{{receiver_transactions}}}')
    db.execute(queries.UPDATE_ECONOMY, (sender_balance.copium, sender_transactions, sender_id, guild_id))
    db.execute(queries.UPDATE_ECONOMY, (receiver_balance.copium, receiver_transactions, receiver_id, guild_id))