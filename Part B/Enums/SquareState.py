from enum import Enum

class SquareState(Enum):
    """
    Used to represent different states that a square can have. Each enum value
    is not equal to its printed representation as with the Player enum as e.g.
    OPEN = ELIMINATED = '-', which would cause issues. Instead, use the
    .get_representation function.
    """
    _OPEN_REPRESENTATION = '-'
    _ELIMINATED_REPRESENTATION = '#' # TODO This should be '-' too in the submitted version for Part B.
    _CORNER_REPRESENTATION = 'X'

    # The square is open and has nothing on it, but can be moved to.
    OPEN = 0
    # The square has a piece on it.
    OCCUPIED = 1
    # The square is a corner i.e. it cannot be moved to and can be used to
    # eliminate pieces.
    CORNER = 2
    # The square is outside the play-zone (due to board shrinkage).
    ELIMINATED = 3

    def get_representation(self):
        """
        Returns the string representation for the square state. Expected use
        would be for printing the board that the square (which has this state)
        is a part of.
        """
        if (self == SquareState.OPEN):
            return SquareState._openRepresentation.value

        if (self == SquareState.ELIMINATED):
            return SquareState._eliminatedRepresentation.value

        if (self == SquareState.CORNER):
            return SquareState._cornerRepresentation.value

        raise ValueError("Invalid SquareState: No representation found.")