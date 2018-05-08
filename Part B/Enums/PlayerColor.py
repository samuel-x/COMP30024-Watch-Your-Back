from enum import Enum

class PlayerColor(Enum):
    """
    Used to represent a player.
    """
    _WHITE_REPRESENTATION = 'W'
    _BLACK_REPRESENTATION = 'B'

    # White player.
    WHITE = 0
    # Black player.
    BLACK = 1

    def get_representation(self):
        """
        Returns the string representation for the piece. Expected use would be
        for printing the board that the square (which has this piece) is a part
        of.
        """
        if (self == PlayerColor.WHITE):
            return PlayerColor._WHITE_REPRESENTATION.value

        if (self == PlayerColor.BLACK):
            return PlayerColor._BLACK_REPRESENTATION.value
