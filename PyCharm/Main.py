from Classes.Node import Node
from Misc.Utilities import Utilities as Utils

# This will be the file to run the program.
node = Node("node", "board", "delta")

def main():
    print(node.board)
    print("hello")

    iAmAString: str = "Woo"

    Utils.UCB1(1, 2, 3, iAmAString)


main()
