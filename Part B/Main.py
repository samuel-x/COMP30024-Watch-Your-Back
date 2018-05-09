from Classes.Agents.MCTSAgent import MCTSAgent
from Classes.Node import Node


# This will be the file to run the program.

def main():
    tree_root: Node = Node(None, None)
    mcts_agent: MCTSAgent = MCTSAgent(tree_root, seed=30024)
    mcts_agent.train(30)

main()
