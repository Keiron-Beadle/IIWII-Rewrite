import discord
from models.brawl import *

BRAWL_ICON = 'https://image.iiwii.app/i/9ce460ae-b734-46c9-9066-7faae667cc96.png'

def brawl_post_game_embed(post_game : BrawlPostGame):
    winner = post_game.get_winner()
    loser = post_game.get_loser()
    winner_pot = post_game.winner_pot.values()
    summed_loser_pot = sum(post_game.loser_pot.values())
    
    if summed_loser_pot == 0:
        voter_winnings_msg = '```md\n# There is no loser pot to share between the winners\n```'
    else:
        voter_winnings_msg = f'```md\n\
            # {summed_loser_pot} copium has been shared between {len(winner_pot)} players\n'
        sorted_winner_pot = sorted(post_game.winner_pot.items(), key=lambda x: x[1], reverse=True)
        for i in range(0,min(len(sorted_winner_pot),5)):
            voter, amount = sorted_winner_pot[i]
            voter_winnings_msg += f'{i}. {voter.display_name} <{amount}>\n'
        voter_winnings_msg += '\n```'

    description = f'{winner.mention} has won and taken **{post_game.brawl_pot//2}** <:copiumcoin:1117202173147750440> from {loser.mention}.\n\n{voter_winnings_msg}'
    embed = discord.Embed(title=post_game.title, 
                        description=description,
                        color=0x7de366)
    embed.set_author(name=winner.display_name, icon_url=winner.avatar.url)
    embed.set_thumbnail(url=BRAWL_ICON)
    return embed

def brawl_started_embed(pre_game : BrawlPreGame):
    embed = discord.Embed(title=pre_game.title, 
                        description=f'{pre_game.player1.mention} and {pre_game.player2.mention} have started a brawl!',
                        color=0x3e5cf0)
    embed.set_author(name=pre_game.player1.display_name, icon_url=pre_game.player1.avatar.url)
   
    embed.add_field(name='Host',value=f'`{pre_game.player1.display_name}`', inline=True)
    embed.add_field(name='Challenger',value=f'`{pre_game.player2.display_name}`', inline=True)
    embed.add_field(name='Brawl Pot', value=f'`  {pre_game.brawl_pot}  `<:copiumcoin:1117202173147750440>', inline=True)
    
    voter_pot = sum(pre_game.player1_pot.values()) + sum(pre_game.player2_pot.values())
    embed.add_field(name='Host Votes', value=f'`  {len(pre_game.player1_pot)}  `', inline=True)
    embed.add_field(name='Challenger Votes', value=f'`  {len(pre_game.player2_pot)}  `', inline=True)
    embed.add_field(name='Voter Pot', value=f'`  {voter_pot}  `<:copiumcoin:1117202173147750440>', inline=True)

    add_voter_pct_field(pre_game, embed, 16)

    embed.set_image(url=pre_game.image)
    embed.set_thumbnail(url=BRAWL_ICON)
    embed.set_footer(text='The host & challenger should use the buttons below to agree who won.')
    return embed

def brawl_request_cancelled_embed(request : BrawlRequest):
    embed = discord.Embed(title=request.title, 
                        description=f'{request.host.mention} has cancelled the brawl.',
                        color=0xf55840)
    embed.set_author(name=request.host.display_name, icon_url=request.host.avatar.url)
    embed.set_thumbnail(url=BRAWL_ICON)
    return embed

def brawl_cancelled_embed(pre_game : BrawlPreGame, canceller : discord.User):
    embed = discord.Embed(title=pre_game.title, 
                        description=f'{canceller.mention} has cancelled the brawl.',
                        color=0xf55840)
    embed.set_author(name=pre_game.player1.display_name, icon_url=pre_game.player1.avatar.url)
    embed.set_thumbnail(url=BRAWL_ICON)
    return embed

def brawl_pre_game_embed(pre_game : BrawlPreGame):
    terms_string = '[Terms]'+('\n'+'\n'.join(pre_game.terms)).replace('\n','\n- ')
    embed = discord.Embed(title=pre_game.title, 
                        description=f"{pre_game.player1.mention} has accepted {pre_game.player2.mention}'s challenge! The pot is `{pre_game.brawl_pot}` <:copiumcoin:1117202173147750440>\n```asciidoc\n{terms_string}\n```",
                        color=0x78e3d8)
    embed.add_field(name='Host',value=f'`{pre_game.player1.display_name}`', inline=True)
    embed.add_field(name='Challenger',value=f'`{pre_game.player2.display_name}`', inline=True)
    embed.add_field(name='\u200b',value='\u200b', inline=True)
    
    add_voter_pct_field(pre_game, embed, 12, True)
    embed.add_field(name='Voter Pot', value=f'`  {sum(pre_game.player1_pot.values()) + sum(pre_game.player2_pot.values())}  `<:copiumcoin:1117202173147750440>', inline=True)

    embed.set_author(name=pre_game.player1.display_name, icon_url=pre_game.player1.avatar.url)
    embed.set_image(url=pre_game.image)
    embed.set_footer(text='The host may start the brawl after 30 seconds to allow for bets!')
    embed.set_thumbnail(url=BRAWL_ICON)
    return embed

def add_voter_pct_field(pre_game : BrawlPreGame, embed : discord.Embed, bars : int, inline : bool = False):
    host_pot = sum(pre_game.player1_pot.values())
    challenger_pot = sum(pre_game.player2_pot.values())

    if host_pot + challenger_pot == 0:
        line_string = '<:WhiteLine:1198295966055407727>'*bars
        embed.add_field(name=f'Vote Distribution',
                value=f'`0%`{line_string}`0%`',
                inline=inline)
        return

    total_pot = max(host_pot + challenger_pot,1)
    host_pot_pct = float(host_pot)/float(total_pot)
    challenger_pot_pct = float(challenger_pot)/float(total_pot)
    rounded_host_pot_pct = round(host_pot_pct*100.0)
    host_pot_bar = '<:BlueLine:1200211417459077171>'*round(host_pot_pct * bars)
    challenger_pot_bar = '<:OrangeLine:1198295959466147900>'*(bars - round(host_pot_pct * bars))
    embed.add_field(name=f'Vote Distribution', 
            value=f'`{rounded_host_pot_pct}%`{host_pot_bar}{challenger_pot_bar}`{round(challenger_pot_pct)}%`',
            inline=inline)

def brawl_created_embed(request : BrawlRequest):
    terms_string = '[Terms]'+('\n'+'\n'.join(request.terms)).replace('\n','\n* ')
    embed = discord.Embed(title=request.title, 
                        description=f'{request.host.mention} is opening a challenge to all players!\n```asciidoc\n{terms_string}\n```',
                        color=0xf0cc59)
    embed.add_field(name='Pot <:copiumcoin:1117202173147750440>', value=f'`  {request.brawl_pot}  `', inline=True)
    embed.set_author(name=request.host.display_name, icon_url=request.host.avatar.url)
    embed.set_footer(text='Join this brawl by clicking the button below!')
    embed.set_image(url=request.image)
    embed.set_thumbnail(url=BRAWL_ICON)
    return embed