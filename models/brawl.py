from enum import Enum
import discord, time

class BrawlStatus(Enum):
    INACTIVE = 0
    OPEN = 1
    ACTIVE = 3
    PRE_GAME = 4

class BrawlRequest:
    def __init__(self, guild : discord.Guild, host : discord.User, pot : int, image : str = None):
        self.guild = guild
        self.host = host
        self.title = ''
        self.terms = ''
        self.brawl_pot = pot
        self.image = image
        self.status = BrawlStatus.OPEN

    def set_title(self, title : str):
        self.title = title
    
    def set_terms(self, terms : list[str]):
        self.terms = terms

class BrawlResponse:
    def __init__(self, request : BrawlRequest, responder : discord.User, responder_terms : list[str]):
        self.request = request
        self.guild = request.guild
        self.responder = responder
        self.terms = responder_terms

class BrawlPreGame:
    def __init__(self, request : BrawlRequest, responder : BrawlResponse):
        self.title = request.title
        self.guild = request.guild
        self.player1 = request.host
        self.player2 = responder.responder
        self.terms = responder.terms
        self.original_terms = request.terms
        self.brawl_pot = request.brawl_pot * 2
        self.status = BrawlStatus.PRE_GAME
        self.player1_pot = {}
        self.player2_pot = {}
        self.start_time = 0
        self.image = request.image

    def start(self):
        self.start_time = time.time()
        self.status = BrawlStatus.ACTIVE
    
class BrawlPostGame:
    def __init__(self, pre_game : BrawlPreGame, winner : discord.User):
        self.__player1 = pre_game.player1
        self.__player2 = pre_game.player2
        self.title = pre_game.title
        self.guild = pre_game.guild
        self.winner = 1 if winner == pre_game.player1 else 2
        self.loser = 2 if winner == pre_game.player1 else 1
        self.brawl_pot = pre_game.brawl_pot
        self.winner_pot = pre_game.player1_pot if winner == pre_game.player1 else pre_game.player2_pot
        self.loser_pot = pre_game.player1_pot if winner == pre_game.player2 else pre_game.player2_pot
        self.status = BrawlStatus.INACTIVE

        self.game_length = time.time() - pre_game.start_time

    def get_winner(self):
        return self.__player1 if self.winner == 1 else self.__player2
    
    def get_loser(self):
        return self.__player1 if self.loser == 1 else self.__player2