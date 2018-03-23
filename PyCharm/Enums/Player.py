from enum import Enum

class Player(Enum):
    """
    Used to represent a player.
    """
    _whiteRepresentation = 'O'
    _blackRepresentation = '@'

    WHITE = 0       # White player.
    BLACK = 1       # Black player.

    def getRepresentation(self):
        if (self == Player.WHITE):
            return Player._whiteRepresentation.value

        if (self == Player.BLACK):
            return Player._blackRepresentation.value