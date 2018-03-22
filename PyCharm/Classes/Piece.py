from Enums.Player import Player


class Piece():
    """
    A structure that represents a piece on the board. Upon creation, assumed to contain the following fields:
    Player owner
    """

    owner: Player

    def __init__(self, owner: Player):
        self.owner = owner

    def __eq__(self, other: 'Piece'):
        return self.owner == other.owner