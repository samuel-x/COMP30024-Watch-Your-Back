from typing import List

from Classes.Board import Board
from Classes.Delta import Delta


class Node():
    """
    Represents a node in the game tree.
    """

    parent: 'Node'
    # The delta that occurred between the parent board and this one.
    delta: Delta

    def __init__(self, parent, delta):
        self.parent = parent
        self.delta = delta