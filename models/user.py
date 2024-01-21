from discord import User, Guild

class User:
    def __init__(self, id: int, guild: Guild):
        self.id = id
        self.guild = guild

    def __eq__(self, other):
        return self.id == other.id and self.guild.id == other.guild.id