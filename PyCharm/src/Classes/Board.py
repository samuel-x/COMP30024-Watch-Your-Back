class Board():
    """
    A structure that represents the board at a given point. Upon creation, assumed to contain the following fields:
    Square[][] squares
    int roundNum            Not turn number i.e. after each player has had a turn, then roundNum == 3.
    GamePhase phase         An enum used to indicate the current phase of the game.
    Player winner           == None while the game isn't done. If phase == FINISHED and winner == None, that means tie.
    """

    def __init__(self):
        pass