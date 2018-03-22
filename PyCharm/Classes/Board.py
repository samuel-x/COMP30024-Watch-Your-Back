from typing import List, Dict

from Classes.Delta import Delta
from Classes.Piece import Piece
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.GamePhase import GamePhase
from Enums.Player import Player
from Enums.SquareState import SquareState


class Board():
    """
    A structure that represents the board at a given point.
    """
    _NUMCOLS: int = 8
    _NUMROWS: int = 8

    # Structure that contains the squares.
    squares: Dict[Pos2D, Square]
    # round_num is not the turn number. e.g. after each player has had a turn, then round_num == 3.
    round_num: int
    # An enum used to indicate the current phase of the game.
    phase: GamePhase
    # Equals None while the game isn't done. If phase == FINISHED and winner == None, that the game was a tie.
    winner: Player

    def __init__(self, squares: Dict[Pos2D, Square], round_num: int, phase: GamePhase):
        if (squares == None):
            self.squares = self._init_squares()
        else:
            self.squares = squares

        self.round_num = round_num
        self.phase = phase


    def get_moves(self, pos: Pos2D) -> List[Delta]:
        potential_moves: List[Delta] = []

        surrounding_squares: List[Square] = self._get_surrounding_squares(pos)
        for surrounding_square in surrounding_squares:
            if (surrounding_square.state == SquareState.OPEN):
                move_origin: Square = self.squares[pos]
                move_target: Square = surrounding_square
                delta: Delta = Delta(move_origin, move_target, self._get_killed_squares(move_origin.occupant,
                                                                                        move_target.pos))
                potential_moves.append(delta)

        return potential_moves

    def _get_surrounding_squares(self, pos: Pos2D) -> List[Square]:
        """
        Returns a list of max 4 squares which are directly adjacent (up, down, left, right) of the given position.
        :param pos: The position which we want adjacent squares for.
        :return: A list of adjacent squares.
        """

        # Generate the four possible positions for the squares we want and then return a list containing the squares
        # located at those positions if they exist.
        adjacent_positions: List[Pos2D] = [pos.add_x(1), pos.add_x(-1), pos.add_y(1), pos.add_y(-1)]
        return [self.squares[adj_pos] for adj_pos in adjacent_positions if adj_pos in self.squares]

    def _get_killed_squares(self, killer_piece: Piece, killer_pos: Pos2D) -> List[Square]:
        killed_squares: List[Square] = []

        surrounding_squares: List[Square] = self._get_surrounding_squares(killer_pos)

        for surrounding_square in surrounding_squares:
            if (surrounding_square.state == SquareState.OCCUPIED and
                    surrounding_square.occupant.owner != killer_piece.owner):
                delta_pos: Pos2D = Pos2D.minus(surrounding_square, killer_pos)
                opposite_square: Square = self.squares[Pos2D.add(surrounding_square.pos, delta_pos)]
                if (opposite_square != None and (opposite_square.state == SquareState.OCCUPIED and
                     opposite_square.occupant.owner == killer_piece.owner) or
                        opposite_square.state == SquareState.CORNER):
                    killed_squares.append(surrounding_square)

        return killed_squares

    def _init_squares(self):
        squares: Dict[Pos2D, Square] = {}
        for col_i in range(Board._NUMCOLS):
            for row_i in range(Board._NUMROWS):
                pos: Pos2D = Pos2D(col_i, row_i)

                if (pos.x == 0 and (pos.y == 0 or pos.y == Board._NUMROWS - 1) or
                        pos.x == Board._NUMCOLS - 1 and (pos.y == 0 or pos.y == Board._NUMROWS - 1)):
                    squares[pos] = Square(pos, None, SquareState.CORNER)
                else:
                    squares[pos] = Square(pos, None, SquareState.OPEN)

        return squares