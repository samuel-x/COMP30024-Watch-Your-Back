from typing import List, Optional

from Classes.Pos2D import Pos2D
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
    # A list of the positions for squares that had pieces removed at the end of the round. If a player moves a piece to
    # commit suicide by moving it e.g. between two enemy pieces, the position that the piece ended up on i.e.
    # move_target will be included in .killed_square_positions.
    killed_square_positions: List[Pos2D]
    # A reference to the enum representing the player who made the move/delta.
    player: Player

    def __init__(self, player: Player, move_origin: Optional[Square], move_target: Square,
                 killed_square_positions: Optional[List[Pos2D]]):
        self.player = player
        self.move_origin = move_origin
        self.move_target = move_target
        self.killed_square_positions = killed_square_positions

    def __str__(self):
        player: str = self.player.__str__()
        if (self.move_origin == None):
            return player + ": -> {}".format(self.move_target.pos)
        else:
            return player + ": {} -> {}".format(self.move_origin.pos, self.move_target.pos)

    def __eq__(self, other: 'Delta'):
        """
        TODO Make this nicer (and for Square?)
        :param other:
        :return:
        """
        if (not isinstance(other, Delta)):
            return False

        self_tuple = (self.player, self.move_origin, self.move_target, self.killed_square_positions)
        other_tuple = (other.player, other.move_origin, other.move_target, other.killed_square_positions)

        return self_tuple == other_tuple