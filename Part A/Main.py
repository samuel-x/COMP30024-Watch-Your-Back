import time

from Classes.AlphaBetaAgent import AlphaBetaAgent
from Classes.Board import Board
from Enums.GamePhase import GamePhase


# This will be the file to run the program.

def main():

    alpha_beta_agent = AlphaBetaAgent(Board.create_from_string(1, GamePhase.MOVEMENT), 30024)
    start = time.time()
    alpha_beta_agent.massacre()
    print(time.time() - start)

main()
