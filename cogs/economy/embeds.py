from discord import Embed, Colour, Member, Guild
from models.balance import Balance, Transaction
import time

COLOURS = {
    'pay': Colour.green(),
    'balance': Colour.blue()
}

EMOJIS = {
    "copium" : "<:copiumcoin:1117202173147750440>",
}

MAX_NAME_LENGTH = 15
WALLET_ICON_URL = 'https://image.iiwii.app/i/b004bcbd-d2d3-4717-8295-31231e850bd8.png'
PAYMENT_ICON_URL = 'https://image.iiwii.app/i/87de663f-b010-4f1c-9292-4c5e378cc6fc.png'

def cap_name(name : str) -> str:
    capped_name = name[:MAX_NAME_LENGTH-3] + '...' if len(name) > MAX_NAME_LENGTH else name
    return capped_name.ljust(MAX_NAME_LENGTH, ' ')

def make_balance(user : Member, guild : Guild, amount : int) -> Embed:
    embed = Embed(title=f'Wallet', colour=COLOURS['balance'])
    embed.set_author(name=f'{user.display_name}', icon_url=f'{user.display_avatar.url}')
    embed.set_thumbnail(url=WALLET_ICON_URL)
    embed.add_field(name=f'> {EMOJIS["copium"]} {amount}', value='\u200b', inline=True)
    embed.set_footer(text=f"Guild: {guild.name}")
    return embed

def make_pay(sender : Member, receiver : Member, amount : int, guild : Guild, currency : str = "Copium") -> Embed:
    embed = Embed(title=f'Payment', colour=COLOURS['pay'])
    embed.set_author(name=f'{sender.display_name}', icon_url=f'{sender.display_avatar.url}')
    embed.set_thumbnail(url=PAYMENT_ICON_URL)
    embed.set_footer(text=f"Guild: {guild.name}")

    sender_name = cap_name(sender.display_name)
    receiver_name = cap_name(receiver.display_name)

    if len(sender_name) > len(receiver_name):
        padding = (len(sender_name) - len(receiver_name)) // 2
        receiver_name = receiver_name.rjust(len(receiver_name) + padding)
        receiver_name = receiver_name.ljust(len(sender_name))
    elif len(receiver_name) > len(sender_name):
        padding = (len(receiver_name) - len(sender_name)) // 2
        sender_name = sender_name.rjust(len(sender_name) + padding)
        sender_name = sender_name.ljust(len(receiver_name))

    emoji = EMOJIS[currency.lower()]
    embed.add_field(name='Sender', value=f'{sender_name}')
    embed.add_field(name=f'<a:rightarrow:1115071589449482300>', value=f'{emoji}\n\u200b {amount}')
    receiver_title = '\u200b' + 'Receiver'.rjust(len(receiver_name)+14)
    embed.add_field(name=receiver_title, value=f'{receiver_name}')
    return embed