import random
from typing import List, Tuple, Dict, Union

from Classes.Board import Board
from Classes.Delta import Delta
from Classes.Pos2D import Pos2D
from Classes.Square import Square
from Enums.GamePhase import GamePhase
from Enums.PlayerColor import PlayerColor
from Misc.Utilities import Utilities as Utils


class Player():
    # TODO: Consider if we should weigh own player's pieces higher than enemies's.
    _WHITE_WEIGHT: float = 1.1
    _BLACK_WEIGHT: float = 1.0
    # Rating-decimal place rounding. Used to prevent floating point imprecision
    # from interfering with move decisions.
    _RATING_NUM_ROUNDING: int = 10
    _ALPHA_START_VALUE: int = -9999
    _BETA_START_VALUE: int = 9999
    _SEED: int = 2
    _DIST_WEIGHT: float = 0.001
    _PREPARE_TO_CENTER: int = 32

    # A reference to the current board that the agent is on.
    _board: Board
    _color: PlayerColor
    # The depth to go in each iteration of the iterative-deepening search
    # algorithm i.e. number of moves to look ahead.
    _depth: int = 1

    def __init__(self, color: str):
        """
        TODO
        This method is called by the referee once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the board, and any other state you would like to maintain for the
        duration of the game.
        The input parameter colour is a string representing the piece colour your program
        will control for this game. It can take one of only two values: the string 'white' (if
        you are the White player for this game) or the string 'black' (if you are the Black
        player for this game).
        """

        self._board = Board(None, 0, GamePhase.PLACEMENT)
        if (color.lower() == "white"):
            self._color = PlayerColor.WHITE
        else:
            self._color = PlayerColor.BLACK

        random.seed(Player._SEED)

    def action(self, turns) -> str:
        """
        This method is called by the referee to request an action by your player.
        The input parameter turns is an integer representing the number of turns that have
        taken place since the start of the current game phase. For example, if White player
        has already made 11 moves in the moving phase, and Black player has made 10
        moves (and the referee is asking for its 11th move), then the value of turns would
        be 21.
        Based on the current state of the board, your player should select its next action
        and return it. Your player should represent this action based on the instructions
        below, in the ‘Representing actions’ section.
        """

        deltas: List[Delta] = self._board.get_all_valid_moves(self._color)
        delta_scores: Dict[Delta, float] = {}

        for delta in deltas:
            delta_scores[delta] = \
                Player.get_alpha_beta_value(
                    self._board.get_next_board(delta), Player._depth - 1,
                    Player._ALPHA_START_VALUE,
                    Player._BETA_START_VALUE, self._color.opposite())

        best_deltas: List[Delta] = Utils.get_best_deltas(delta_scores, self._color)
        best_delta: Tuple[Delta, float]
        if (len(best_deltas) > 1):
            # There are more than one "best" deltas. Pick a random one.
            best_delta = random.choice(list(best_deltas))
        else:
            best_delta = best_deltas[0]

        self._board = self._board.get_next_board(best_delta[0])

        print(self._color, "DOES", best_delta[0], "[{}]".format(best_delta[1]))
        return best_delta[0].get_referee_form()

    def update(self, action: Tuple[Union[int, Tuple[int]]]):
        """
        This method is called by the referee to inform your player about the opponent’s
        most recent move, so that you can maintain your internal board configuration.
        The input parameter action is a representation of the opponent’s recent action
        based on the instructions below, in the ‘Representing actions’ section.
        This method should not return anything.
        Note: update() is only called to notify your player about the opponent’s actions.
        Your player will not be notified about its own actions.

        - To represent the action of placing a piece on square (x,y), use a tuple (x,y).
        - To represent the action of moving a piece from square (a,b) to square (c,d), use
        a nested tuple ((a,b),(c,d)).
        - To represent a forfeited turn, use the value None.
        """

        # TODO
        # Easiest way to generate a Delta from 'action' seems to be to use
        # board.get_valid_movements or board.get_valid_placements and then
        # "getting" the Delta being made by matching the Pos2Ds.

        print(self._color, "SEES", action)

        if (action is None):
            # Opponent forfeited turn.
            self._board.round_num += 1
            self._board._update_game_phase()

        positions: List[Pos2D]

        if (type(action[0]) == int):
            positions = [Pos2D(action[0], action[1])]
        else:
            positions = [Pos2D(x, y) for x, y in action]

        opponent_delta: Delta = None
        deltas: List[Delta]
        if (len(positions) == 1):
            # Placement
            assert(self._board.phase == GamePhase.PLACEMENT)

            deltas = self._board.get_valid_placements(self._color.opposite())

            for delta in deltas:
                if delta.move_target.pos == positions[0]:
                    opponent_delta = delta
                    break

        elif (len(positions) == 2):
            # Movement.
            assert(self._board.phase == GamePhase.MOVEMENT)

            deltas = self._board.get_valid_movements(positions[0])

            for delta in deltas:
                if delta.move_target.pos == positions[1]:
                    opponent_delta = delta
                    break

        assert(opponent_delta is not None)

        self._board = self._board.get_next_board(opponent_delta)

    @staticmethod
    def get_alpha_beta_value(board: Board, depth: int, alpha: float, beta: float, color: PlayerColor) -> float:
        if (depth == 0 or board.phase == GamePhase.FINISHED):
            return Player.get_heuristic_value(board)

        if (color == PlayerColor.WHITE): # Maximizer
            v: float = -999999
            deltas: List[Delta] = board.get_all_valid_moves(color)
            for delta in deltas:
                v = max(v, Player.get_alpha_beta_value(board.get_next_board(delta), depth - 1, alpha, beta, color.opposite()))
                alpha = max(alpha, v)
                if (beta <= alpha):
                    break
            return v

        else: # Minimizer
            v = 999999
            deltas: List[Delta] = board.get_all_valid_moves(color)
            for delta in deltas:
                v = min(v, Player.get_alpha_beta_value(board.get_next_board(delta), depth - 1, alpha, beta, color.opposite()))
                beta = min(beta, v)
                if (beta <= alpha):
                    break
            return v

    @staticmethod
    def get_heuristic_value(board: Board):
        """
        Given a board, calculates and returns its rating based on heuristics.
        This heuristic applies both the Aggressive and Defensive tactic, where the pieces

        """

        # Get our squares
        white_squares: List[Square] = board.get_player_squares(PlayerColor.WHITE)
        black_squares: List[Square] = board.get_player_squares(PlayerColor.BLACK)


        # Apply the defensive center movement if the board is shrinking, otherwise
        # apply the aggressive "move towards enemies" strategy
        manhattan_dist_sum: int = 0
        if board.round_num > board.death_zone_rounds[0]-Player._PREPARE_TO_CENTER:
            for white_square in white_squares:
                manhattan_dist_center_avg: float = 0
                count: int = 1
                for center_square in board.center_zone:
                    if center_square != white_square.pos:
                        count += 1
                        displacement_center: Pos2D = (center_square - white_square.pos)
                        manhattan_dist_center_avg += abs(displacement_center.x) + abs(displacement_center.y)
                manhattan_dist_sum += manhattan_dist_center_avg/count
        else:
            if (len(black_squares) > 0):
                black_square: Square = black_squares[0]
                for white_square in white_squares:
                    displacement: Pos2D = (black_square.pos - white_square.pos)
                    manhattan_dist_sum += abs(displacement.x) + abs(displacement.y)

        # Calculate the number of white and black pieces. This is a very
        # important heuristic that will help prioritize preserving white's own
        # pieces and killing the enemy's black pieces.
        num_white_pieces: int = len(white_squares)
        num_black_pieces: int = len(black_squares)

        # Return the heuristic rating by using the appropriate weights.
        if board.phase != GamePhase.PLACEMENT:
            return round(Player._WHITE_WEIGHT * num_white_pieces
                         - Player._BLACK_WEIGHT * num_black_pieces
                         - Player._DIST_WEIGHT * manhattan_dist_sum,
                         Player._RATING_NUM_ROUNDING)
        else:
            return round(Player._WHITE_WEIGHT * num_white_pieces
                         - Player._BLACK_WEIGHT * num_black_pieces,
                         Player._RATING_NUM_ROUNDING)
