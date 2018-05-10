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
    # --- Heuristic Weights ---
    # TODO: Consider if we should weigh own player's pieces higher than enemies's.
    _OWN_PIECE_WEIGHT: float = 1.0
    _OPPONENT_PIECE_WEIGHT: float = -1.0

    # Don't want to prioritize mobility over pieces, so it's much smaller.
    _OWN_MOBILITY_WEIGHT: float = 0.01
    _OPPONENT_MOBILITY_WEIGHT: float = -0.01

    # TODO: How to balance cohesiveness and mobility? They're opposing, in a way.
    _OWN_DIVIDED_WEIGHT: float = -0.001 # Bad to be divided. Want to be cohesive!
    _OPPONENT_DIVIDED_WEIGHT: float = 0.001 # Good for opponent to be divided.

    # Heuristic score decimal place rounding. Used to prevent floating point
    # imprecision from interfering with move decisions.
    _RATING_NUM_ROUNDING: int = 10

    _ALPHA_START_VALUE: int = -9999
    _BETA_START_VALUE: int = 9999
    _SEED: int = 1337

    # A reference to the current board that the agent is on.
    _board: Board
    _color: PlayerColor
    # The depth to go in each iteration of the iterative-deepening search
    # algorithm i.e. number of moves to look ahead.
    _depth: int = 2

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

        deltas: List[Delta] = self._board.get_all_possible_deltas(self._color)
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

            deltas = self._board.get_possible_placements(self._color.opposite())

            for delta in deltas:
                if delta.move_target.pos == positions[0]:
                    opponent_delta = delta
                    break

        elif (len(positions) == 2):
            # Movement.
            assert(self._board.phase == GamePhase.MOVEMENT)

            deltas = self._board.get_possible_deltas(positions[0])

            for delta in deltas:
                if delta.move_target.pos == positions[1]:
                    opponent_delta = delta
                    break

        assert(opponent_delta is not None)

        self._board = self._board.get_next_board(opponent_delta)

    @staticmethod
    def get_alpha_beta_value(board: Board, depth: int, alpha: float, beta: float, color: PlayerColor) -> float:
        if (depth == 0 or board.phase == GamePhase.FINISHED):
            return Player.get_heuristic_value(board, color)

        if (color == PlayerColor.WHITE): # Maximizer
            v: float = -999999
            deltas: List[Delta] = board.get_all_possible_deltas(color)
            for delta in deltas:
                v = max(v, Player.get_alpha_beta_value(board.get_next_board(delta), depth - 1, alpha, beta, color.opposite()))
                alpha = max(alpha, v)
                if (beta <= alpha):
                    break
            return v

        else: # Minimizer
            v = 999999
            deltas: List[Delta] = board.get_all_possible_deltas(color)
            for delta in deltas:
                v = min(v, Player.get_alpha_beta_value(board.get_next_board(delta), depth - 1, alpha, beta, color.opposite()))
                beta = min(beta, v)
                if (beta <= alpha):
                    break
            return v

    @staticmethod
    def get_heuristic_value(board: Board, player: PlayerColor):
        """
        Given a board, calculates and returns its rating based on heuristics.
        """

        player_squares: List[Square] = board.get_player_squares(player)
        opponent_squares: List[Square] = board.get_player_squares(player.opposite())

        # -- Num pieces --
        # Calculate the number of white and black pieces. This is a very
        # important heuristic that will help prioritize preserving white's own
        # pieces and killing the enemy's black pieces.
        num_own_pieces: int = len(player_squares)
        num_opponent_pieces: int = len(opponent_squares)

        # -- Mobility --
        # Calculate the mobility for both white and black i.e. the number of
        # possible moves they can make.
        own_mobility: int = board.get_num_moves(player)
        opponent_mobility: int = board.get_num_moves(player.opposite())

        # -- Cohesiveness --
        own_total_distance: int = 0
        opponent_total_distance: int = 0

        displacement: Pos2D
        for idx, square1 in enumerate(player_squares):
            for square2 in player_squares[idx + 1:]:
                displacement = square1.pos - square2.pos
                own_total_distance += abs(displacement.x) + abs(displacement.y)

        for idx, square1 in enumerate(opponent_squares):
            for square2 in opponent_squares[idx + 1:]:
                displacement = square1.pos - square2.pos
                opponent_total_distance += abs(displacement.x) + abs(displacement.y)

        own_avg_distance: float = own_total_distance / (num_own_pieces + 1)
        opponent_avg_distance: float = opponent_total_distance / (num_opponent_pieces + 1)

        # Calculate the heuristic score/rating.
        rounded_heuristic_score: float = round(
            Player._OWN_PIECE_WEIGHT * num_own_pieces
            + Player._OPPONENT_PIECE_WEIGHT * num_opponent_pieces
            + Player._OWN_MOBILITY_WEIGHT * own_mobility
            + Player._OPPONENT_MOBILITY_WEIGHT * opponent_mobility
            + Player._OWN_DIVIDED_WEIGHT * own_avg_distance
            + Player._OPPONENT_DIVIDED_WEIGHT * opponent_avg_distance,
            Player._RATING_NUM_ROUNDING)

        # Return the score as is or negate, depending on the player.
        # For white, return as is. For black, negate.
        return rounded_heuristic_score if player == PlayerColor.WHITE \
            else -rounded_heuristic_score
