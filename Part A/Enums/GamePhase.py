from enum import Enum

class GamePhase(Enum):
    """
    Used to represent different states that a game/board can be in.
    """
    PLACEMENT = 0       # We're in the placement phase.
    MOVEMENT = 1        # We're in the movement phase.
    FINISHED = 2        # The game is finished. Either player may be a victor or the game was a tie.