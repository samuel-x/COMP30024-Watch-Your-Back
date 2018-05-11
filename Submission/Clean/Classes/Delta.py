from typing import List, Optional

from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.PlayerColor import PlayerColor


class Delta():
    """
    A more abstract class. It contains information regarding a move made. An
    before-board and an appropriate delta should give just enough information to
    create the resulting board.
    """

    # The square that the moving piece originated from.
    move_origin: Square
    # The square that the moving piece moved to. The actual piece object will
    # not be attached to move_target, it will still be on move_origin.
    move_target: Square
    # A list of the positions for squares that had pieces removed at the end of
    # the round. If a player moves a piece to commit suicide by moving it e.g.
    # between two enemy pieces, the position that the piece ended up on i.e.
    # move_target will be included in .killed_square_positions.
    killed_square_positions: List[Pos2D]
    # A list of squares that were eliminated due to the shrinking of the board, not due to the direct movement of an
    # enemy piece.
    eliminated_squares: List[Square]
    # A list of squares that became corner pieces as a result of a death zone.
    new_corners: List[Square]
    # A reference to the enum representing the player who made the move/delta.
    player: PlayerColor

    def __init__(self, player: PlayerColor, move_origin: Optional[Square], move_target: Square,
                 killed_square_positions: Optional[List[Pos2D]], eliminated_squares: List[Square],
                 new_corners: List[Square]):
        self.player = player
        self.move_origin = move_origin
        self.move_target = move_target
        self.killed_square_positions = killed_square_positions
        self.eliminated_squares = eliminated_squares
        self.new_corners = new_corners

    def get_referee_form(self):
        if (self.move_origin is None):
            return self.move_target.pos.get_referee_form()
        else:
            return (self.move_origin.pos.get_referee_form(),
                    self.move_target.pos.get_referee_form())

    def __str__(self) -> str:
        """
        Returns a string representation of the calling instance.
        """
        if self.move_origin is None:
            return "{}".format(self.move_target.pos)
        else:
            return "{} -> {}".format(self.move_origin.pos, self.move_target.pos)

    def __eq__(self, other: 'Delta') -> bool:
        """
        Compares two delta objects.
        """
        self_tuple = (self.player, self.move_origin, self.move_target,
                      self.killed_square_positions)
        other_tuple = (other.player, other.move_origin, other.move_target,
                       other.killed_square_positions)

        return self_tuple == other_tuple

    def __hash__(self):
        components = (self.move_origin, self.move_target,
                      *self.killed_square_positions, *self.eliminated_squares,
                      *self.new_corners, self.player)

        return hash(components)