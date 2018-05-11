from typing import List

from Classes.Board import Board
from Classes.Delta import Delta


class Node():
    """
    Represents a node in the MCTS tree.
    """

    parent: 'Node'
    children: List['Node']
    num_simulations: int
    # The number of wins recorded on the node. It is a float to allow for e.g. 2.5 which can represent 2 wins and 1
    # draw, or 1 win and 3 draws, etc.
    wins: float
    board: Board
    # The delta that occurred between the parent board and this one.
    delta: Delta

    def __init__(self, parent, board, delta):
        self.parent = parent
        self.board = board
        self.delta = delta

        self.children = []
        # In order to use the UCB1 function, numSimulations needs to be != 0. To solve this, we initialize and assume
        # all nodes have two simulations and one win i.e. 50% average win rate. This will give all nodes a fair chance
        # at being selected in simulations.
        self.num_simulations = 2
        self.wins = 1