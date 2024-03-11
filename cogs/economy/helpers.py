import time
from cogs.economy import cache
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
    balance = cache.get_user_balance(user_id, guild_id)
    if balance:
        return balance
    db_entry = db.select_one(queries.GET_ECONOMY, (user_id, guild_id))
    if not db_entry:
        balance = insert_user(user_id, guild_id)
    else:
        balance = Balance(db_entry[0],db_entry[1],db_entry[2],db_entry[3])
    cache.update_user_balance(user_id, guild_id, balance)
    return balance

def get_user_currency(balance, currency) -> int:
    if currency.lower() == 'copium':
        return balance.copium
    return 0

def admin_take(user_id, guild_id, amount, currency):
    user_balance = get_user_balance(user_id, guild_id)
    checked_amount = min(user_balance.copium, amount)
    user_balance.copium -= checked_amount
    user_balance.transactions.append(Transaction(time.time(), 'pay', 1198446442013003889, currency, checked_amount))
    user_transactions = Transaction.join_transactions(user_balance.transactions)
    user_transactions = BALANCE_JSON.replace('{}',f'{{{user_transactions}}}')
    db.execute(queries.UPDATE_ECONOMY, (user_balance.copium, user_transactions, user_id, guild_id))
    cache.update_user_balance(user_id, guild_id, user_balance)

def admin_pay(receiver_id, guild_id, amount, currency):
    receiver_balance = get_user_balance(receiver_id, guild_id)
    receiver_balance.copium += amount
    receiver_balance.transactions.append(Transaction(time.time(), 'receive', 1198446442013003889, currency, amount))
    receiver_transactions = Transaction.join_transactions(receiver_balance.transactions)
    receiver_transactions = BALANCE_JSON.replace('{}',f'{{{receiver_transactions}}}')
    db.execute(queries.UPDATE_ECONOMY, (receiver_balance.copium, receiver_transactions, receiver_id, guild_id))
    cache.update_user_balance(receiver_id, guild_id, receiver_balance)

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
    cache.update_user_balance(sender_id, guild_id, sender_balance)
    cache.update_user_balance(receiver_id, guild_id, receiver_balance)