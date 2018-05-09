from copy import deepcopy, copy
from typing import List, Dict, Tuple, Optional

from Classes.Delta import Delta
from Classes.Piece import Piece
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.GamePhase import GamePhase
from Enums.PlayerColor import PlayerColor
from Enums.SquareState import SquareState


class Board():
    """
    A structure that represents the board at a given point.
    """

    MOVING_PHASE_ROUND_START = 24

    # TODO Move these into Utilities? Elsewhere?
    _TOP_LEFT: str = "top left"
    _TOP_RIGHT: str = "top right"
    _BOTTOM_LEFT: str = "bottom left"
    _BOTTOM_RIGHT: str = "bottom right"
    _HORIZONTAL: str = "horizontal"
    _VERTICAL: str = "vertical"
    _OMNI: str = "omnidirectional"

    _NUM_COLS: int = 8
    _NUM_ROWS: int = 8

    # TODO: Better way to specify placement zone?
    _WHITE_PLACEMENT_ZONE_CORNER_POSITIONS: List[Pos2D] = \
        [Pos2D(0, 0), Pos2D(_NUM_COLS, _NUM_ROWS - 2)]
    _BLACK_PLACEMENT_ZONE_CORNER_POSITIONS: List[Pos2D] = \
        [Pos2D(0, 2), Pos2D(_NUM_COLS, _NUM_ROWS)]

    center_zone: List[Pos2D] = [Pos2D(_NUM_COLS % 2, _NUM_ROWS % 2), Pos2D(_NUM_COLS % 2, _NUM_ROWS % 2 + 1),
                                Pos2D(_NUM_COLS % 2 + 1, _NUM_ROWS % 2), Pos2D(_NUM_COLS % 2 + 1, _NUM_ROWS % 2 + 1)]

    death_zone_rounds: List[int] = [151, 215]

    # The minimum number of pieces a player can have on the board before they
    # lose.
    _MIN_NUM_PIECES_BEFORE_LOSS = 2

    # Structure that contains the squares as (position : square) pairs.
    squares: Dict[Pos2D, Square]
    # round_num is not the turn number. e.g. after each player has had a turn,
    # then round_num == 3.
    round_num: int
    # An enum used to indicate the current phase of the game.
    phase: GamePhase
    # Equals None while the game isn't done. If phase == FINISHED and winner is
    # None, that the game was a tie.
    winner: PlayerColor

    def __init__(self, squares: Optional[Dict[Pos2D, Square]], round_num: int,
                 phase: GamePhase, winner: PlayerColor = None):
        if (squares is None):
            self.squares = self._init_squares()
        else:
            self.squares = squares

        self.round_num = round_num
        self.phase = phase
        self.winner = winner

    def get_num_moves(self, player: PlayerColor) -> int:
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

    def get_valid_placements(self, player: PlayerColor) -> List[Delta]:
        """
        TODO
        :return:
        """

        player_zone_corner_positions: List[Pos2D]
        if (player == PlayerColor.WHITE):
            player_zone_corner_positions = \
                Board._WHITE_PLACEMENT_ZONE_CORNER_POSITIONS
        else:
            player_zone_corner_positions = \
                Board._BLACK_PLACEMENT_ZONE_CORNER_POSITIONS

        # Get a list of all valid squares in the zone that the given player is
        # allowed to place pieces.
        valid_squares: List[Square] = \
            [square for square in
             self._select_squares(player_zone_corner_positions[0],
                                  player_zone_corner_positions[1])
             if square.state == SquareState.OPEN]

        return [Delta(player, None, square,
                      self._get_killed_positions(Piece(player), square.pos), [],
                      []) for square in valid_squares]

    def get_possible_deltas(self, pos: Pos2D) -> List[Delta]:
        """
        Given a position on the board, returns a list of possible moves (or
        'deltas') from that position.
        """
        possible_deltas: List[Delta] = []

        potential_square_eliminations: List[Square] = []
        potential_new_corners: List[Square] = []
        if (self.round_num in Board.death_zone_rounds):
            (potential_square_eliminations, potential_new_corners) = \
                self._get_death_zone_changes()

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

            # Calculate kills that occur due to the change in corners
            # (if applicable).
            potential_corner_kills: List[Square] = []
            if (self.round_num in Board.death_zone_rounds):
                assert(len(potential_new_corners) == 4)

                for corner in potential_new_corners:
                    adj_occupied_squares: List[Square] = \
                        [square for square in
                         self._get_adjacent_squares(corner.pos) if
                         square.state == SquareState.OCCUPIED]
                    for adj_square in adj_occupied_squares:
                        opposite_square: Square = \
                            self.squares.get(self._get_opposite_pos(corner.pos,
                                                                    adj_square.pos))

                        if (opposite_square is None):
                            continue

                        # Edge case handling. If the delta involves moving to
                        # the opposite square, pretend it's already there.
                        if (opposite_square.pos == move_target.pos):
                            opposite_square = copy(opposite_square)
                            opposite_square.state = move_target.state
                            opposite_square.occupant = move_target.occupant

                        # First statement is edge case handling. If the delta
                        # involves moving away from the opposite square, it
                        # cannot killed adj_square.
                        if (opposite_square.pos != move_origin.pos
                                and opposite_square.state == SquareState.OCCUPIED
                                and adj_square.occupant.owner
                                != opposite_square.occupant.owner):
                            potential_corner_kills.append(adj_square)

            potential_kills: List[Pos2D] = \
                self._get_killed_positions(move_origin.occupant,
                                           move_target.pos) \
                + [square.pos for square in potential_corner_kills]
            # TODO Here, add function to assess kills from new corners.
            delta: Delta = Delta(self.squares[pos].occupant.owner, move_origin,
                                 move_target, potential_kills,
                                 potential_square_eliminations,
                                 potential_new_corners)
            possible_deltas.append(delta)

        return possible_deltas

    def get_all_valid_moves(self, player: PlayerColor) -> List[Delta]:
        """
        Returns a list of all possible moves for a given player.
        """

        if (self.phase == GamePhase.PLACEMENT):
            return self.get_valid_placements(player)

        if (self.phase == GamePhase.MOVEMENT):
            valid_moves: List[Delta] = []

            # Get a list of all squares that are occupied by the given player.
            player_squares: List[Square] = self._get_player_squares(player)
            # Iterate over each of these squares and add their valid moves to
            # 'valid_moves'.
            [valid_moves.extend(self.get_possible_deltas(square.pos)) for square
             in player_squares]

            return valid_moves

        assert (self.phase == GamePhase.FINISHED)
        raise ValueError("Game is finished. Neither player can move.")

    def get_next_board(self, delta: Delta) -> 'Board':
        """
        This method takes a delta and uses it to create a new board from the
        calling instance. This can be seen as actually making the move, once the
        move has been determined.
        """

        # Sanity checks to ensure we're calling the method correctly.
        assert (self.squares[delta.move_target.pos].state == SquareState.OPEN)
        if (delta.move_origin is not None):
            assert (self.squares[delta.move_origin.pos].state
                    == SquareState.OCCUPIED)

        next_board: Board = self.__deepcopy__()

        # Make sure that both the original and target squares are changed to
        # reflect change in the given delta.
        if (delta.move_origin is None):
            # This delta is a placement.
            next_board.squares[delta.move_target.pos].occupant = \
                Piece(delta.player)
        else:
            # This delta is a movement.
            next_board.squares[delta.move_target.pos].occupant = \
                delta.move_origin.occupant
            next_board.squares[delta.move_origin.pos].occupant = None
            next_board.squares[delta.move_origin.pos].state = SquareState.OPEN

        next_board.squares[delta.move_target.pos].state = SquareState.OCCUPIED

        # Update all the squares that had a killed piece.
        for pos in delta.killed_square_positions:
            next_board.squares[pos].occupant = None
            next_board.squares[pos].state = SquareState.OPEN

        for square in delta.eliminated_squares: # TODO: Make eliminated squares and new_corners also lists of positions instead?
            next_board.squares[square.pos].occupant = None
            next_board.squares[square.pos].state = SquareState.ELIMINATED

        for square in delta.new_corners:
            next_board.squares[square.pos].occupant = None
            next_board.squares[square.pos].state = SquareState.CORNER

        # Update the game state.
        next_board.round_num += 1
        next_board._update_game_phase()

        return next_board

    def get_player_squares(self, player: PlayerColor) -> List[Square]:
        """
        Returns a list of all squares that have a piece on them that is
        controlled by the given player.
        """
        return [square for square in self.squares.values() if
                square.state == SquareState.OCCUPIED
                and square.occupant.owner == player]

    def get_valid_block(self, pos: Pos2D, block_size: int=2) -> List[Pos2D]:
        """
        Returns a 2x2 Block of positions to be used in AlphaBetaPlayerTurtle
        :param pos:
        :return:
        """
        block_squares: List[Square] = [self.squares.get(pos)]
        for row in range(1, block_size):
            for col in range(1, block_size):
                block_squares.append(self.squares.get(pos + Pos2D(row, col)))

        return [square.pos for square in block_squares if square is not None]

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
            if (adjacent_square.state == SquareState.OCCUPIED
                    and adjacent_square.occupant.owner != moving_piece.owner):
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
        [x_adjacent.remove(self.squares[pos]) for pos in killed_positions if
         self.squares[pos] in x_adjacent]
        [y_adjacent.remove(self.squares[pos]) for pos in killed_positions if
         self.squares[pos] in y_adjacent]

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

    def _get_player_squares(self, player: PlayerColor) -> List[Square]:
        """
        TODO
        :param player:
        :return:
        """
        return [square for square in self.squares.values() if
                square.state == SquareState.OCCUPIED
                and square.occupant.owner == player]

    def _get_death_zone_changes(self) -> Tuple[List[Square], List[Square]]:
        """
        TODO
        Does not take into account the round num. Simply returns a tuple of
        (eliminated squares : new corners).
        """

        eliminated_squares: List[Square] = []
        new_corners: List[Square] = []

        original_corners: Dict[str, Square] = self._get_corner_squares()
        eliminated_squares.extend(
            self._select_squares(original_corners[Board._TOP_LEFT].pos,
                                 original_corners[Board._TOP_RIGHT].pos,
                                 offset = Pos2D(0, 1)))
        eliminated_squares.extend(
            self._select_squares(original_corners[Board._TOP_RIGHT].pos,
                                 original_corners[Board._BOTTOM_RIGHT].pos,
                                 offset = Pos2D(1, 1)))
        eliminated_squares.extend(
            self._select_squares(original_corners[Board._BOTTOM_LEFT].pos,
                                 original_corners[Board._BOTTOM_RIGHT].pos,
                                 offset = Pos2D(0, 1)))
        # TODO Consider that this means that top left will be in eliminated_squares TWICE due to the first argument
        # to _select_squares always being inclusive.
        eliminated_squares.extend(
            self._select_squares(original_corners[Board._TOP_LEFT].pos,
                                 original_corners[Board._BOTTOM_LEFT].pos,
                                 offset=Pos2D(1, 0)))

        new_corners.append(
            self.squares[original_corners[Board._TOP_LEFT].pos
                         + Pos2D(1, 1)])
        new_corners.append(
            self.squares[original_corners[Board._TOP_RIGHT].pos
                         + Pos2D(-1, 1)])
        new_corners.append(
            self.squares[original_corners[Board._BOTTOM_LEFT].pos
                         + Pos2D(1, -1)])
        new_corners.append(
            self.squares[original_corners[Board._BOTTOM_RIGHT].pos
                         + Pos2D(-1, -1)])



        return (eliminated_squares, new_corners)

    def _get_corner_squares(self) -> Dict[str, Square]:
        """
        TODO
        :return:
        """
        corners: Dict[str, Square] = {}
        counter: int = 0
        top_left_corner: Square = self.squares[Pos2D(counter, counter)]
        while (top_left_corner.state != SquareState.CORNER):
            counter += 1
            top_left_corner = self.squares[Pos2D(counter, counter)]

        corners[Board._TOP_LEFT] = top_left_corner
        dist_between_corners: int = Board._NUM_COLS - 2 * counter - 1
        corners[Board._TOP_RIGHT] = \
            self.squares[top_left_corner.pos
                         + Pos2D(dist_between_corners, 0)]
        corners[Board._BOTTOM_LEFT] = \
            self.squares[top_left_corner.pos
                         + Pos2D(0, dist_between_corners)]
        corners[Board._BOTTOM_RIGHT] = \
            self.squares[top_left_corner.pos
                         + Pos2D(dist_between_corners, dist_between_corners)]

        return corners

    def _select_squares(self, top_left_corner: Pos2D,
                        bottom_right_corner: Pos2D,
                        offset: Pos2D = Pos2D(0, 0)) -> List[Square]:
        """
        TODO: Make inclusive or exclusive? <- Kind of handled by offset, might be ugly though.
        :param top_left_corner:
        :param bottom_right_corner:
        :return:
        """
        squares: List[Square] = []

        # offset can make the selection inclusive.
        for row_i in range(top_left_corner.y, bottom_right_corner.y + offset.y):
            for col_i in range(top_left_corner.x, bottom_right_corner.x
                                                  + offset.x):
                squares.append(self.squares[Pos2D(col_i, row_i)])

        return squares

    def _update_game_phase(self):
        """
        Checks the current state of the game and the board to determine if the
        game phase should change (and then makes that change).
        """

        if (self.round_num == Board.MOVING_PHASE_ROUND_START):
            self.phase = GamePhase.MOVEMENT

        if (self.phase == GamePhase.PLACEMENT):
            # We're still in the placement phase, so neither player can lose due
            # to a lack of pieces on the board. End the method call, making no
            # changes to the phase.
            return

        player_square_counts: Dict[PlayerColor, int] = \
            {PlayerColor.WHITE: len(self._get_player_squares(PlayerColor.WHITE)),
             PlayerColor.BLACK: len(self._get_player_squares(PlayerColor.BLACK))}

        if (player_square_counts[PlayerColor.WHITE]
                < Board._MIN_NUM_PIECES_BEFORE_LOSS
                and player_square_counts[PlayerColor.BLACK]
                < Board._MIN_NUM_PIECES_BEFORE_LOSS):
            # Tie
            self.winner = None
            self.phase = GamePhase.FINISHED
        elif (player_square_counts[PlayerColor.BLACK]
              < Board._MIN_NUM_PIECES_BEFORE_LOSS):
            # White wins
            self.winner = PlayerColor.WHITE
            self.phase = GamePhase.FINISHED
        elif (player_square_counts[PlayerColor.WHITE]
              < Board._MIN_NUM_PIECES_BEFORE_LOSS):
            # Black wins
            self.winner = PlayerColor.BLACK
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
        winner: PlayerColor = self.winner

        return Board(squares, round_num, phase, winner)

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
                elif (char == PlayerColor.WHITE.get_representation()):
                    new_board.squares[pos] = \
                        Square(pos, Piece(PlayerColor.WHITE),
                               SquareState.OCCUPIED)
                elif (char == PlayerColor.BLACK.get_representation()):
                    new_board.squares[pos] = \
                        Square(pos, Piece(PlayerColor.BLACK),
                               SquareState.OCCUPIED)

        return new_board

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