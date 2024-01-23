from discord import Colour

class Role:
    def __init__(self, guild_id, name, colour, emoji, group):
        self.guild_id = guild_id
        self.name = name
        self.colour : Colour = Colour.from_str(colour)
        self.emoji = emoji
        self.group = group

    @classmethod
    def to_str(cls, role):
        return f'{role.name}\u2a0a{role.colour}\u2a0a{role.emoji}\u2a0a{role.group}'

    @classmethod
    def list_to_str(cls, roles):
        str = '\u2800'
        for role in roles:
            str += f'{role.guild_id}\u2a0a{role.name}\u2a0a{role.colour}\u2a0a{role.emoji}\u2a0a{role.group}'
        return str + '\u200b'
    
    @classmethod
    def str_to_list(cls, str):
        ret = []
        if str == '\u2800\u200b':
            return ret
        for role in str.split('\u2800')[1:]:
            guild_id, name, colour, emoji, group = role.split('\u2a0a')
            ret.append(Role(int(guild_id), name, colour, emoji, group))
        return ret