# This will be the file to run the program.
import time

from Classes.AlphaBetaAgent import AlphaBetaAgent
from Classes.Board import Board
from Enums.GamePhase import GamePhase


from Enums.Player import Player

MOVES = "Moves"
MASSACRE = "Massacre"

def main():

    board: Board = Board.create_from_string(1, GamePhase.MOVEMENT)

    mode: str = input()

    if (mode == MOVES):
        print(board.get_num_moves(Player.WHITE))
        print(board.get_num_moves(Player.BLACK))
    elif (mode == MASSACRE):
        start = time.time()  # TODO Delete
        alpha_beta_agent = AlphaBetaAgent(board, 30024)
        alpha_beta_agent.massacre()
        print(time.time() - start)


main()

