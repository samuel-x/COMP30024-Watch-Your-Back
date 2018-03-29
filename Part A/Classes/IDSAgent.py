import random
from typing import List, Tuple

from Classes.Board import Board
from Classes.Delta import Delta
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.GamePhase import GamePhase
from Enums.Player import Player


class IDSAgent:

    # When playing massacre, we don't want to sacrifice our own pieces to kill enemy pieces. Therefore, weigh white
    # pieces higher than black pieces.
    _WHITE_WEIGHT: float = 1.1
    _BLACK_WEIGHT: float = 1.0
    # How much to weigh the manhattan distance. We only want to weigh the manhattan distance enough for it to play
    # a role when there are no options to kill an enemy piece, hence the low weight.
    _DIST_WEIGHT: float = 0.001
    # We really don't want to repeat board states. When a repeat board is
    _REPEAT_BOARD: int = -99999
    # Rating-decimal place rounding. Used to prevent floating point imprecision from interfering with move decisions.
    _RATING_NUM_ROUNDING: int = 10
    # The length of the history of recent board states the agent can remember. Used to avoid repeat moves. Can be quiet
    # high, as each board (being represented by a string) does not take much memory.
    _BOARD_HISTORY_MEMORY: int = 512
    # The depth to go in each iteration of the iterative-deepening search algorithm. 0 indexed, i.e. 0 is depth of 1.
    _DEPTH: int = 1

    # A reference to the current board that the agent is on.
    _board: Board
    # A list of recent boards. Each board is stored in its string form, for memory and efficiency purposes.
    # This will allow us to check if a move results in a previous board, and therefore not perform that move, avoiding
    # endless loops in the process.
    _recent_board_history: List[str] = []

    def __init__(self, start_board: Board, seed: int = None):
        self._board = start_board
        if (seed != None):
            random.seed(seed)

    def massacre(self):
        """
        This method runs the algorithm until all enemy pieces are killed (or the game is over otherwise).
        This method uses a variant of iterative deepening search. All moves within '_DEPTH' + 1 levels will be explored,
        at which point the most promising move will be made. We then, again, evaluate all possible moves within
        '_DEPTH' + 1 levels, perform the best-rated move, etc etc.
        """
        print(self._board)

        # While the game is not finished, perform the algorithm.
        while (self._board.phase != GamePhase.FINISHED):
            # Evaluate all of the possible moves from this board.
            deltas: List[Delta] = self._board.get_all_valid_moves(Player.WHITE)
            # Shuffling the calculated deltas can assist in avoiding endless loops.
            random.shuffle(deltas)

            # Get the best move to perform. TODO: Before submission, only grab delta (no ratings)
            best_delta: Tuple[Delta, List[float]] = IDSAgent.get_best_delta(self._board, Player.WHITE, IDSAgent._DEPTH,
                                                                            self._recent_board_history)

            # Before performing the move, save the current board into the recent boards history list.
            self._recent_board_history = [str(self._board)] + self._recent_board_history[:IDSAgent._BOARD_HISTORY_MEMORY]

            # Perform the move, replacing the reference to the old board with the new one.
            self._board = self._board.get_next_board(best_delta[0])

            print("{:3}: {} ({})".format(self._board.round_num - 1, best_delta[0], best_delta[1]))
            print(self._board)

    @staticmethod
    def get_board_ratings(board: Board, depth: int, recent_board_history: List[str]) -> List[float]:
        """
        Returns a list of ratings for the given board of size 'depth' + 1. For example, if this function returns
        the this list: [2.2, 1.6, 1.7], that means that the given board is rated 1.7, the best board state from the
        given board is rated 1.6, and the best board state from that 1.6 board is rated 2.2. i.e. the list of ratings
        corresponds to levels as so: [depth, depth - 1, depth - 2, ... 0] where 0 is the given/current board's rating.
        By returning a list of ratings, we can better compare series of moves, particularly a series which results
        in the same state, but by different means e.g. 'kill enemy piece at (2, 2) then move to (2, 1)' vs 'move to
        (2, 1) then kill enemy piece at (2, 2)'. In this scenario, we can prioritize the former, thanks to the list
        of ratings being returned.
        :param board: The board from which we want to get board ratings.
        :param depth: The number of moves down the tree to explore.
        :param recent_board_history: A list of boards represented by strings used to avoid repeating previous board states,
                              avoiding endless loops in the process.
        :return: A list of ratings, as explained above.
        """

        # If the current board has been explored in recent board history, return the appropriate rating to discourage
        # its selection in a list e.g. [-99999].
        if (str(board) in recent_board_history):
            return [IDSAgent._REPEAT_BOARD]

        # If we're at the end of our search, either due to depth being equal to 0 or the board being marked as finished,
        # simply return the heuristic value of the board in a list.
        if (depth == 0 or board.phase == GamePhase.FINISHED):
            return [IDSAgent.get_heuristic_value(board)]

        # Evaluate all possible moves from this board and keep track of the best one.
        best_rating = IDSAgent.get_best_delta(board, Player.WHITE, depth, recent_board_history)[1]

        # Return the list of ratings from the best move and attach this given board's rating onto the end.
        return best_rating + [IDSAgent.get_heuristic_value(board)]

    @staticmethod
    def get_best_delta(board: Board, player: Player, depth: int, recent_board_history: List[str]) -> \
            Tuple[Delta, List[float]]:
        """
        Returns the highest-rated (or best) move from the current board for the given player, exploring 'depth' number
        of levels to determine the best move. recent_board_history helps avoid repeating board states. Along with
        the delta object for the best move, also returns a list of floats, containing the ratings for the series of
        moves used to rate the returned delta. This list is more thoroughly explained in the docs for
        'get_board_ratings'.
        """
        # Evaluate all of the possible moves from this board.
        deltas: List[Delta] = board.get_all_valid_moves(player)
        # Shuffling the calculated deltas can assist in avoiding endless loops, particularly if board states are being
        # repeated.
        random.shuffle(deltas)

        # Iterate through every valid move, rating them and keeping track of the best move along the way.
        best_delta: Tuple[Delta, List[float]] = (None, [-999999])
        for delta in deltas:
            delta_ratings: List[float] = IDSAgent.get_board_ratings(board.get_next_board(delta),
                                                                    depth - 1, recent_board_history)
            best_delta = max([best_delta,
                              (delta, delta_ratings)], key=lambda x: (x[1][0], -len(x[1]), x[1]))

        return best_delta

    @staticmethod
    def get_heuristic_value(board: Board):
        """
        Given a board, calculates and returns its rating based on heuristics.
        """
        # Get a list of all squares with white pieces and a list of squares with black pieces.
        white_squares: List[Square] = board.get_player_squares(Player.WHITE)
        black_squares: List[Square] = board.get_player_squares(Player.BLACK)

        # If there are any black pieces, calculate the sum of all white pieces' manhattan displacement to the first
        # black piece in the list. This piece will remain consistent until it is dead. This fixes the issue of white
        # pieces, when separated from the black pieces, not being able to find their way to the black pieces easily.
        manhattan_dist_sum: int = 0
        if (len(black_squares) > 0):
            black_square: Square = black_squares[0]
            for white_square in white_squares:
                difference: Pos2D = (black_square.pos - white_square.pos)
                manhattan_dist_sum += abs(difference.x) + abs(difference.y)

        # Calculate the number of white and black pieces. This is a very important heuristic that will help prioritize
        # preserving white's own pieces and killing the enemy's black pieces.
        num_white_pieces: int = len(white_squares)
        num_black_pieces: int = len(black_squares)

        # Return the heuristic rating by using the appropriate weights.
        return round(IDSAgent._WHITE_WEIGHT * num_white_pieces - \
                     IDSAgent._BLACK_WEIGHT * num_black_pieces - \
                     IDSAgent._DIST_WEIGHT * manhattan_dist_sum, IDSAgent._RATING_NUM_ROUNDING)