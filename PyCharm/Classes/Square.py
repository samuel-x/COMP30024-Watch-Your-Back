from Classes.Piece import Piece
from Classes.Pos2D import Pos2D
from Enums.SquareState import SquareState


class Square():
    """
    A structure that represents a square on a board. Upon creation, assumed to contain the following fields:
    Pos2D pos               A 2D coordinate object to indicate the location of the square on the board.
    Piece occupant
    SquareState state       An enum used to indicate the state of the square.
    """

    pos: Pos2D
    occupant: Piece
    state: SquareState

    def __init__(self):
        pass