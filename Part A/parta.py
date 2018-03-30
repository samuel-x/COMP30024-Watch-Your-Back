# This will be the file to run the program.

from Classes.Board import Board
from Classes.IDSAgent import IDSAgent
from Enums.GamePhase import GamePhase
from Enums.Player import Player

MOVES = "Moves"
MASSACRE = "Massacre"


def parta():

    # Notes on style:

    # This project utilizes type hints, as specified in the PEP484 standard:
    # https://www.python.org/dev/peps/pep-0484/
    # This project utilizes variable annotations, as specified in the PEP526
    # standard: https://www.python.org/dev/peps/pep-0526/
    # This, in our opinion, makes the code easier to read, debug, and
    # understand, as types are (almost) always explicitly stated.

    # Additionally, we utilize the convention of naming attributes of classes
    # with a leading underscore ('_') if they are not meant as part of its
    # public interface i.e. not meant to be used outside of the defining class.
    # These tend to be helper methods for other, larger methods that *are* part
    # of the public interface for that class. This, in our opinion, makes the
    # utilization classes easier as it's easier to see which methods to avoid
    # using outside of their defining classes.

    board: Board = Board.create_from_string(1, GamePhase.MOVEMENT)
    mode: str = input()

    if (mode == MOVES):
        print(board.get_num_moves(Player.WHITE))
        print(board.get_num_moves(Player.BLACK))
    elif (mode == MASSACRE):
        alpha_beta_agent = IDSAgent(board, 1)
        alpha_beta_agent.massacre()


parta()
