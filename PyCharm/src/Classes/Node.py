class Node():
    """
    Represents a node in the MCTS tree. Upon creation, assumed to contain the following fields:
    Node parent
    Node[] children
    int numSimulations
    float wins             Where e.g. 2.5 can represent 2 wins and 1 draw, or 1 win and 3 draws, etc.
    Board board
    Delta delta            The delta that occurred between the parent board and this one.
    """

    def __init__(self, parent, board, delta):
        self.parent = parent
        self.board = board
        self.delta = delta

        self.children = []
        # In order to use the UCB1 function, numSimulations needs to be != 0. To solve this, we initialize and assume
        # all nodes have two simulations and one win i.e. 50% average win rate. This will give all nodes a fair chance
        # at being selected in simulations.
        self.numSimulations = 2
        self.wins = 1