from math import sqrt, log

class Utilities():
    """
    A class designed not to be instantiated. Contains useful methods to be used elsewhere in the project.
    """

    @staticmethod
    def UCB1(wi: float, ni: int, Ni: int, c: float) -> float:
        return wi / ni + c * sqrt(log(Ni) / ni)