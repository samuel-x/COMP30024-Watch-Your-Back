import copy

from Classes.Board import Board
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
node = Node("node", "board", "delta")

def main():
    board: Board = Board(None, 1, GamePhase.PLACEMENT, None)

    tree_root: Node = Node(None, board, None)
    mcts_agent: MCTSAgent = MCTSAgent(tree_root)
    mcts_agent.train(60)

main()
