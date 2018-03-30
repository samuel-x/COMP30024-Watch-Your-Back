class Pos2D:
    """
    Represents a 2D position.
    """

    # Two ints to represent the 2D position.
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """
        Returns a new Pos2D with 'x' and 'y' added to the calling instance's corresponding values. Allows for simple
        pos1 + pos2 notation.
        """
        return Pos2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """
        Returns a new Pos2D with respective values of 'other' subtracted from 'self'. Allows for simple pos1 - pos2
        notation.
        """
        return Pos2D(self.x - other.x, self.y - other.y)

    def __str__(self):
        """
        Returns a string representation of the Pos2D instance. Allows Pos2Ds to be used in the 'print()' function.
        """
        return "({}, {})".format(self.x, self.y)

    def __hash__(self) -> int:
        """
        Since we use Pos2Ds as keys in Board.squares (which is a Dict[Pos2D, Square]), we need to define a hash
        function so that Python knows how to hash them.
        """
        return hash((self.x, self.y))

    def __eq__(self, other: 'Pos2D') -> bool:
        """
        Used to compare if two Pos2Ds are equal or not. Also required in order to make Pos2Ds usable as dictionary keys.
        """
        return (self.x, self.y) == (other.x, other.y)
