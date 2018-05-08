from math import sqrt, log

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