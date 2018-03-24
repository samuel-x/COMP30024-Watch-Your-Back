from Enums.Player import Player


class Piece():
    """
    A structure that represents a piece on the board. Upon creation, assumed to contain the following fields:
    Player owner
    """

    owner: Player

    def __init__(self, owner: Player):
        self.owner = owner

    def getRepresentation(self):
        """
        Returns the string representation for the piece. Expected use would be for printing the board that the
        square (which has this piece) is a part of.
        """
        return self.owner.getRepresentation()

    def __eq__(self, other: 'Piece'): # TODO Do we need this?
        return self.owner == other.owner