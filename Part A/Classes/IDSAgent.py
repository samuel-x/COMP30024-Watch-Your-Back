import random
from typing import List, Tuple

from Classes.Board import Board
from Classes.Delta import Delta
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.GamePhase import GamePhase
from Enums.Player import Player


class IDSAgent:

    # When playing massacre, we don't want to sacrifice our own pieces to kill enemy pieces. Therefore, weigh white
    # pieces higher than black pieces.
    _WHITE_WEIGHT: float = 1.1
    _BLACK_WEIGHT: float = 1.0
    # How much to weigh the manhattan distance. We only want to weigh the manhattan distance enough for it to play
    # a role when there are no options to kill an enemy piece, hence the low weight.
    _DIST_WEIGHT: float = 0.001
    # We really don't want to repeat board states. When a repeat board is
    _REPEAT_BOARD: int = -99999
    # Score-decimal place rounding. Used to prevent floating point imprecision from interfering with move decisions.
    _SCORE_NUM_ROUNDING: int = 10
    # The length of the history of recent board states the agent can remember. Used to avoid repeat moves.
    _BOARD_MEMORY: int = 256

    # A reference to the current board that the agent is on.
    _board: Board
    _recent_board_history: List[str] = []

    def __init__(self, start_board: Board, seed: int = None):
        self._board = start_board

        if (seed != None):
            random.seed(seed)

    def massacre(self):
        """
        This method runs the algorithm until all enemy pieces are killed (or the game is over otherwise).
        """
        print(self._board)

        while (self._board.phase != GamePhase.FINISHED):

            deltas: List[Delta] = self._board.get_all_valid_moves(Player.WHITE)
            delta_scores: List[Tuple[Delta, List[float]]] = []
            for delta in deltas:
                delta_scores.append((delta, IDSAgent.get_board_score(self._board.get_next_board(delta), 0,
                                                                     self._recent_board_history)))

            # If there are multiple deltas with the same high-score, this will ensure that a random one is picked so
            # that it's not deterministic every time the game starts. Also helps avoid endless loops.
            random.shuffle(delta_scores)

            best_delta: Tuple[Delta, List[float]] = max(delta_scores, key=lambda x:(x[1][0], -len(x[1]), x[1]))

            self._board = self._board.get_next_board(best_delta[0])

            self._recent_board_history = [self._board.__str__()] + self._recent_board_history[:IDSAgent._BOARD_MEMORY]

            print("{:3}: {} ({})".format(self._board.round_num - 1, best_delta[0], best_delta[1]))
            print(self._board)

    @staticmethod
    def get_board_score(board: Board, depth: int, board_history: List[str]) -> List[float]:
        if (board.__str__() in board_history):
            return [IDSAgent._REPEAT_BOARD]

        if (depth == 0 or board.phase == GamePhase.FINISHED):
            return [IDSAgent.get_heuristic_value(board)]

        deltas: List[Delta] = board.get_all_valid_moves(Player.WHITE)
        best_score: List[float] = [-999999]
        for delta in deltas:
            best_score = max(best_score, IDSAgent.get_board_score(board.get_next_board(delta), depth - 1, board_history))

        return best_score + [IDSAgent.get_heuristic_value(board)]

    @staticmethod
    def get_heuristic_value(board: Board):
        black_squares: List[Square] = board.get_player_squares(Player.BLACK)
        white_squares: List[Square] = board.get_player_squares(Player.WHITE)

        manhattan_dist_sum: int = 0
        if (len(black_squares) > 0):
            black_square: Square = black_squares[0]
            for white_square in white_squares:
                difference: Pos2D = (black_square.pos - white_square.pos)
                manhattan_dist_sum += abs(difference.x) + abs(difference.y)

        num_white_pieces: int = len(white_squares)
        num_black_pieces: int = len(black_squares)
        return round(IDSAgent._WHITE_WEIGHT * num_white_pieces - \
               IDSAgent._BLACK_WEIGHT * num_black_pieces - \
               IDSAgent._DIST_WEIGHT * manhattan_dist_sum, IDSAgent._SCORE_NUM_ROUNDING)