from enum import Enum

class GamePhase(Enum):
    """
    Used to represent different states that a game/board can be in.
    """

    # Specifies the placement phase.
    PLACEMENT = 0
    # Specifies the movement phase.
    MOVEMENT = 1
    # The game is finished. Either player may be a victor or the game was a tie.
    FINISHED = 2