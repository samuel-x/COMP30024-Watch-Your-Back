from enum import Enum


class SquareState(Enum):
    """
    Used to represent different states that a square can have. Each enum value is not equal to its printed
    representation as with the Player enum as e.g. OPEN = ELIMINATED = '-', which would cause issues. Instead, use the
    .getRepresentation function.
    """
    _OPEN_REPRESENTATION = '-'
    _CORNER_REPRESENTATION = 'X'

    OPEN = 0            # The square is open and has nothing on it, but can be moved to.
    CORNER = 1          # The square is a corner i.e. it cannot be moved to and can be used to eliminate pieces.
    OCCUPIED = 2        # The square has a piece on it.

    def get_representation(self):
        """
        Returns the string representation for the square state. Expected use would be for printing the board that the
        square (which has this state) is a part of.
        """
        if (self == SquareState.OPEN):
            return SquareState._OPEN_REPRESENTATION.value

        if (self == SquareState.CORNER):
            return SquareState._CORNER_REPRESENTATION.value

        raise ValueError("Invalid SquareState: No representation found.")
