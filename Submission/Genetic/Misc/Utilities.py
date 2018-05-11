from math import sqrt, log
from typing import List, Dict, Tuple

from Classes.Delta import Delta
from Enums.PlayerColor import PlayerColor


class Utilities():
    """
    A class designed not to be instantiated. Contains useful methods to be used elsewhere in the project.
    """

    _FIRST_PLAYER: PlayerColor = PlayerColor.WHITE
    _SECOND_PLAYER: PlayerColor = PlayerColor.BLACK

    @staticmethod
    def UCB1(wi: float, ni: int, Ni: int, c: float) -> float:
        """
        TODO
        :param wi:
        :param ni:
        :param Ni:
        :param c:
        :return:
        """
        return wi / ni + c * sqrt(log(Ni) / ni)

    @staticmethod
    def get_player(round_num: int) -> PlayerColor:
        if (round_num % 2 == 1):
            return Utilities._FIRST_PLAYER
        else:
            return Utilities._SECOND_PLAYER

    @staticmethod
    def get_best_deltas(delta_scores: Dict[Delta, float], color: PlayerColor) -> List[Tuple[Delta, float]]:
        """
        Given a dictionary of deltas to their scores a player color, returns a
        list of best deltas (and their scores) for that player.
        """

        best_value: float
        if (color == PlayerColor.WHITE): # Maximize
            best_value = max(delta_scores.values())
        else: # Minimize
            best_value = min(delta_scores.values())

        best_deltas: List[(Delta, float)] = []
        for delta, score in delta_scores.items():
            if (score == best_value):
                best_deltas.append((delta, score))

        return best_deltas
