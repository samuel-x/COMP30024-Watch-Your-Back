import random
import time
from math import sqrt
from typing import List, Tuple

from Classes import Delta
from Classes.Board import Board
from Classes.Node import Node
from Enums.GamePhase import GamePhase
from Enums.Player import Player
from Misc.Utilities import Utilities as Utils


class MCTSAgent():
    """
    Contains the main driver functions used for this AI. Contains functions that, together, implement the Monte Carlo
    Tree Search algorithm.
    """

    _EXPLORATION_MULTIPLIER: float = sqrt(2)

    # A reference to the root node in the tree that's being searched by MCTS.
    tree_root: Node
    _board: Board
    _init_board: Board = Board(None, 1, GamePhase.PLACEMENT)

    def __init__(self, tree_root: Node, start_board: Board = _init_board, seed: int = None):
        self.tree_root = tree_root
        self._board = start_board

        if (seed is not None):
            random.seed(seed)

    def train(self, duration_seconds: int):
        end_time: float = time.time() + duration_seconds
        while (time.time() < end_time):
            print(self.tree_root.wins, self.tree_root.num_simulations) # TODO Remove
            self._simulate()
            self._board = self._init_board
            # break # TODO Remove
        print(self.tree_root.wins, self.tree_root.num_simulations)  # TODO Remove

    def _select(self, node: Node, total_num_simulations: int) -> Node:
        scores: List[Tuple[Node, float]] = []
        unexplored_nodes_score: float = Utils.UCB1(1, 2, total_num_simulations, MCTSAgent._EXPLORATION_MULTIPLIER)
        # A list of all deltas which have already been explored at least once. Therefore, they are nodes.
        children: List[Node] = node.children
        # A list of all valid deltas from the given board.
        deltas: List[Delta] = self._board.get_all_valid_moves(Utils.get_player(self._board.round_num))

        if (len(children) > 0):
            for child in children:
                # Since some deltas have already been explored and are therefore included in 'children', remove them
                # from 'deltas' so that it only contains unexplored moves.
                deltas.remove(child.delta)
                scores.append((child, Utils.UCB1(child.wins, child.num_simulations, total_num_simulations,
                                                 MCTSAgent._EXPLORATION_MULTIPLIER)))

            # Since there are no unexplored options available, we'll set its score to -1 such that the algorithm won't
            # attempt to choose an unexplored option (since there are none).
            if len(deltas) == 0:
                unexplored_nodes_score = -1

            # Order by highest scoring nodes.
            scores = sorted(scores, key=lambda x:x[1], reverse=True)
            for child, score in scores:
                if (score > unexplored_nodes_score):
                    # This is to avoid re-exploring a leaf node that resulted in a win or loss. We want to explore new
                    # options. Otherwise we'd have wasted this simulation or back-propagated the same result twice.
                    if (self._board.get_next_board(child.delta).phase == GamePhase.FINISHED):
                        continue
                    else:
                        return child
                else:
                    # We've now reached a (node : score) pair that has a lower score than all the unexplored moves.
                    # Therefore, stop iterating through existing nodes so we can instead select an unexplored move.
                    break

        random_delta: Delta = random.choice(deltas)
        new_child_node: Node = Node(node, random_delta)
        node.children.append(new_child_node)
        return new_child_node

    def _simulate(self):
        leaf: Node = self._select(self.tree_root, self.tree_root.num_simulations)
        self._board = self._board.get_next_board(leaf.delta)
        while (self._board.phase != GamePhase.FINISHED):

            leaf = self._select(leaf, self.tree_root.num_simulations)
            self._board = self._board.get_next_board(leaf.delta)
            if (self._board != 1): # TODO Remove this
                selection = "({}, {}) -> NODE" if leaf.num_simulations > 2 else "({}, {}) -> EXPLORE"
                print("{:3}: {} : {}".format(self._board.round_num - 1, leaf.delta.player, selection.format(leaf.wins, leaf.num_simulations)))
                if (leaf.delta.move_origin is not None):
                    print("{} -> ".format(leaf.delta.move_origin.pos), end="")
                print("{}".format(leaf.delta.move_target.pos))

            print(self._board)
            print("")

        self._back_propagate(leaf, self._board.winner)

    def _back_propagate(self, node: Node, winner: Player):
        """
        TODO
        Can be done recursively, but no point in using a stack. Iteratively
        is more memory efficient.
        :param node:
        :param winner:
        :return:
        """

        while (node is not None):
            node.num_simulations += 1

            if ((node.parent is None and node.children[0].delta.player == winner) or
                    (node.delta is not None and node.delta.player == winner)):
                node.wins += 1
            elif (winner is None):
                # Must have been a tie.
                node.wins += 0.5

            # TODO Remove this (temp for printing/debugging)
            # if (node.board.round_num != 1):
            #     print("{:3}: {}: ".format(node.board.round_num - 1, node.delta.player), end="")
            #     if (node.delta.move_origin is not None):
            #         print("{} -> ".format(node.delta.move_origin.pos), end="")
            #     print("{}".format(node.delta.move_target.pos))
            #
            # print(node.board)
            # print("")

            node = node.parent