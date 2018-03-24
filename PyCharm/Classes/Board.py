from copy import deepcopy
from typing import List, Dict, Tuple, Optional

from Classes.Delta import Delta
from Classes.Piece import Piece
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.GamePhase import GamePhase
from Enums.Player import Player
from Enums.SquareState import SquareState


class Board():
    """
    A structure that represents the board at a given point.
    """
    # TODO Move these into Utilities? Elsewhere?
    _TOP_LEFT: str = "top left"
    _TOP_RIGHT: str = "top right"
    _BOTTOM_LEFT: str = "bottom left"
    _BOTTOM_RIGHT: str = "bottom right"
    _HORIZONTAL: str = "horizontal"
    _VERTICAL: str = "vertical"
    _OMNI: str = "omnidirectional" # TODO Better name?
    _NUM_COLS: int = 8
    _NUM_ROWS: int = 8
    # TODO: Better way to specify placement zone?
    _WHITE_PLACEMENT_ZONE_CORNER_POSITIONS: List[Pos2D] = [Pos2D(0, 0), Pos2D(_NUM_COLS, _NUM_ROWS - 2)]
    _BLACK_PLACEMENT_ZONE_CORNER_POSITIONS: List[Pos2D] = [Pos2D(0, 2), Pos2D(_NUM_COLS, _NUM_ROWS)]
    _MOVING_PHASE_ROUND_START = 24
    _DEATH_ZONE_ROUNDS: List[int] = [128, 192]
    _MIN_NUM_PIECES_BEFORE_LOSS = 2

    # Structure that contains the squares.
    squares: Dict[Pos2D, Square]
    # round_num is not the turn number. e.g. after each player has had a turn, then round_num == 3.
    round_num: int
    # An enum used to indicate the current phase of the game.
    phase: GamePhase
    # Equals None while the game isn't done. If phase == FINISHED and winner == None, that the game was a tie.
    winner: Player

    def __init__(self, squares: Optional[Dict[Pos2D, Square]], round_num: int, phase: GamePhase, winner: Player = None):
        if (squares == None):
            self.squares = self._init_squares()
        else:
            self.squares = squares

        self.round_num = round_num
        self.phase = phase
        self.winner = winner

    def get_valid_placements(self, player: Player) -> List[Delta]:
        """
        TODO
        :return:
        """

        player_zone_corner_positions: List[Pos2D]
        if (player == Player.WHITE):
            player_zone_corner_positions = Board._WHITE_PLACEMENT_ZONE_CORNER_POSITIONS
        else:
            player_zone_corner_positions = Board._BLACK_PLACEMENT_ZONE_CORNER_POSITIONS

        # Get a list of all valid squares in the zone that the given player is allowed to place pieces.
        valid_squares: List[Square] = \
            [square for square in
             self._select_squares(player_zone_corner_positions[0], player_zone_corner_positions[1] + Pos2D(-1, -1)) if
             square.state == SquareState.OPEN]

        return [Delta(player, None, square, self._get_killed_squares(Piece(player), square.pos), [], []) for square in valid_squares]

    def get_valid_moves(self, pos: Pos2D) -> List[Delta]:
        """
        :param pos:
        :return:
        """
        valid_moves: List[Delta] = []

        potential_square_eliminations: List[Square] = []
        potential_new_corners: List[Square] = []
        if (self.round_num in Board._DEATH_ZONE_ROUNDS):
            (potential_square_eliminations, potential_new_corners) = self._get_death_zone_square_changes()

        surrounding_squares: List[Square] = self._get_surrounding_squares(pos)
        for surrounding_square in surrounding_squares:
            if (surrounding_square.state == SquareState.OPEN):
                move_origin: Square = self.squares[pos]
                move_target: Square = surrounding_square
                potential_kills: List[Pos2D] = self._get_killed_squares(move_origin.occupant, move_target.pos)
                delta: Delta = Delta(self.squares[pos].occupant.owner, move_origin, move_target, potential_kills,
                                     potential_square_eliminations, potential_new_corners)
                valid_moves.append(delta)

        return valid_moves

    def get_all_valid_moves(self, player: Player) -> List[Delta]:
        """
        Returns a list of all possible moves for a given player.
        """

        if (self.phase == GamePhase.PLACEMENT):
            return self.get_valid_placements(player)

        if (self.phase == GamePhase.MOVEMENT):
            valid_moves: List[Delta] = []

            # Get a list of all squares that are occupied by the given player.
            player_squares: List[Square] = self._get_player_squares(player)
            # Iterate over each of these squares and add their valid moves to 'valid_moves'.
            [valid_moves.extend(self.get_valid_moves(square.pos)) for square in player_squares]

            return valid_moves

        raise ValueError("Game is finished. Neither player can move.")

    def get_next_board(self, delta: Delta) -> 'Board':
        """
        TODO
        :param delta:
        :return:
        """

        # Sanity checks to ensure we're calling the method correctly.
        assert self.squares[delta.move_target.pos].state == SquareState.OPEN
        if (delta.move_origin != None):
            assert self.squares[delta.move_origin.pos].state == SquareState.OCCUPIED

        board_copy: Board = self.__deepcopy__()

        # Make sure that both the original and target squares are changed to reflect change in the given delta.
        if (delta.move_origin == None):
            # This delta is a placement.
            board_copy.squares[delta.move_target.pos].occupant = Piece(delta.player)
        else:
            # This delta is a movement.
            board_copy.squares[delta.move_target.pos].occupant = delta.move_origin.occupant
            board_copy.squares[delta.move_origin.pos].occupant = None
            board_copy.squares[delta.move_origin.pos].state = SquareState.OPEN

        board_copy.squares[delta.move_target.pos].state = SquareState.OCCUPIED

        for pos in delta.killed_square_positions:
            board_copy.squares[pos].occupant = None
            board_copy.squares[pos].state = SquareState.OPEN

        for square in delta.eliminated_squares: # TODO: Make eliminated squares and new_corners also lists of positions instead?
            board_copy.squares[square.pos].occupant = None
            board_copy.squares[square.pos].state = SquareState.ELIMINATED

        for square in delta.new_corners:
            board_copy.squares[square.pos].occupant = None
            board_copy.squares[square.pos].state = SquareState.CORNER

        board_copy._update_game_phase()
        board_copy.round_num += 1

        return board_copy

    def print(self):
        for col_i in range(Board._NUM_COLS):
            for row_i in range(Board._NUM_ROWS):
                pos: Pos2D = Pos2D(col_i, row_i)
                print("{} ".format(self.squares[pos].getRepresentation()), end="")
            # Finished row, print new line.
            print("")

    def _get_surrounding_squares(self, pos: Pos2D, direction: str = _OMNI) -> List[Square]:
        """
        Returns a list of max 4 squares which are directly adjacent (up, down, left, right) of the given position.
        Can specify if only surrounding squares in a certain direction are wanted using the 'direction' parameter.
        :param pos: The position which we want adjacent squares for.
        :return: A list of adjacent squares.
        """
        adjacent_squares: List[Square] = []
        if (direction == Board._OMNI):
            adjacent_squares.extend(self._get_surrounding_squares(pos, Board._HORIZONTAL))
            adjacent_squares.extend(self._get_surrounding_squares(pos, Board._VERTICAL))
        elif (direction == Board._HORIZONTAL):
            adjacent_squares = [self.squares.get(pos + Pos2D(1, 0)), self.squares.get(pos + Pos2D(-1, 0))]
        elif (direction == Board._VERTICAL):
            adjacent_squares = [self.squares.get(pos + Pos2D(0, 1)), self.squares.get(pos + Pos2D(0, -1))]

        return [square for square in adjacent_squares if square != None]

    def _get_killed_squares(self, moving_piece: Piece, moving_piece_pos: Pos2D) -> List[Pos2D]:
        """
        TODO Mention about how it handles the moving piece being killed.
        :param moving_piece:
        :param moving_piece_pos:
        :return:
        """
        killed_positions: List[Pos2D] = []

        # Short for 'horizontally surrounding squares'.
        horiz_surr_squares: List[Square] = self._get_surrounding_squares(moving_piece_pos, Board._HORIZONTAL)
        vert_surr_squares: List[Square] = self._get_surrounding_squares(moving_piece_pos, Board._VERTICAL)

        # Add any surrounding squares that would be killed if the given piece moved to the given location.
        for surrounding_square in [*horiz_surr_squares, *vert_surr_squares]:
            if (surrounding_square.state == SquareState.OCCUPIED and
                    surrounding_square.occupant.owner != moving_piece.owner):
                delta_pos: Pos2D = surrounding_square.pos - moving_piece_pos
                opposite_square: Square = self.squares.get(surrounding_square.pos + delta_pos)
                if (opposite_square != None and (opposite_square.state == SquareState.OCCUPIED and
                                                 opposite_square.occupant.owner == moving_piece.owner) or
                        opposite_square != None and opposite_square.state == SquareState.CORNER): # TODO Can this be written better?
                    killed_positions.append(surrounding_square.pos)

        # Now check if the piece that is moving gets killed. This would be a stupid move, but it could happen.

        # Remove references to surrounding squares if they are going to be killed, as they then cannot kill the moving
        # piece.
        [horiz_surr_squares.remove(self.squares[pos]) for pos in killed_positions if self.squares[pos] in horiz_surr_squares] # TODO: Make this nicer?
        [vert_surr_squares.remove(self.squares[pos]) for pos in killed_positions if self.squares[pos] in vert_surr_squares]

        # Filter out squares from both lists that are not occupied by enemy pieces.
        potential_horiz_killer_squares = [square for square in horiz_surr_squares if square.state == SquareState.OCCUPIED and
                                    square.occupant.owner != moving_piece.owner]
        potential_vert_killer_squares = [square for square in vert_surr_squares if square.state == SquareState.OCCUPIED and
                                    square.occupant.owner != moving_piece.owner]

        if (len(potential_horiz_killer_squares) == 2 or len(potential_vert_killer_squares) == 2):
            killed_positions.append(moving_piece_pos)

        return killed_positions

    def _get_player_squares(self, player: Player) -> List[Square]:
        """
        TODO
        :param player:
        :return:
        """
        return [square for square in self.squares.values() if
                square.state == SquareState.OCCUPIED and square.occupant.owner == player]

    def _get_death_zone_square_changes(self) -> Tuple[List[Square], List[Square]]:
        """
        TODO Does not seem to work correctly (see later rounds when printed).
        Does not take into account the round num. Simply returns a tuple of (eliminated squares : new corners).
        """

        eliminated_squares: List[Square] = []
        new_corners: List[Square] = []

        original_corners: Dict[str, Square] = self._get_corner_squares()
        eliminated_squares.extend(self._select_squares(original_corners[Board._TOP_LEFT].pos,
                                                       original_corners[Board._TOP_RIGHT].pos))
        eliminated_squares.extend(self._select_squares(original_corners[Board._TOP_RIGHT].pos,
                                                       original_corners[Board._BOTTOM_RIGHT].pos))
        eliminated_squares.extend(self._select_squares(original_corners[Board._BOTTOM_RIGHT].pos,
                                                       original_corners[Board._BOTTOM_LEFT].pos))
        eliminated_squares.extend(self._select_squares(original_corners[Board._BOTTOM_LEFT].pos,
                                                       original_corners[Board._TOP_LEFT].pos))

        new_corners.append(self.squares[original_corners[Board._TOP_LEFT].pos + Pos2D(1, 1)])
        new_corners.append(self.squares[original_corners[Board._TOP_RIGHT].pos + Pos2D(-1, 1)])
        new_corners.append(self.squares[original_corners[Board._BOTTOM_LEFT].pos + Pos2D(1, -1)])
        new_corners.append(self.squares[original_corners[Board._BOTTOM_RIGHT].pos + Pos2D(-1, -1)])

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
        corners[Board._TOP_RIGHT] = self.squares[top_left_corner.pos + Pos2D(dist_between_corners, 0)]
        corners[Board._BOTTOM_LEFT] = self.squares[top_left_corner.pos + Pos2D(0, dist_between_corners)]
        corners[Board._BOTTOM_RIGHT] = \
            self.squares[top_left_corner.pos + Pos2D(dist_between_corners, dist_between_corners)]

        return corners

    def _select_squares(self, top_left_corner: Pos2D, bottom_right_corner: Pos2D) -> List[Square]:
        """
        TODO: Make inclusive or exclusive?
        :param top_left_corner:
        :param bottom_right_corner:
        :return:
        """
        squares: List[Square] = []

        # + 1 so as to make the selection inclusive.
        for col_i in range(top_left_corner.x, bottom_right_corner.x + 1):
            for row_i in range(top_left_corner.y, bottom_right_corner.y + 1):
                squares.append(self.squares[Pos2D(col_i, row_i)])

        return squares

    def _update_game_phase(self):
        """
        TODO
        - Get num player pieces.
            - If either player has < 2 pieces, they lose.
            - If both players have < 2 pieces, it's a draw.
        :return:
        """

        if (self.round_num == Board._MOVING_PHASE_ROUND_START):
            self.phase = GamePhase.MOVEMENT

        if (self.phase == GamePhase.PLACEMENT):
            # We're still in the placement phase, so neither player can lose due to a lack of pieces on the board.
            # End the method call, making no changes to the phase.
            return

        player_square_counts: Dict[Player, int] = {Player.WHITE: len(self._get_player_squares(Player.WHITE)),
                                                   Player.BLACK: len(self._get_player_squares(Player.BLACK))}

        if (player_square_counts[Player.WHITE] < Board._MIN_NUM_PIECES_BEFORE_LOSS and
                player_square_counts[Player.BLACK] < Board._MIN_NUM_PIECES_BEFORE_LOSS):
            # Tie
            self.winner = None
            self.phase = GamePhase.FINISHED
        elif (player_square_counts[Player.BLACK] < Board._MIN_NUM_PIECES_BEFORE_LOSS):
            # White wins
            self.winner = Player.WHITE
            self.phase = GamePhase.FINISHED
        elif (player_square_counts[Player.WHITE] < Board._MIN_NUM_PIECES_BEFORE_LOSS):
            # Black wins
            self.winner = Player.BLACK
            self.phase = GamePhase.FINISHED

    def _init_squares(self) -> Dict[Pos2D, Square]:
        """
        TODO
        :return:
        """
        squares: Dict[Pos2D, Square] = {}
        for col_i in range(Board._NUM_COLS):
            for row_i in range(Board._NUM_ROWS):
                pos: Pos2D = Pos2D(col_i, row_i)

                if (pos.x == 0 and (pos.y == 0 or pos.y == Board._NUM_ROWS - 1) or
                        pos.x == Board._NUM_COLS - 1 and (pos.y == 0 or pos.y == Board._NUM_ROWS - 1)):
                    squares[pos] = Square(pos, None, SquareState.CORNER)
                else:
                    squares[pos] = Square(pos, None, SquareState.OPEN)

        return squares
    def __deepcopy__(self, memodict={}) -> 'Board':
        """
        Returns a deep copy of the calling instance. Necessary in order to ensure that different boards don't reference
        the same Square objects in memory.
        """
        squares: Dict[Pos2D, Square] = deepcopy(self.squares)
        round_num: int = self.round_num
        phase: GamePhase = self.phase
        winner: Player = self.winner

        return Board(squares, round_num, phase, winner)
