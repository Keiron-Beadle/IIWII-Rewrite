import json

class Transaction:
    def __init__(self, time, type, other_user, currency, amount):
        self.time = int(time)
        self.type = type
        self.other_user = other_user
        self.currency = currency
        self.amount = int(amount)

    def __str__(self):
        return '"%s":{"type":"%s","other_user":"%s","currency":"%s","amount":%s}' % (self.time, self.type, self.other_user, self.currency, self.amount)
    
    @classmethod
    def join_transactions(cls, transactions):
        return ','.join(str(transaction) for transaction in transactions)

def transaction_decoder(obj) -> list[Transaction]:
    if 'transactions' in obj and isinstance(obj['transactions'], dict):
        transactions = []
        for time, details in obj['transactions'].items():
            transaction = Transaction(time, details.get('type'), details.get('other_user'), details.get('currency'), details.get('amount'))
            transactions.append(transaction)
        return transactions
    return obj

class Balance:
    def __init__(self, id, guild_id, copium, transactions):
        self.id = id
        self.guild_id = guild_id
        self.copium = copium
        self.transactions = json.loads(transactions, object_hook=transaction_decoder)
