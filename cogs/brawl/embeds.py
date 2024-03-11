import discord
from models.brawl import *

def brawl_post_game_embed(post_game : BrawlPostGame):
    embed = discord.Embed(title=post_game.winner.display_name, 
                        description=f'{post_game.winner.mention} has won the brawl and taken `{post_game.brawl_pot}`<:copiumcoin:1117202173147750440>.',
                        color=0x50ad3e)
    embed.add_field(name='Winner Pot <:copiumcoin:1117202173147750440>', value=f'`  {sum(post_game.winner_pot.values())}  `', inline=True)
    embed.set_author(name=post_game.winner.display_name, icon_url=post_game.winner.avatar.url)
    return embed

def brawl_started_embed(pre_game : BrawlPreGame):
    embed = discord.Embed(title=pre_game.title, 
                        description=f'{pre_game.player1.mention} and {pre_game.player2.mention} have started a brawl! The pot is `{pre_game.brawl_pot}` <:copiumcoin:1117202173147750440>.',
                        color=0x50ad3e)
    embed.set_author(name=pre_game.player1.display_name, icon_url=pre_game.player1.avatar.url)
    embed.add_field(name='Host',value=f'`{pre_game.player1.display_name}`', inline=True)
    embed.add_field(name='Challenger',value=f'`{pre_game.player2.display_name}`', inline=True)
    embed.add_field(name='Pot <:copiumcoin:1117202173147750440>', value=f'`  {pre_game.brawl_pot}  `', inline=True)
    embed.set_image(url=pre_game.image)
    embed.set_footer(text='The host & challenger should use the buttons below to agree who won.')
    return embed

def brawl_request_cancelled_embed(request : BrawlRequest):
    embed = discord.Embed(title=request.title, 
                        description=f'{request.host.mention} has cancelled the brawl.',
                        color=0xe74c3c)
    embed.set_author(name=request.host.display_name, icon_url=request.host.avatar.url)
    return embed

def brawl_cancelled_embed(pre_game : BrawlPreGame, canceller : discord.User):
    embed = discord.Embed(title=pre_game.title, 
                        description=f'{canceller.mention} has cancelled the brawl.',
                        color=0xe74c3c)
    embed.set_author(name=pre_game.player1.display_name, icon_url=pre_game.player1.avatar.url)
    return embed

def brawl_pre_game_embed(pre_game : BrawlPreGame):
    terms_string = '[Terms]'+('\n'+'\n'.join(pre_game.terms)).replace('\n','\n* ')
    embed = discord.Embed(title=pre_game.title, 
                        description=f"{pre_game.player1.mention} has accepted {pre_game.player2.mention}'s challenge!\n```asciidoc\n{terms_string}\n```",
                        color=0xdbbd38)
    embed.add_field(name='Host',value=f'`{pre_game.player1.display_name}`', inline=True)
    embed.add_field(name='Challenger',value=f'`{pre_game.player2.display_name}`', inline=True)
    embed.add_field(name='Pot <:copiumcoin:1117202173147750440>', value=f'`  {pre_game.brawl_pot}  `', inline=True)
    
    host_pot = sum(pre_game.player1_pot.values())
    challenger_pot = sum(pre_game.player2_pot.values())
    total_pot = max(host_pot + challenger_pot,1)
    host_pot_pct = float(host_pot)/float(total_pot)
    challenger_pot_pct = float(challenger_pot)/float(total_pot)
    rounded_host_pot_pct = round(host_pot_pct*100.0)
    num_of_bars = 16
    host_pot_bar = '<:BlueLine:1200211417459077171>'*round(host_pot_pct * num_of_bars)
    challenger_pot_bar = '<:OrangeLine:1198295959466147900>'*(num_of_bars - round(host_pot_pct * num_of_bars))
    embed.add_field(name='Voter Pot', value=f'`{rounded_host_pot_pct}%`{host_pot_bar}{challenger_pot_bar}`{100-rounded_host_pot_pct}%`', inline=False)

    embed.set_author(name=pre_game.player1.display_name, icon_url=pre_game.player1.avatar.url)
    embed.set_image(url=pre_game.image)
    embed.set_footer(text='The host may start the brawl after 30 seconds to allow for bets!')
    return embed

def brawl_created_embed(request : BrawlRequest):
    terms_string = '[Terms]'+('\n'+'\n'.join(request.terms)).replace('\n','\n* ')
    embed = discord.Embed(title=request.title, 
                        description=f'{request.host.mention} is opening a challenge to all players!\n```asciidoc\n{terms_string}\n```',
                        color=0x50ad3e)
    embed.add_field(name='Pot <:copiumcoin:1117202173147750440>', value=f'`  {request.brawl_pot}  `', inline=True)
    embed.set_author(name=request.host.display_name, icon_url=request.host.avatar.url)
    embed.set_footer(text='Join this brawl by clicking the button below!')
    embed.set_image(url=request.image)
    return embed