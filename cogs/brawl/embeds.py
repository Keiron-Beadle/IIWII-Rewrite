import discord
from models.brawl import BrawlRequest

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