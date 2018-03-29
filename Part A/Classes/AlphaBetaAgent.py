import random
#import difflib
from typing import List, Tuple

from Classes.Board import Board
from Classes.Delta import Delta
from Classes.Node import Node
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.GamePhase import GamePhase
from Enums.Player import Player



class AlphaBetaAgent():

    _board: Board
    _node: Node
    _init_node: Node = Node(None, None)

    def __init__(self, start_board: Board = None, seed: int = random.randint(0, 999999)):
        self._board = start_board
        self._node = self._init_node
        random.seed(seed)

    def massacre(self):
        """
        This method runs the algorithm until all enemy pieces are killed or there is a draw.
        :return:
        """
        print(self._board)

        while (self._board.phase != GamePhase.FINISHED):

            deltas: List[Delta] = self._board.get_all_valid_moves(Player.WHITE)
            delta_scores: List[Tuple[Delta, List[float]]] = []
            for delta in deltas:
                delta_scores.append((delta, AlphaBetaAgent.alphabeta(self._board.get_next_board(delta),
                                                                     Node(self._node, delta), 1, [])))

            # If there are multiple deltas with the same high-score, this will ensure that a random one is picked so
            # that it's not deterministic every time the game starts (which is an issue with simple
            # white - black heuristic).
            random.shuffle(delta_scores)

            best_delta: Tuple[Delta, List[float]] = max(delta_scores, key=lambda x:x[1])

            self._board = self._board.get_next_board(best_delta[0])
            self._node = Node(self._node, best_delta[0])

            print("{:3}: {} ({})".format(self._board.round_num - 1, best_delta[0], best_delta[1]))
            print(self._board)

    @staticmethod
    def alphabeta(board: Board, node: Node, depth: int, historical_scores: List[float]) -> List[float]:
        if (depth == 0 or board.phase == GamePhase.FINISHED):
            return [AlphaBetaAgent.get_heuristic_value(board)] + historical_scores

        deltas: List[Delta] = board.get_all_valid_moves(Player.WHITE)
        best_score: List[float] = [-999999] + historical_scores
        for delta in deltas:
            child_node: Node = Node(node, delta)
            best_score = max(best_score, AlphaBetaAgent.alphabeta(board.get_next_board(delta), child_node, depth - 1, historical_scores))

        return  historical_scores + best_score + [AlphaBetaAgent.get_heuristic_value(board)]

    @staticmethod
    def get_heuristic_value(board: Board):
        black_squares: List[Square] = board.get_player_squares(Player.BLACK)
        white_squares: List[Square] = board.get_player_squares(Player.WHITE)

        manhatten_dist_sum: int = 0
        if (len(black_squares) > 0):
            black_square: Square = black_squares[0]
            for white_square in white_squares:
                difference: Pos2D = (black_square.pos - white_square.pos)
                manhatten_dist_sum += abs(difference.x) + abs(difference.y)

        num_white_pieces: int = len(white_squares)
        num_black_pieces: int = len(black_squares)
        return num_white_pieces - num_black_pieces - board.round_num - manhatten_dist_sum * 0.001