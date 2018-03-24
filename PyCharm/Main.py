import copy

from Classes.Board import Board
from Classes.LiteMCTSAgent import LiteMCTSAgent
from Classes.LiteNode import LiteNode
from Classes.MCTSAgent import MCTSAgent
from Classes.Node import Node
from Classes.Piece import Piece
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.GamePhase import GamePhase
from Enums.Player import Player
from Enums.SquareState import SquareState
from Misc.Utilities import Utilities as Utils

# This will be the file to run the program.

def main():
    # TODO Implement turn skipping if a player cannot move.
    board: Board = Board(None, 1, GamePhase.PLACEMENT, None)

    # tree_root: Node = Node(None, board, None)
    # mcts_agent: MCTSAgent = MCTSAgent(tree_root, 30024)
    # mcts_agent.train(60 * 60)

    tree_root: LiteNode = LiteNode(None, None)
    mcts_agent: LiteMCTSAgent = LiteMCTSAgent(tree_root, seed=30024)
    mcts_agent.train(60*60)


    # pos1 = Pos2D(5, 3)
    # pos2 = Pos2D(3, 3)

main()
