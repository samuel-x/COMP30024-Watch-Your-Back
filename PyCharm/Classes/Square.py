from typing import Optional

from Classes.Piece import Piece
from Classes.Pos2D import Pos2D
from Enums.SquareState import SquareState


class Square():
    """
    A structure that represents a square on a board.
    """

    # A 2D coordinate object to indicate the location of the square on the board.
    pos: Pos2D
    # A piece that may or may not be on the square. Equals None when there is no piece.
    occupant: Piece
    # An enum used to indicate the state of the square.
    state: SquareState

    def __init__(self, pos: Pos2D, occupant: Optional[Piece], state: SquareState):
        self.pos = pos
        self.occupant = occupant
        self.state = state

    def __eq__(self, other: 'Square'):
        if (not isinstance(self, Square)):
            return not isinstance(other, Square)

        return (self.pos, self.occupant, self.state) == (other.pos, other.occupant, other.state) if isinstance(other, Square) else False #TODO This is ugly