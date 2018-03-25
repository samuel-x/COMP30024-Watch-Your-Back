from Enums.Player import Player


class Piece():
    """
    A structure that represents a piece on the board.
    """

    owner: Player
    _id: int = 0

    def __init__(self, owner: Player):
        self.owner = owner
        self._id = Piece._id
        Piece._id += 1

    def getRepresentation(self):
        """
        Returns the string representation for the piece. Expected use would be for printing the board that the
        square (which has this piece) is a part of.
        """
        return self.owner.getRepresentation()

    def __eq__(self, other: 'Piece'):
        return self._id == other._id