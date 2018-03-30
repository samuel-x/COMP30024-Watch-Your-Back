from copy import deepcopy
from typing import List, Dict, Optional

from Classes.Delta import Delta
from Classes.Piece import Piece
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.GamePhase import GamePhase
from Enums.Player import Player
from Enums.SquareState import SquareState


class Board:
    """
    A structure that represents the board at a given point.
    """

    # Directional/locational constants.
    _HORIZONTAL: str = "horizontal"
    _VERTICAL: str = "vertical"
    _OMNI: str = "omnidirectional"

    _NUM_COLS: int = 8
    _NUM_ROWS: int = 8

    # The minimum number of pieces a player can have on the board before they
    # lose.
    _MIN_NUM_PIECES_BEFORE_LOSS = 1

    # Structure that contains the squares as (position : square) pairs.
    squares: Dict[Pos2D, Square]
    # round_num is not the turn number. e.g. after each player has had a turn,
    # then round_num == 3.
    round_num: int
    # An enum used to indicate the current phase of the game.
    phase: GamePhase

    def __init__(self, squares: Optional[Dict[Pos2D, Square]], round_num: int,
                 phase: GamePhase):
        if (squares is None):
            self.squares = self._init_squares()
        else:
            self.squares = squares

        self.round_num = round_num
        self.phase = phase

    def get_num_moves(self, player: Player) -> int:
        """
        This method takes a player and returns the number of possible moves that
        they can take. This is required for Part A question 1 as defined in the
        spec.
        """
        player_squares: List[Square] = self.get_player_squares(player)
        count: int = 0
        for player_square in player_squares:
            adj_squares: List[Square] = \
                self._get_adjacent_squares(player_square.pos)
            for adj_square in adj_squares:
                if (adj_square.state == SquareState.OPEN):
                    count += 1
                elif(adj_square.state == SquareState.OCCUPIED):
                    opposite_square: Square = \
                        self.squares.get(
                            self._get_opposite_pos(player_square.pos,
                                                   adj_square.pos))
                    if (opposite_square is not None
                            and opposite_square.state == SquareState.OPEN):
                        count += 1

        return count

    def get_valid_movements(self, pos: Pos2D) -> List[Delta]:
        """
        Given a position on the board, returns a list of possible moves (or
        'deltas') from that position.
        """
        valid_moves: List[Delta] = []

        adjacent_squares: List[Square] = self._get_adjacent_squares(pos)
        # For each adjacent square, determine if it can be moved to or jumped
        # over and then create and store the corresponding delta if possible.
        for adjacent_square in adjacent_squares:
            move_origin: Square
            move_target: Square

            if (adjacent_square.state == SquareState.OPEN):
                move_origin = self.squares[pos]
                move_target = adjacent_square
            elif (adjacent_square.state == SquareState.OCCUPIED):
                opposite_square: Square = \
                    self.squares.get(
                        self._get_opposite_pos(pos, adjacent_square.pos))
                if (opposite_square is not None
                        and opposite_square.state == SquareState.OPEN):
                    move_origin = self.squares[pos]
                    move_target = opposite_square
                else:
                    continue
            else:
                continue

            potential_kills: List[Pos2D] = \
                self._get_killed_positions(move_origin.occupant,
                                           move_target.pos)
            delta: Delta = Delta(self.squares[pos].occupant.owner, move_origin,
                                 move_target, potential_kills)
            valid_moves.append(delta)

        return valid_moves

    def get_all_valid_moves(self, player: Player) -> List[Delta]:
        """
        Returns a list of all possible moves for a given player.
        """
        valid_moves: List[Delta] = []

        # Get a list of all squares that are occupied by the given player.
        player_squares: List[Square] = self.get_player_squares(player)

        # Iterate over each of these squares and add their valid moves to
        # 'valid_moves'.
        [valid_moves.extend(self.get_valid_movements(square.pos)) for square in
         player_squares]

        return valid_moves

    def get_next_board(self, delta: Delta) -> 'Board':
        """
        This method takes a delta and uses it to create a new board from the
        calling instance. This can be seen as actually making the move, once the
        move has been determined.
        """

        # Sanity checks to ensure we're doing a legal move.
        assert self.squares[delta.move_target.pos].state == SquareState.OPEN
        assert self.squares[delta.move_origin.pos].state == SquareState.OCCUPIED

        next_board: Board = deepcopy(self)

        # Make sure that both the original and target squares are changed to
        # reflect change in the given delta.
        next_board.squares[delta.move_target.pos].occupant = \
            delta.move_origin.occupant
        next_board.squares[delta.move_target.pos].state = SquareState.OCCUPIED
        next_board.squares[delta.move_origin.pos].occupant = None
        next_board.squares[delta.move_origin.pos].state = SquareState.OPEN

        # Update all the squares that had a killed piece.
        for pos in delta.killed_square_positions:
            next_board.squares[pos].occupant = None
            next_board.squares[pos].state = SquareState.OPEN

        # Update the game state.
        next_board.round_num += 1
        next_board._update_game_phase()

        return next_board

    def get_player_squares(self, player: Player) -> List[Square]:
        """
        Returns a list of all squares that have a piece on them that is
        controlled by the given player.
        """
        return [square for square in self.squares.values() if
                square.state == SquareState.OCCUPIED
                and square.occupant.owner == player]

    def _get_adjacent_squares(self, pos: Pos2D, direction: str = _OMNI) \
            -> List[Square]:
        """
        Returns a list of max 4 squares which are directly adjacent (up, down,
        left, right) of the given position. Can specify if only adjacent squares
        in a certain direction are wanted using the 'direction' parameter.
        :param pos: The position which we want adjacent squares for.
        :param direction: The desired direction to get the adjacent squares for.
        Can be horizontal, vertical, or omni i.e. both.
        :return: A list of adjacent squares.
        """
        adjacent_squares: List[Square] = []
        if (direction == Board._OMNI):
            # Recursively call this method to get the horizontally and
            # vertically adjacent squares.
            adjacent_squares.extend(
                self._get_adjacent_squares(pos, Board._HORIZONTAL))
            adjacent_squares.extend(
                self._get_adjacent_squares(pos, Board._VERTICAL))
        elif (direction == Board._HORIZONTAL):
            adjacent_squares = [self.squares.get(pos + Pos2D(1, 0)),
                                self.squares.get(pos + Pos2D(-1, 0))]
        elif (direction == Board._VERTICAL):
            adjacent_squares = [self.squares.get(pos + Pos2D(0, 1)),
                                self.squares.get(pos + Pos2D(0, -1))]

        return [square for square in adjacent_squares if square is not None]

    def _get_killed_positions(self, moving_piece: Piece,
                              moving_piece_target_pos: Pos2D) -> List[Pos2D]:
        """
        This method takes a piece that is moving and it's target position and
        calculates a list of positions that will be killed as a result of the
        move. This may include the moving piece itself.
        """
        killed_positions: List[Pos2D] = []

        # Short for 'horizontally adjacent squares'.
        x_adjacent: List[Square] = \
            self._get_adjacent_squares(moving_piece_target_pos,
                                       Board._HORIZONTAL)
        y_adjacent: List[Square] = \
            self._get_adjacent_squares(moving_piece_target_pos,
                                       Board._VERTICAL)

        # Add any adjacent squares that would be killed if the given piece moved
        # to the given location.
        for adjacent_square in [*x_adjacent, *y_adjacent]:
            if (adjacent_square.state == SquareState.OCCUPIED and
                    adjacent_square.occupant.owner != moving_piece.owner):
                opposite_square: Square = \
                    self.squares.get(self._get_opposite_pos(
                        moving_piece_target_pos, adjacent_square.pos))

                if opposite_square is None:
                    # The opposite square out of bounds, move onto the next one.
                    continue

                # Check if the opposite piece is owned by the same player who's
                # making the move or if it is a corner square. If so, add the
                # adjacent square to the list of killed positions.
                if ((opposite_square.state == SquareState.OCCUPIED
                     and opposite_square.occupant.owner == moving_piece.owner
                     and opposite_square.occupant != moving_piece)
                        or opposite_square.state == SquareState.CORNER):
                    killed_positions.append(adjacent_square.pos)

        # Now check if the piece that is moving gets killed. This would
        # (probably) be a stupid move, but it could happen.

        # Remove references to adjacent squares if they are going to be killed,
        # as they then cannot kill the moving piece.
        [x_adjacent.remove(self.squares[pos]) for pos in killed_positions
         if self.squares[pos] in x_adjacent]
        [y_adjacent.remove(self.squares[pos]) for pos in killed_positions
         if self.squares[pos] in y_adjacent]

        # Filter out squares from both lists that are not occupied by enemy
        # pieces or aren't corners.
        potential_x_killer_squares = \
            [square for square in x_adjacent
             if ((square.state == SquareState.OCCUPIED
                  and (square.occupant.owner != moving_piece.owner))
                 or (square.state == SquareState.CORNER))]
        potential_y_killer_squares = \
            [square for square in y_adjacent
             if ((square.state == SquareState.OCCUPIED
                  and (square.occupant.owner != moving_piece.owner))
                 or (square.state == SquareState.CORNER))]

        # If either list still has two squares in them, that means that the
        # moving piece is doomed.
        if (len(potential_x_killer_squares) == 2
                or len(potential_y_killer_squares) == 2):
            killed_positions.append(moving_piece_target_pos)

        return killed_positions

    def _update_game_phase(self) -> None:
        """
        Checks the current state of the game and the board to determine if the
        game phase should change (and then makes that change).
        """

        # If either player has less than the minimum number of required pieces,
        # change the game state to reflect that the game has finished.
        if ((len(self.get_player_squares(Player.WHITE))
             < Board._MIN_NUM_PIECES_BEFORE_LOSS)
                or (len(self.get_player_squares(Player.BLACK))
                    < Board._MIN_NUM_PIECES_BEFORE_LOSS)):
            self.phase = GamePhase.FINISHED

    def __str__(self) -> str:
        """
        Returns a string representation of the calling instance.
        """
        output: str = ""

        for row_i in range(Board._NUM_ROWS):
            for col_i in range(Board._NUM_COLS):
                pos: Pos2D = Pos2D(col_i, row_i)
                output += ("{} ".format(self.squares[pos].get_representation()))
            # Finished row, add new line.
            output += "\n"

        return output

    def __deepcopy__(self, memodict={}) -> 'Board':
        """
        Returns a deep copy of the calling instance. Necessary in order to
        ensure that different boards don't reference the same Square objects in
        memory.
        """
        squares: Dict[Pos2D, Square] = deepcopy(self.squares)
        round_num: int = self.round_num
        phase: GamePhase = self.phase

        return Board(squares, round_num, phase)

    @staticmethod
    def _get_opposite_pos(first_pos: Pos2D, second_pos: Pos2D) -> Pos2D:
        """
        Given two sequential, adjacent positions, return the third position in
        that sequence. This method can be seen as getting the position that is
        opposite of 'first_pos' in regards to 'second_pos'. This method always
        returns a Pos2D, regardless of if it marks a position off of the board,
        an eliminated square, etc. In other words, it does no checking to see if
        the position is valid.
        """
        displacement: Pos2D = second_pos - first_pos

        # Ensure that the two given positions are adjacent.
        assert (abs(displacement.x) + abs(displacement.y)) == 1

        return second_pos + displacement

    @staticmethod
    def _init_squares() -> Dict[Pos2D, Square]:
        """
        This method initializes all square objects for a complete board as if it
        were the beginning of the game.
        """
        squares: Dict[Pos2D, Square] = {}
        for col_i in range(Board._NUM_COLS):
            for row_i in range(Board._NUM_ROWS):
                pos: Pos2D = Pos2D(col_i, row_i)

                if (pos.x == 0 and (
                        pos.y == 0 or pos.y == Board._NUM_ROWS - 1) or
                        pos.x == Board._NUM_COLS - 1 and (
                                pos.y == 0 or pos.y == Board._NUM_ROWS - 1)):
                    squares[pos] = Square(pos, None, SquareState.CORNER)
                else:
                    squares[pos] = Square(pos, None, SquareState.OPEN)

        return squares

    @staticmethod
    def create_from_string(round_num: int, game_phase: GamePhase) -> 'Board':
        """
        This method takes a string (that is a representation of the board in x-y
        format) and returns a board object. This also defines the round number
        and the game phase for the board.
        """
        new_board: Board = Board(None, round_num, game_phase)
        for row_i in range(Board._NUM_ROWS):
            row_string: List[str] = input().split(" ")
            for col_i, char in enumerate(row_string):
                pos: Pos2D = Pos2D(col_i, row_i)
                if (char == SquareState.CORNER.get_representation()):
                    new_board.squares[pos] = \
                        Square(pos, None, SquareState.CORNER)
                elif (char == SquareState.OPEN.get_representation()):
                    new_board.squares[pos] = \
                        Square(pos, None, SquareState.OPEN)
                elif (char == Player.WHITE.get_representation()):
                    new_board.squares[pos] = \
                        Square(pos, Piece(Player.WHITE), SquareState.OCCUPIED)
                elif (char == Player.BLACK.get_representation()):
                    new_board.squares[pos] = \
                        Square(pos, Piece(Player.BLACK), SquareState.OCCUPIED)

        return new_board
