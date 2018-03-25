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
        if (start_board == None):
            self._board = Board(None, 1, GamePhase.PLACEMENT)
        else:
            self._board = start_board

        self._node = self._init_node
        random.seed(seed)

    def run(self):
        print(self._board)

        is_maximizer: bool = True
        while (self._board.phase != GamePhase.FINISHED):
            # if (not is_maximizer): # TODO Uncomment when doing massacre mode.
            #     is_maximizer = not is_maximizer
            #     self._board.round_num -= 1
            #     continue

            deltas: List[Delta] = self._board.get_all_valid_moves(Utils.get_player(self._board.round_num))
            delta_scores: List[Tuple[Delta, float]] = []
            for delta in deltas:
                delta_scores.append((delta, AlphaBetaAgent.alphabeta(self._board.get_next_board(delta), Node(self._node, delta), 4, -9999, 9999, not is_maximizer)))

            # If there are multiple deltas with the same high-score, this will ensure that a random one is picked so
            # that it's not deterministic every time the game starts (which is an issue with simple
            # white - black heuristic).
            random.shuffle(delta_scores)

            if (len(set([delta_score[1] for delta_score in delta_scores])) == 1):
                best_delta: Tuple[Delta, float] = random.choice(delta_scores)
            elif is_maximizer:
                best_delta: Tuple[Delta, float] = max(delta_scores, key=lambda x:x[1])
            elif not is_maximizer:
                best_delta: Tuple[Delta, float] = min(delta_scores, key=lambda x:x[1])

            self._board = self._board.get_next_board(best_delta[0])
            self._node = Node(self._node, best_delta[0])
            is_maximizer = not is_maximizer

            print("{:3}: {} ({})".format(self._board.round_num - 1, best_delta[0], best_delta[1]))
            print(self._board)

    @staticmethod
    def alphabeta(board: Board, node: Node, depth: int, alpha: float, beta: float, is_maximizer: bool):
        if (depth == 0 or board.phase == GamePhase.FINISHED):
            return AlphaBetaAgent.get_heuristic_value(board)

        if (is_maximizer):
            v: float = -999999
            deltas: List[Delta] = board.get_all_valid_moves(Utils.get_player(board.round_num))
            for delta in deltas:
                child_node: Node = Node(node, delta)
                v = max(v, AlphaBetaAgent.alphabeta(board.get_next_board(delta), child_node, depth - 1, alpha, beta, False))
                alpha = max(alpha, v)
                if (beta <= alpha):
                    break
            return v
        else:
            v = 999999
            deltas: List[Delta] = board.get_all_valid_moves(Utils.get_player(board.round_num))
            for delta in deltas:
                child_node: Node = Node(node, delta)
                v = min(v, AlphaBetaAgent.alphabeta(board.get_next_board(delta), child_node, depth - 1, alpha, beta, True))
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return v

    @staticmethod
    def get_heuristic_value(board: Board):
        WHITE_VICTORY: int = 9999
        BLACK_VICTORY: int = -9999

        if (board.phase == GamePhase.FINISHED):
            if (board.winner == Player.WHITE):
                return WHITE_VICTORY
            if (board.winner == Player.BLACK):
                return BLACK_VICTORY

        num_white_pieces: int = len(board._get_player_squares(Player.WHITE))
        num_black_pieces: int = len(board._get_player_squares(Player.BLACK))
        return num_white_pieces - num_black_pieces