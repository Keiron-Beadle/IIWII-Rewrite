from discord import Embed, Colour, Member, Guild
from models.balance import Balance, Transaction
import time

COLOURS = {
    'pay': Colour.green(),
    'balance': Colour.blue()
}

MAX_NAME_LENGTH = 15
COPIUM_EMOJI = '<:copiumcoin:1117202173147750440>'
WALLET_ICON_URL = 'https://image.iiwii.app/i/b004bcbd-d2d3-4717-8295-31231e850bd8.png'

def cap_name(name : str) -> str:
    capped_name = name[:MAX_NAME_LENGTH-3] + '...' if len(name) > MAX_NAME_LENGTH else name
    return capped_name.ljust(MAX_NAME_LENGTH, ' ')

def make_balance(user : Member, guild : Guild, balance : Balance):
    embed = Embed(title=f'Wallet', colour=COLOURS['balance'])
    embed.set_author(name=f'{user.display_name}', icon_url=f'{user.display_avatar.url}')
    embed.set_thumbnail(url=WALLET_ICON_URL)
    embed.add_field(name=f'> {COPIUM_EMOJI} {balance.balance}', value='\u200b', inline=True)
    embed.set_footer(text=f"Guild: {guild.name}")
    return embed

def make_pay(payer : Member, payee : Member, amount : int, guild : Guild):
    pass