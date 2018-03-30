from enum import Enum


class Player(Enum):
    """
    Used to represent a player.
    """
    _WHITE_REPRESENTATION = 'O'
    _BLACK_REPRESENTATION = '@'

    WHITE = 0       # White player.
    BLACK = 1       # Black player.

    def get_representation(self):
        """
        Returns the string representation for the piece. Expected use would be for printing the board that the
        square (which has this piece) is a part of.
        """
        if (self == Player.WHITE):
            return Player._WHITE_REPRESENTATION.value

        if (self == Player.BLACK):
            return Player._BLACK_REPRESENTATION.value
