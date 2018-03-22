class Delta():
    """
    A more abstract class. It contains information regarding a move made. An before-board and an appropriate delta
    should give just enough information to create the resulting board.
    Upon creation, assumed to contain the following fields:
    Square moveOrigin           The square that the moving piece originated from.
    Square moveTarget           The square that the moving piece moved to.
    Square[] killedSquares      A list of the squares that had pieces removed at the end of the round.

    .killedSquares may include squares that were killed due to the shrinking of the board, not necessarily due to the
    direct movement of an enemy piece. If a player moves a piece to commit suicide by moving it e.g. between two
    enemy pieces, the square that the piece ended up on i.e. moveTarget will be included in .killedSquares.
    """

    def __init__(self):
        pass