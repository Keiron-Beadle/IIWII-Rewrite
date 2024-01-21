from typing import Optional
import database.mariadb as db
from models.balance import Balance
import cogs.economy.database_queries as queries

def insert_user(user_id, guild_id) -> Balance:
    STARTING_COPIUM = 100
    BALANCE_JSON = '{"transactions":{}}'
    db.execute(queries.INSERT, (user_id, guild_id, STARTING_COPIUM, BALANCE_JSON))
    return Balance(user_id, guild_id, STARTING_COPIUM, BALANCE_JSON)

def get_user_balance(user_id, guild_id) -> Balance:
    balance = db.select_one(queries.GET_ECONOMY, (user_id,guild_id))
    if not balance:
        return insert_user(user_id, guild_id)
    return Balance(balance[0], balance[1], balance[2], balance[3])