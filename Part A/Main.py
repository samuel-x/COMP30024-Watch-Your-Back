from Classes.AlphaBetaAgent import AlphaBetaAgent
from Classes.Board import Board
from Classes.MCTSAgent import MCTSAgent
from Classes.Node import Node
from Enums.GamePhase import GamePhase


# This will be the file to run the program.

def main():
    # tree_root: Node = Node(None, None)
    # mcts_agent: MCTSAgent = MCTSAgent(tree_root, seed=30024)
    # mcts_agent.train(20)

    # alpha_beta_agent = AlphaBetaAgent(Board.create_from_string(31, GamePhase.MOVEMENT, None), 30024)
    alpha_beta_agent = AlphaBetaAgent(None, 30024)
    alpha_beta_agent.run()

main()
