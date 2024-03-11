import time
from models.balance import Balance
from discord import Embed, Colour, Member, Guild

COLOURS = {
    'pay': Colour.green(),
    'balance': Colour.blue()
}

EMOJIS = {
    "copium" : "<:copiumcoin:1117202173147750440>",
}

MAX_NAME_LENGTH = 15
WALLET_ICON_URL = 'https://image.iiwii.app/i/b004bcbd-d2d3-4717-8295-31231e850bd8.png'
PAYMENT_ICON_URL = 'https://image.iiwii.app/i/39d8aff2-dd0a-40d9-bffa-8289ba38ce3e.png'

def cap_name(name : str, alignment : str) -> str:
    capped_name = name[:MAX_NAME_LENGTH-3] + '...' if len(name) > MAX_NAME_LENGTH else name
    if alignment.lower() == 'left':
        return capped_name.ljust(MAX_NAME_LENGTH, ' ')
    elif alignment.lower() == 'right':
        return capped_name.rjust(MAX_NAME_LENGTH, ' ')
    return capped_name

def make_balance(user : Member, guild : Guild, amount : float) -> Embed:
    embed = Embed(title=f'Wallet', colour=COLOURS['balance'])
    embed.set_author(name=f'{user.display_name}', icon_url=f'{user.display_avatar.url}')
    embed.set_thumbnail(url=WALLET_ICON_URL)
    embed.add_field(name=f'> {EMOJIS["copium"]} {amount:.2f}', value='\u200b', inline=True)
    embed.set_footer(text=f"Guild: {guild.name}")
    return embed

def get_transaction_body(user : Member, balance : Balance, start : int = 0, show_iiwii_transactions : bool = False) -> str:
    transaction_body = ''
    transactions = balance.transactions
    if not show_iiwii_transactions:
        transactions = [transaction for transaction in transactions if transaction.other_user != '1198446442013003889']
    if start > len(transactions):
        return transaction_body
    for i in range(start, min(start + 10, len(transactions))):
        transaction = transactions[i]
        other_user = user.guild.get_member(int(transaction.other_user))
        other_user_name = other_user.display_name if other_user else '[Deleted User]'
        if transaction.type == 'pay':
            transaction_body += f'`{time.ctime(transaction.time)}` - Paid {transaction.amount:.2f} {EMOJIS[transaction.currency.lower()]} to {other_user_name}\n'
        elif transaction.type == 'receive':
            transaction_body += f'`{time.ctime(transaction.time)}` - Received {transaction.amount:.2f} {EMOJIS[transaction.currency.lower()]} from {other_user_name}\n'
    return transaction_body

def make_full_balance(user : Member, guild : Guild, balance : Balance, start_transasction : int = 0, show_iiwii_transactions : bool = True) -> Embed:
    embed = make_balance(user, guild, balance.copium)
    transaction_body = get_transaction_body(user, balance, start_transasction, show_iiwii_transactions)
    embed.add_field(name='Transactions', value=transaction_body, inline=False)
    return embed

def make_pay(sender : Member, receiver : Member, amount : float, guild : Guild, currency : str = "Copium") -> Embed:
    embed = Embed(title=f'Payment', colour=COLOURS['pay'])
    embed.set_author(name=f'{sender.display_name}', icon_url=f'{sender.display_avatar.url}')
    embed.set_thumbnail(url=PAYMENT_ICON_URL)
    embed.set_footer(text=f"Guild: {guild.name}")
    sender_name = cap_name(sender.display_name, 'left')
    receiver_name = cap_name(receiver.display_name, 'right')
    emoji = EMOJIS[currency.lower()]
    embed.add_field(name='Sender', value=f'```ansi\n\u001b[1;37m{sender_name}\n```')
    embed.add_field(name=f'<a:rightarrow:1115071589449482300>', value=f'{emoji}\n\u200b {amount:.2f}')
    receiver_title = '\u200b' + 'Receiver'.rjust(len(receiver_name)+14)
    embed.add_field(name=receiver_title, value=f'```ansi\n\u001b[1;37m{receiver_name}\n```')
    return embed