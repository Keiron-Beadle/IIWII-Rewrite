import discord, time

class BrawlRequest:
    def __init__(self, host : discord.User, pot : int, image : str = None):
        self.host = host
        self.title = ''
        self.terms = ''
        self.brawl_pot = pot
        self.image = image

    def set_title(self, title : str):
        self.title = title
    
    def set_terms(self, terms : list[str]):
        self.terms = terms

class BrawlResponse:
    def __init__(self, request : BrawlRequest, responder : discord.User, responder_terms : list[str]):
        self.request = request
        self.responder = responder
        self.terms = responder_terms

class BrawlPreGame:
    def __init__(self, request : BrawlRequest, responder : BrawlResponse):
        self.player1 = request.host
        self.player2 = responder.responder
        self.terms = responder.terms
        self.brawl_pot = request.brawl_pot
        self.player1_pot = {}
        self.player2_pot = {}
        self.start_time = 0

    def start(self):
        self.start_time = time.time()
    
class BrawlPostGame:
    def __init__(self, pre_game : BrawlPreGame, winner : discord.User):
        self.winner = pre_game.player1 if winner == pre_game.player1 else pre_game.player2
        self.loser = pre_game.player1 if winner == pre_game.player2 else pre_game.player2

        self.winner_pot = pre_game.player1_pot if winner == pre_game.player1 else pre_game.player2_pot
        self.loser_pot = pre_game.player1_pot if winner == pre_game.player2 else pre_game.player2_pot

        self.game_length = pre_game.start_time - time.time()