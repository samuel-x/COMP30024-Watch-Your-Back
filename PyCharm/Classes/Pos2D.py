class Pos2D():
    """
    Represents a 2D position.
    """

    # Two ints to represent the 2D position.
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    # TODO: Better names between 'plus' and 'add'?
    def plus(self, x: int, y: int) -> 'Pos2D':
        """
         Returns a new Pos2D with 'x' and 'y' added to the calling instance's corresponding values.
        """
        return Pos2D(self.x + x, self.y + y)

    @staticmethod
    def add(pos1: 'Pos2D', pos2: 'Pos2D') -> 'Pos2D':
        """
        Returns a new Pos2D with the two given positions added together.
        """
        return Pos2D(pos1.x + pos2.x, pos1.y + pos2.y)

    @staticmethod
    def minus(pos1: 'Pos2D', pos2: 'Pos2D') -> 'Pos2D':
        """
        Returns a new Pos2D with second given position subtracted from the first.
        """
        return Pos2D(pos1.x - pos2.x, pos1.y - pos2.y)

    # TODO: Implement copy (and in Square)
    # def __deepcopy__(self, memodict={}) -> 'Pos2D':
    #

    def __hash__(self) -> int:
        """
        Since we use Pos2Ds as keys in Board.squares (which is a Dict[Pos2D, Square]), we need to define a hash
        function so that Python knows how to hash them.
        """
        return hash((self.x, self.y))

    def __eq__(self, other: 'Pos2D') -> bool:
        """
        Used to compare if two Pos2Ds are equal or not. Required in order to make Pos2Ds usable as dictionary keys.
        """
        return (self.x, self.y) == (other.x, other.y)