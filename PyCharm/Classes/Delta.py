from typing import List

from Classes.Square import Square


class Delta():
    """
    A more abstract class. It contains information regarding a move made. An before-board and an appropriate delta
    should give just enough information to create the resulting board.
    """

    # The square that the moving piece originated from.
    move_origin: Square
    # The square that the moving piece moved to. The actual piece object will not be attached to move_target, it will
    # still be on move_origin.
    move_target: Square
    # A list of the squares that had pieces removed at the end of the round. May include squares that were killed due
    # to the shrinking of the board, not necessarily due to the direct movement of an enemy piece. If a player moves a
    # piece to commit suicide by moving it e.g. between two enemy pieces, the square that the piece ended up on
    # i.e. moveTarget will be included in .killedSquares.
    killed_squares: List[Square]

    def __init__(self, move_origin: Square, move_target: Square, killed_squares: List[Square]):
        pass