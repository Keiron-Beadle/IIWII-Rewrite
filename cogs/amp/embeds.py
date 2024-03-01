import discord, re
from models.amp import ADSInstanceData

POSSIBLE_ADDRESS_FIELDS = ['Minecraft Server Address', 'Application Address', 'Game Address']
 
def find_current_players(instance):
    if instance.Metrics:
        return instance.Metrics['Active Users'].RawValue
    return None

def find_max_players(instance):
    if instance.Metrics:
        return instance.Metrics['Active Users'].MaxValue
    return None

def find_port(instance):
    for endpoint in instance.ApplicationEndpoints:
        if endpoint.DisplayName in POSSIBLE_ADDRESS_FIELDS:
            return endpoint.Endpoint.split(':')[1]
    return None

def server_list(user : discord.User, instances : ADSInstanceData):
    embed = discord.Embed(
        title='Server List', 
        description='The IP for all of the server is: **amp.iiwii.app:PORT**. The port will vary between servers.',
        color=discord.Color.blue()
    )
    embed.set_author(name = user.display_name, icon_url=user.avatar.url)
    
    for instance in instances.iterate_instances():
        status_emoji = '<:Up:1198118104006398066>' if instance.Running else '<:Down:1198118101779238933>'
        port = find_port(instance)
        current_players = find_current_players(instance)
        max_players = find_max_players(instance)
        
        player_count_str = '0/0' if not current_players or not max_players else f'{current_players}/{max_players}'
        status_body = f'```ansi\n[0;2m[0;31m[+][0m Port: {port}\n[0;31m[+][0m Online: {player_count_str}[0m[2;37m[0m\n```' \
                    if not instance.Running else f'```ansi\n[2;32m[2;36m[2;32m[+][0m[2;36m[0m[2;32m[0m Port: {port}\n[2;32m[+][0m Online: {player_count_str}\n```'
        formatted_name = re.sub(r'(?<=.)([A-Z])', r' \1', instance.FriendlyName)
        embed.add_field(name=f'{status_emoji} {formatted_name}', value=f'{status_body}', inline=True)

    if len(instances) % 3 == 2:
        embed.add_field(name='\u200b', value='\u200b', inline=True)
    elif len(instances) % 3 == 1:
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)

    # Add memory usage line
    ram_percentage = (instances.used_ram / instances.installed_ram)
    ram_chart = ''
    if ram_percentage > 0.75:
        line_emoji = '<:RedLine:1198295963706597376>'
    elif ram_percentage > 0.4:
        line_emoji = '<:OrangeLine:1198295959466147900>'
    else:
        line_emoji = '<:GreenLine:1198295961873682464>'

    subdivision = 20
    line_count = max(int(ram_percentage * subdivision), 1)
    empty_count = subdivision - line_count
    line_emojis = line_emoji * line_count
    empty_emojis = '<:WhiteLine:1198295966055407727>' * empty_count
    ram_chart = line_emojis + empty_emojis
    embed.add_field(name="Memory Usage", value=f"{ram_chart}`[{int(ram_percentage*100)}%]`", inline=False)
    return embed