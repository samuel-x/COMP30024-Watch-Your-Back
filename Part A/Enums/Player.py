from enum import Enum

class Player(Enum):
    """
    Used to represent a player.
    """
    _whiteRepresentation = 'O' # TODO Change these to O and @ respectively before submission.
    _blackRepresentation = '@'

    WHITE = 0       # White player.
    BLACK = 1       # Black player.

    def getRepresentation(self):
        """
        Returns the string representation for the piece. Expected use would be for printing the board that the
        square (which has this piece) is a part of.
        """
        if (self == Player.WHITE):
            return Player._whiteRepresentation.value

        if (self == Player.BLACK):
            return Player._blackRepresentation.value