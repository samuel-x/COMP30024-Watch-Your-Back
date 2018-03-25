import random
from typing import List, Tuple

from Classes.Board import Board
from Classes.Delta import Delta
from Classes.Node import Node
from Enums.GamePhase import GamePhase
from Enums.Player import Player
from Misc.Utilities import Utilities as Utils


class AlphaBetaAgent():

    _board: Board
    _node: Node
    _init_node: Node = Node(None, None)

    def __init__(self, start_board: Board = None, seed: int = random.randint(0, 999999)):
        self._board = start_board
        self._node = self._init_node
        random.seed(seed)

    def massacre(self):
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
        best_score: List[float] = [-9999] + historical_scores
        for delta in deltas:
            child_node: Node = Node(node, delta)
            best_score = max(best_score, AlphaBetaAgent.alphabeta(board.get_next_board(delta), child_node, depth - 1, historical_scores))

        return  historical_scores + best_score + [AlphaBetaAgent.get_heuristic_value(board)]

    @staticmethod
    def get_heuristic_value(board: Board):
        # if (board.phase == GamePhase.FINISHED):
        #     return 9999 - board.round_num
        num_white_pieces: int = len(board._get_player_squares(Player.WHITE))
        num_black_pieces: int = len(board._get_player_squares(Player.BLACK))
        return num_white_pieces - num_black_pieces - board.round_num