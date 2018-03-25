from Classes.Board import Board
from Classes.MCTSAgent import MCTSAgent
from Classes.Node import Node
from Enums.GamePhase import GamePhase


# This will be the file to run the program.

def main():
    tree_root: Node = Node(None, None)
    mcts_agent: MCTSAgent = MCTSAgent(tree_root, seed=30024)
    mcts_agent.train(20)

main()
