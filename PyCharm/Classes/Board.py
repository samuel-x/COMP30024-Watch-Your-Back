from typing import List, Dict

from Classes.Delta import Delta
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.SquareState import SquareState


class Board():
    """
    A structure that represents the board at a given point. Upon creation, assumed to contain the following fields:
    Square[][] squares
    int roundNum            Not turn number i.e. after each player has had a turn, then roundNum == 3.
    GamePhase phase         An enum used to indicate the current phase of the game.
    Player winner           == None while the game isn't done. If phase == FINISHED and winner == None, that means tie.
    """

    squares: Dict[Pos2D, Square]

    def __init__(self):
        pass

    def get_moves(self: Square, pos: Pos2D) -> List[Delta]:
        potential_moves: List[Delta] = []

        surrounding_squares: List[Square] = self._getSurroundingSquares(self, pos)
        for surrounding_square in surrounding_squares:
            if (surrounding_square.state == SquareState.OPEN):
                move_origin: Square = surrounding_square
                potential_moves.append(Delta(self.squares[pos], surrounding_square, self._getKilledSquares(self, )))


    def _getSurroundingSquares(self: Square, pos: Pos2D) -> List[Square]:
        pass