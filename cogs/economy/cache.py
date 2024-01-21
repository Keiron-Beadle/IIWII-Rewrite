from typing import Optional
from models.balance import Balance

USER_BALANCES = {}

def update_user_balance(user_id, guild_id, balance : Balance):
    USER_BALANCES[(user_id, guild_id)] = balance

def get_user_balance(user_id : int, guild_id : int) -> Optional[Balance]:
    return USER_BALANCES.get((user_id, guild_id))