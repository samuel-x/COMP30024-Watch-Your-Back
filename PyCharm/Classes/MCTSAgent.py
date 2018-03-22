import time
from random import choice
from typing import List, Tuple

from math import sqrt

from Classes import Delta
from Classes.Node import Node
from Enums.GamePhase import GamePhase
from Enums.Player import Player
from Misc.Utilities import Utilities as Utils


class MCTSAgent():
    """
    Contains the main driver functions used for this AI. Contains functions that, together, implement the Monte Carlo
    Tree Search algorithm.
    """

    _EXPLORATIONMULTIPLIER: float = sqrt(2)

    # A reference to the root node in the tree that's being searched by MCTS.
    tree_root: Node

    def __init__(self, tree_root: Node):
        self.tree_root = tree_root

    def train(self, duration_seconds: int):
        end_time: float = time.time() + duration_seconds
        while (time.time() < end_time):
            self._simulate()

    @staticmethod
    def _select(node: Node, total_num_simulations: int) -> Node:
        scores: List[Tuple[Node, float]] = []
        unexplored_nodes_score: float = Utils.UCB1(1, 2, total_num_simulations, MCTSAgent._EXPLORATIONMULTIPLIER)
        # A list of all deltas which have already been explored at least once. Therefore, they are nodes.
        children: List[Node] = node.children
        # A list of all valid deltas from the given board.
        deltas: List[Delta] = node.board.get_all_valid_moves(Utils.get_player(node.board.round_num))

        if (len(children) > 0):
            for child in children:
                # Since some deltas have already been explored and are therefore included in 'children', remove them
                # from 'deltas' so that it only contains unexplored moves.
                deltas.remove(child.delta)
                scores.append((child, Utils.UCB1(child.wins, child.num_simulations, total_num_simulations,
                                                 MCTSAgent._EXPLORATIONMULTIPLIER)))

            # Order by highest scoring nodes.
            scores = sorted(scores, key=lambda x:x[1], reverse=True)
            for child, score in scores:
                if (score > unexplored_nodes_score):
                    # This is to avoid re-exploring a leaf node that resulted in a win or loss. We want to explore new
                    # options. Otherwise we'd have wasted this simulation or back-propagated the same result twice.
                    if (child.board.phase == GamePhase.FINISHED):
                        continue
                    else:
                        return child
                else:
                    # We've now reached a (node : score) pair that has a lower score than all the unexplored moves.
                    # Therefore, stop iterating through existing nodes so we can instead select an unexplored move.
                    break

        random_delta: Delta = choice(deltas)
        new_child_node: Node = Node(node, node.board.get_next_board(random_delta), random_delta)
        node.children.append(new_child_node)
        return new_child_node

    def _simulate(self):
        leaf: Node = self._select(self.tree_root, self.tree_root.num_simulations)
        while (leaf.board.phase != GamePhase.FINISHED):
            leaf = self._select(leaf, self.tree_root.num_simulations)

        self._back_propagate(leaf, leaf.board.winner)

    def _back_propagate(self, node: Node, winner: Player):
        """
        TODO
        Can be done recursively, but no point in using a stack. Iteratively
        is more memory efficient.
        :param node:
        :param winner:
        :return:
        """

        while (node != None):
            node.num_simulations += 1

            if (node.board.winner == winner):
                node.wins += 1
            elif (winner == None):
                # Must have been a tie.
                node.wins += 0.5

            print(node.num_simulations, node.wins)

            node = node.parent