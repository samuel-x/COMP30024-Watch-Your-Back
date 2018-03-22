from typing import List, Optional

from Classes.Square import Square
from Enums.Player import Player


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
    # A list of the squares that had pieces removed at the end of the round. If a player moves a piece to commit
    # suicide by moving it e.g. between two enemy pieces, the square that the piece ended up on i.e. moveTarget will be
    # included in .killedSquares.
    killed_squares: List[Square]
    # A list of squares that were eliminated due to the shrinking of the board, not due to the direct movement of an
    # enemy piece.
    eliminated_squares: List[Square]
    # A list of squares that became corner pieces as a result of a death zone.
    new_corners: List[Square]
    # A reference to the enum representing the player who made the move/delta.
    player: Player

    def __init__(self, player: Player, move_origin: Optional[Square], move_target: Square,
                 killed_squares: Optional[List[Square]], eliminated_squares: List[Square],
                 new_corners: List[Square]):
        self.player = player
        self.move_origin = move_origin
        self.move_target = move_target
        self.killed_squares = killed_squares
        self.eliminated_squares = eliminated_squares
        self.new_corners = new_corners

    def __eq__(self, other: 'Delta'):
        self_tuple = (self.player, self.move_origin, self.move_target, self.killed_squares, self.eliminated_squares,
                      self.new_corners)
        other_tuple = (other.player, other.move_origin, other.move_target, other.killed_squares,
                       other.eliminated_squares, other.new_corners)

        return self_tuple == other_tuple