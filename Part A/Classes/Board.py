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
    # Directional/locational constants.
    _HORIZONTAL: str = "horizontal"
    _VERTICAL: str = "vertical"
    _OMNI: str = "omnidirectional"

    _NUM_COLS: int = 8
    _NUM_ROWS: int = 8
    _MIN_NUM_PIECES_BEFORE_LOSS = 1

    # Structure that contains the squares.
    squares: Dict[Pos2D, Square]
    # round_num is not the turn number. e.g. after each player has had a turn, then round_num == 3.
    round_num: int
    # An enum used to indicate the current phase of the game.
    phase: GamePhase

    def __init__(self, squares: Optional[Dict[Pos2D, Square]], round_num: int, phase: GamePhase):
        if (squares == None):
            self.squares = self._init_squares()
        else:
            self.squares = squares

        self.round_num = round_num
        self.phase = phase

    def get_num_moves(self, player: Player) -> int:
        """
        This method takes a player and returns the number of possible moves that they can take.
        This is required for Part A question 1 as defined in the spec.
        :param player:
        :return:
        """
        player_squares: List[Square] = self.get_player_squares(player)
        count: int = 0
        for player_square in player_squares:
            surr_squares = self._get_surrounding_squares(player_square.pos)
            for surr_square in surr_squares:
                if (surr_square.state == SquareState.OPEN):
                    count += 1
                elif(surr_square.state == SquareState.OCCUPIED):
                    opposite_square: Square = self.squares.get(self._get_opposite_pos(player_square.pos, surr_square.pos))
                    if (opposite_square != None and opposite_square.state == SquareState.OPEN):
                        count += 1

        return count

    def get_valid_movements(self, pos: Pos2D) -> List[Delta]:
        """
        This method takes a position on the board and returns a list of possible moves (or 'deltas') from that position.
        :param pos:
        :return:
        """
        valid_moves: List[Delta] = []

        surrounding_squares: List[Square] = self._get_surrounding_squares(pos)
        for surrounding_square in surrounding_squares:
            move_origin: Square
            move_target: Square

            if (surrounding_square.state == SquareState.OPEN):
                move_origin = self.squares[pos]
                move_target = surrounding_square
            elif (surrounding_square.state == SquareState.OCCUPIED):
                opposite_square: Square = self.squares.get(self._get_opposite_pos(pos, surrounding_square.pos))
                if (opposite_square != None and opposite_square.state == SquareState.OPEN):
                    move_origin = self.squares[pos]
                    move_target = opposite_square
                else:
                    continue
            else:
                continue

            potential_kills: List[Pos2D] = self._get_killed_positions(move_origin.occupant, move_target.pos)
            delta: Delta = Delta(self.squares[pos].occupant.owner, move_origin, move_target, potential_kills)
            valid_moves.append(delta)

        return valid_moves

    def get_all_valid_moves(self, player: Player) -> List[Delta]:
        """
        Returns a list of all possible moves for a given player.
        """
        valid_moves: List[Delta] = []

        # Get a list of all squares that are occupied by the given player.
        player_squares: List[Square] = self.get_player_squares(player)

        # Iterate over each of these squares and add their valid moves to 'valid_moves'.
        [valid_moves.extend(self.get_valid_movements(square.pos)) for square in player_squares]

        return valid_moves

    def get_next_board(self, delta: Delta) -> 'Board': # <- 'Board' Is this really normal?
        """
        This method takes a delta and creates a new board from this delta. This is used in order to update the game.
        :param delta:
        :return:
        """

        # Sanity checks to ensure we're calling the method correctly.
        assert self.squares[delta.move_target.pos].state == SquareState.OPEN
        assert self.squares[delta.move_origin.pos].state == SquareState.OCCUPIED

        board_copy: Board = self.__deepcopy__()

        # Make sure that both the original and target squares are changed to reflect change in the given delta.
        board_copy.squares[delta.move_target.pos].occupant = delta.move_origin.occupant
        board_copy.squares[delta.move_target.pos].state = SquareState.OCCUPIED
        board_copy.squares[delta.move_origin.pos].occupant = None
        board_copy.squares[delta.move_origin.pos].state = SquareState.OPEN

        for pos in delta.killed_square_positions:
            board_copy.squares[pos].occupant = None
            board_copy.squares[pos].state = SquareState.OPEN

        board_copy.round_num += 1
        board_copy._update_game_phase()

        return board_copy


    def get_player_squares(self, player: Player) -> List[Square]:
        """
        TODO
        :param player:
        :return:
        """
        return [square for square in self.squares.values() if
                square.state == SquareState.OCCUPIED and square.occupant.owner == player]

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

    def _check_opposite_squares(self, moving_piece: Piece, opposite_square: Square) -> bool:
        """
        This method checks opposite squares for enemy pieces or corners.
        :param moving_piece:
        :param opposite_square:
        :return:
        """
        return (opposite_square != None and
                    (opposite_square.state == SquareState.OCCUPIED and
                    opposite_square.occupant.owner == moving_piece.owner and
                    opposite_square.occupant != moving_piece) or
                        opposite_square != None and
                        opposite_square.state == SquareState.CORNER)

    def _get_killed_positions(self, moving_piece: Piece, moving_piece_target_pos: Pos2D) -> List[Pos2D]:
        """
        This method takes a piece that is moving and it's target position and calculates a list of positions
        where the piece will be killed by enemy pieces.
        TODO Mention about how it handles the moving piece being killed.
        :param moving_piece:
        :param moving_piece_target_pos:
        :return:
        """
        killed_positions: List[Pos2D] = []

        # Short for 'horizontally surrounding squares'.
        x_surround: List[Square] = self._get_surrounding_squares(moving_piece_target_pos, Board._HORIZONTAL)
        y_surround: List[Square] = self._get_surrounding_squares(moving_piece_target_pos, Board._VERTICAL)

        # Add any surrounding squares that would be killed if the given piece moved to the given location.
        for surrounding_square in [*x_surround, *y_surround]:
            if (surrounding_square.state == SquareState.OCCUPIED and
                    surrounding_square.occupant.owner != moving_piece.owner):
                opposite_square: Square = \
                    self.squares.get(self._get_opposite_pos(moving_piece_target_pos, surrounding_square.pos))
                if self._check_opposite_squares(moving_piece, opposite_square): # TODO Can this be written better?
                    killed_positions.append(surrounding_square.pos)

        # Now check if the piece that is moving gets killed. This would be a stupid move, but it could happen.

        # Remove references to surrounding squares if they are going to be killed, as they then cannot kill the moving
        # piece.
        [x_surround.remove(self.squares[pos]) for pos in killed_positions if self.squares[pos] in x_surround] # TODO: Make this nicer?
        [y_surround.remove(self.squares[pos]) for pos in killed_positions if self.squares[pos] in y_surround] # I looked up using Filter() instead but apparently it's recommended list comprehensions are better

        # Filter out squares from both lists that are not occupied by enemy pieces or aren't corners.
        potential_x_killer_squares = [square for square in x_surround if (square.state == SquareState.OCCUPIED and
                                    square.occupant.owner != moving_piece.owner) or square.state == SquareState.CORNER]
        potential_y_killer_squares = [square for square in y_surround if (square.state == SquareState.OCCUPIED and
                                    square.occupant.owner != moving_piece.owner) or square.state == SquareState.CORNER]

        if (len(potential_x_killer_squares) == 2 or len(potential_y_killer_squares) == 2):
            killed_positions.append(moving_piece_target_pos)

        return killed_positions

    def _get_opposite_pos(self, first_pos: Pos2D, second_pos: Pos2D) -> Pos2D:
        """
        TODO Better name?
        Always returns a Pos2D, regardless of if it marks a position off of the board, an eliminated square, etc.
        Takes two adjacent positions and returns the third if read in the order of first_pos -> second_pos -> third_pos.
        :param first_pos:
        :param second_pos:
        :return:
        """
        delta: Pos2D = second_pos - first_pos

        assert (abs(delta.x) + abs(delta.y)) == 1

        return second_pos + delta

    def _update_game_phase(self):
        """
        TODO
        - Get num player pieces.
            - If either player has < 2 pieces, they lose.
            - If both players have < 2 pieces, it's a draw.
        :return:
        """

        player_square_counts: Dict[Player, int] = {Player.WHITE: len(self.get_player_squares(Player.WHITE)),
                                                   Player.BLACK: len(self.get_player_squares(Player.BLACK))}
        if (player_square_counts[Player.WHITE] < Board._MIN_NUM_PIECES_BEFORE_LOSS or
            player_square_counts[Player.BLACK] < Board._MIN_NUM_PIECES_BEFORE_LOSS):
            self.phase = GamePhase.FINISHED

    def _init_squares(self) -> Dict[Pos2D, Square]:
        """
        This method creates all the squares in the board.
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

    def __str__(self):
        output: str = ""

        for row_i in range(Board._NUM_ROWS):
            for col_i in range(Board._NUM_COLS):
                pos: Pos2D = Pos2D(col_i, row_i)
                output += ("{} ".format(self.squares[pos].getRepresentation()))
            # Finished row, add new line.
            output += "\n"

        return output

    def __deepcopy__(self, memodict={}) -> 'Board':
        """
        Returns a deep copy of the calling instance. Necessary in order to ensure that different boards don't reference
        the same Square objects in memory.
        """
        squares: Dict[Pos2D, Square] = deepcopy(self.squares)
        round_num: int = self.round_num
        phase: GamePhase = self.phase

        return Board(squares, round_num, phase)

    @staticmethod
    def create_from_string(round_num: int, game_phase: GamePhase):
        """
        This method takes a string (that is a representation of the board in x-y format) and returns a board object.
        This also defines the round number and the game phase from the board.
        :param round_num:
        :param game_phase:
        :return:
        """
        new_board: Board = Board(None, round_num, game_phase)
        for row_i in range(Board._NUM_ROWS):
            row_string: List[str] = input().split(" ")
            for col_i, char in enumerate(row_string):
                pos: Pos2D = Pos2D(col_i, row_i)
                if (char == SquareState.CORNER.getRepresentation()):
                    new_board.squares[pos] = Square(pos, None, SquareState.CORNER)
                elif (char == SquareState.OPEN.getRepresentation()):
                    new_board.squares[pos] = Square(pos, None, SquareState.OPEN)
                elif (char == Player.WHITE.getRepresentation()):
                    new_board.squares[pos] = Square(pos, Piece(Player.WHITE), SquareState.OCCUPIED)
                elif (char == Player.BLACK.getRepresentation()):
                    new_board.squares[pos] = Square(pos, Piece(Player.BLACK), SquareState.OCCUPIED)

        return new_board
