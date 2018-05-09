from math import sqrt, log
from typing import Union, Iterable

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
    def get_num_max(nums: Iterable[Union[int, float]]) -> int:
        """
        Given a list of numbers, returns the number of max values in it e.g.
        given [4 5 6 2 1 6], returns 2 because there are two 6s (max value).
        """

        max_value: Union[int, float] = max(nums)
        count: int = 0
        for num in nums:
            if (num == max_value):
                count += 1

        return count
