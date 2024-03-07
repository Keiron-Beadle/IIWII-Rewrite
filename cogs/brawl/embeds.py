import discord
from models.brawl import *

def brawl_pre_game_embed(pre_game : BrawlPreGame):
    terms_string = '[Terms]'+('\n'+'\n'.join(pre_game.terms)).replace('\n','\n* ')
    embed = discord.Embed(title=pre_game.title, 
                        description=f"{pre_game.player2.mention} has accepted {pre_game.player1.mention}'s challenge!\n```asciidoc\n{terms_string}\n```",
                        color=0xdbbd38)
    embed.add_field(name='<:copiumcoin:1117202173147750440>', value=f'`  {pre_game.brawl_pot}  `', inline=True)
    embed.add_field(name='Opponent', value=f'`  {pre_game.player2.mention}  `',inline=True)
    embed.set_author(name=pre_game.player1.display_name, icon_url=pre_game.player1.avatar.url)
    embed.set_image(url=pre_game.image)
    embed.set_footer(text='The host may start the brawl after 30 seconds to allow for bets!')
    return embed

def brawl_created_embed(request : BrawlRequest):
    terms_string = '[Terms]'+('\n'+'\n'.join(request.terms)).replace('\n','\n* ')
    embed = discord.Embed(title=request.title, 
                        description=f'{request.host.mention} is opening a challenge to all players!\n```asciidoc\n{terms_string}\n```',
                        color=0x50ad3e)
    embed.add_field(name='<:copiumcoin:1117202173147750440>', value=f'`  {request.brawl_pot}  `', inline=True)
    embed.add_field(name='Opponent', value='`  None  `',inline=True)
    embed.set_author(name=request.host.display_name, icon_url=request.host.avatar.url)
    embed.set_footer(text='Join this brawl by clicking the button below!')
    embed.set_image(url=request.image)
    return embed