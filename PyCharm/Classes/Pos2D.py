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

    def add_x(self, x: int):
        """
        Returns a new Pos2D with 'x' added to the calling instance's x value.
        """
        return Pos2D(self.x + x, self.y)

    def add_y(self, y: int):
        """
         Returns a new Pos2D with 'y' added to the calling instance's y value.
        """
        return Pos2D(self.x, self.y + y)

    @staticmethod
    def add(pos1, pos2):
        """
        Returns a new Pos2D with the two given positions added together.
        """
        return Pos2D(pos1.x + pos2.x, pos1.y + pos2.y)

    @staticmethod
    def minus(pos1, pos2):
        """
        Returns a new Pos2D with second given position subtracted from the first.
        """
        return Pos2D(pos1.x - pos2.x, pos1.y - pos2.y)