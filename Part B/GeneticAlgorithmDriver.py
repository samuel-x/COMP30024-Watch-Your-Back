"""
Referee for COMP30024 Artificial Intelligence, 2018
Authors: Matt Farrugia and Shreyash Patodia
version: v1.2
"""

import argparse
import gc
import importlib
import random
import time
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from typing import List, Dict

import multiprocessing
from numpy import mean
from numpy.random import choice

from GeneticPlayer import Player

VERSION_INFO = """Referee version 1.2 (released May 07 2018)
Plays a basic game of Watch Your Back! between two Player classes
Allows for resource limiting to simulate performance constraints used in marking
Run `python referee.py -h` for help and additional usage information
"""

def main():
    SEED: int = 33
    random.seed(SEED)
    time_out: float = 10.0
    MAX_TIMEOUT: float = 60.0
    ARTIFICIAL_HEURISTICS = [1, -1, 0.01, -0.01, -0.001, 0.001, -0.005, 0.005]

    N: int = 10 # Population size.
    NUM_HEURISTIC_VALUES: int = 8 # Number of heuristic values.
    NUM_GAMES_PER_GENERATION: int = 100
    NUM_GAMES_PER_PLAYER_PER_GENERATION = round_even(NUM_GAMES_PER_GENERATION / (N * (N - 1) / 2))
    NUM_PARENTS: int = 3
    MUTATION_RATE: float = 0.05
    print("NUM_GAMES_PER_PLAYER_PER_GENERATION:", NUM_GAMES_PER_PLAYER_PER_GENERATION)
    population: Dict[int, PlayerWrapper] = {}

    # Generate initial population.
    heuristic_weights: List[float]
    new_wrapper: PlayerWrapper
    for i in range(N - 1):
        heuristic_weights = [random.uniform(-1, 1) for i in range(NUM_HEURISTIC_VALUES)]
        new_wrapper = PlayerWrapper(heuristic_weights)
        population[new_wrapper.id] = new_wrapper

    # Insert custom player.
    new_wrapper = PlayerWrapper(ARTIFICIAL_HEURISTICS)
    population[new_wrapper.id] = new_wrapper

    pool: Pool = Pool(11)
    processes: List[ApplyResult]
    generation_counter = 1
    while(True):
        print("\nGeneration:", generation_counter)
        # Generate the processes for each game to be played on.
        player_wrappers: List[PlayerWrapper] = list(population.values())
        processes = []
        for idx, player1 in enumerate(player_wrappers):
            for player2 in player_wrappers[idx + 1:]:
                for i in range(NUM_GAMES_PER_PLAYER_PER_GENERATION):
                    process: ApplyResult
                    if (i % 2 == 0):
                        print("Playing:", player1.id, player2.id, "player1 as white")
                        process = pool.apply_async(simulate_game, (player1, player2, i, len(processes)))
                    else:
                        print("Playing:", player1.id, player2.id, "player1 as black")
                        process = pool.apply_async(simulate_game, (player2, player1, i, len(processes)))
                    processes.append(process)

        print("Num games to play:", len(processes))

        # Get results.
        results = []
        timed_out: bool = False
        counter: int = 0
        while (counter < len(processes)):
            try:
                print("Getting {} at {:2f} seconds timeout...".format(counter, time_out))
                results.append(processes[counter].get(time_out))
                print("Got {}.".format(counter))
                time_out *= 0.98 # Decrease timeout by 2%.
                timed_out = False
            except multiprocessing.TimeoutError:
                if (timed_out):
                    print(counter, "timed out x2 - abandoning game.")
                    results.append(("SKIP", "SKIP", "SKIP", "SKIP", "SKIP"))
                    timed_out = False
                else:
                    time_out = min(time_out * 2, MAX_TIMEOUT)  # Double timeout and try again.
                    print(counter, "timed out x1 - retrying simulation.")
                    timed_out = True
                    counter -= 1

            counter += 1

        assert (len(results) == len(processes))

        # Evaluate results as the threads complete.
        for (player1_id, player2_id, i, answer, _) in results:
            if (answer == "SKIP"):
                continue

            if (answer == "W" and i % 2 == 0):
                population[player1_id].wins += 1
                population[player2_id].losses += 1
            elif(answer == "B" and i % 2 == 0):
                population[player2_id].wins += 1
                population[player1_id].losses += 1
            elif(answer == "W" and i % 2 == 1):
                population[player2_id].wins += 1
                population[player1_id].losses += 1
            elif(answer == "B" and i % 2 == 1):
                population[player1_id].wins += 1
                population[player2_id].losses += 1
            elif(answer == "draw"):
                population[player1_id].wins += 0.5
                population[player1_id].losses += 0.5
                population[player2_id].wins += 0.5
                population[player2_id].losses += 0.5

        # Calculate win rates i.e. fitness scores.
        for player in player_wrappers:
            player.win_rate = player.wins / (player.wins + player.losses)

        # Print fitness scores and parameters.
        print("Rank:")
        sorted_players: List[PlayerWrapper] = sorted(player_wrappers, key=lambda x: x.win_rate, reverse=True)
        for player in sorted_players:
            print("ID: {} | WR: {:4f} | Param: {}".format(player.id, player.win_rate, ["{:8f}".format(param) for param in player.parameters]))

        # Calculate probability of each class being a parent (derived from win rate).
        sum_win_rates: float = sum(player.win_rate for player in sorted_players)
        parent_probabilities: List[float] = []
        parent_probability: float
        for player in sorted_players:
            parent_probability = player.win_rate / sum_win_rates
            print("Parent probability: {:8f}".format(parent_probability))
            parent_probabilities.append(parent_probability)

        # Reproduction/Selection
        new_population: Dict[int, PlayerWrapper] = {}
        for i in range(N):
            parents: List[PlayerWrapper] = choice(sorted_players, NUM_PARENTS, p=parent_probabilities)
            child_parameters: List[float] = []
            for j in range(NUM_HEURISTIC_VALUES):
                parent_values: List[float] = [parent.parameters[j] for parent in parents]
                # Crossover
                child_value: float = mean(parent_values)
                # Mutate
                child_value *= random.uniform(1 - MUTATION_RATE, 1 + MUTATION_RATE)
                child_parameters.append(child_value)

            child_wrapper: PlayerWrapper = PlayerWrapper(child_parameters)
            new_population[child_wrapper.id] = child_wrapper

        # Insert custom wrapper.
        if (generation_counter % 5 == 0):
            del(new_population[child_wrapper.id])
            child_wrapper: PlayerWrapper = PlayerWrapper(ARTIFICIAL_HEURISTICS)
            new_population[child_wrapper.id] = child_wrapper

        population = new_population
        generation_counter += 1

class PlayerWrapper():
    _id: int = 0

    parameters: List[float]
    player: Player
    wins: float
    losses: float
    win_rate: float
    id: int

    def __init__(self, parameters: List[float]):
        self.parameters = parameters
        self.id = PlayerWrapper._id
        self.wins = 0.0
        self.losses = 0.0
        self.win_rate = 0.0
        PlayerWrapper._id += 1

    def make_player(self, color):
        return Player(color, self.parameters)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((self.id, "PlayerWrapper"))

def simulate_game(whiteWrapper: PlayerWrapper, blackWrapper: PlayerWrapper, i: int, game_count: int):
    """Coordinate a game of Watch Your Back! between two Player classes."""
    print("Simulating game #{}...".format(game_count))

    # load command-line options
    # options = _Options()

    # initialise the game and players
    game = _Game()
    white = _Player(whiteWrapper.make_player("white"), TIME_LIMIT_DEFAULT, SPACE_LIMIT_DEFAULT)
    black = _Player(blackWrapper.make_player("black"), TIME_LIMIT_DEFAULT, SPACE_LIMIT_DEFAULT)
    # now, play the game!
    player, opponent = white, black  # white has first move

    while game.playing():
        turns = game.turns

        if (turns > 200):
            game.winner = "draw"
            break

        try:
            action = player.action(turns)
        except _ResourceLimitException as e:
            # looks like one of the players exceeded their resource limits
            # during calculation of 'action'---that's the end of this game, then
            print(f"resource limit exceeded during action():", e)
            return

        try:
            game.update(action)
        except _InvalidActionException as e:
            # if one of the players makes an invalid action,
            # print the error message
            print(f"invalid action ({game.loser}):", e)
            break

        try:
            opponent.update(action)
        except _ResourceLimitException as e:
            # looks like one of the players exceeded their resource limits
            # during calculation of 'update'
            print(f"resource limit exceeded during update():", e)
            return

        # other player's turn!
        player, opponent = opponent, player

    print("Game #{} ({} vs {}) finished. Winner: {}".format(game_count, whiteWrapper.id, blackWrapper.id, game.winner))
    print(game)
    if (i % 2 == 0):
        return (whiteWrapper.id, blackWrapper.id, i, game.winner, game_count)  # ("W", "B", or "draw")
    else:
        return (blackWrapper.id, whiteWrapper.id, i, game.winner, game_count)

def round_even(x):
    init_result: int = int(x)
    if (init_result % 2 == 0):
        return max(init_result, 2) # In case x was e.g. 0.9 and rounded down to 0.
    else:
        return init_result + 1

# --------------------------------------------------------------------------- #

# OPTIONS

# default values (to use if flag is not provided)
DELAY_DEFAULT = 0
SPACE_LIMIT_DEFAULT = 0
TIME_LIMIT_DEFAULT  = 0

# missing values (to use if flag is provided, but with no value)
DELAY_NOVALUE = 1.0 # seconds
SPACE_LIMIT_NOVALUE = 100.0 # MB (each)
TIME_LIMIT_NOVALUE  = 120.0 # seconds (each)


class _Options:
    """
    Parse and contain command-line arguments.
    
    --- help message: ---
    usage: referee.py [-h] [-d [DELAY]] [-s [SPACE_LIMIT]] [-t [TIME_LIMIT]]
                      white_module black_module

    Plays a game of Watch Your Back! between two Player classes

    positional arguments:
      white_module          full name of module containing White Player class
      black_module          full name of module containing Black Player class

    optional arguments:
      -h, --help            show this help message and exit
      -d [DELAY], --delay [DELAY]
                            how long (float, seconds) to wait between turns
      -s [SPACE_LIMIT], --space_limit [SPACE_LIMIT]
                            limit on memory space (float, MB) for each player
      -t [TIME_LIMIT], --time_limit [TIME_LIMIT]
                            limit on CPU time (float, seconds) for each player
    ---------------------
    """
    def __init__(self):
        parser = argparse.ArgumentParser(
                description="Plays a game of Watch Your Back! between two "
                    "Player classes")
        parser.add_argument('white_module',
                help="full name of module containing White Player class")
        parser.add_argument('black_module',
                help="full name of module containing Black Player class")
        parser.add_argument('-d', '--delay',
                type=float, default=DELAY_DEFAULT, nargs="?",
                help="how long (float, seconds) to wait between turns")
        parser.add_argument('-s', '--space_limit',
                type=float, default=SPACE_LIMIT_DEFAULT, nargs="?",
                help="limit on memory space (float, MB) for each player")
        parser.add_argument('-t', '--time_limit',
                type=float, default=TIME_LIMIT_DEFAULT,  nargs="?",
                help="limit on CPU time (float, seconds) for each player")

        args = parser.parse_args()

        self.white_player = _load_player(args.white_module)
        self.black_player = _load_player(args.black_module)
        self.delay = _novalue_check(args.delay, DELAY_NOVALUE)
        self.space = _novalue_check(args.space_limit, SPACE_LIMIT_NOVALUE)
        self.time  = _novalue_check(args.time_limit, TIME_LIMIT_NOVALUE)

# HELPER FUNCTIONS

def _novalue_check(value, default):
    """
    Check if a value has been provided (is not None)
    Return that value if so, or default if not
    """
    return value if value is not None else default

def _load_player(modulename, package='.'):
    """
    Load a Player class given the name of a module.
    
    :param modulename: where to look for the Player class (name of a module)
    :param package: where to look for the module (relative package)
    :return: the Player class (a class object)
    """
    module = importlib.import_module(modulename, package=package)
    player_class = module.Player
    return player_class

# --------------------------------------------------------------------------- #

# PLAYER WRAPPER CLASS

class _Player:
    """
    Wrapper for a Player class to simplify initialization and resource limiting
    """
    def __init__(self, player, time_limit, space_limit):
        self.timer = _CountdownTimer(time_limit)
        self.space_limit = space_limit

        gc.collect() # off the clock
        with self.timer:
            self.player = player
        _space_check(self.space_limit)

    def update(self, move):
        gc.collect()
        with self.timer:
            self.player.update(move)
        _space_check(self.space_limit)

    def action(self, turns):
        gc.collect()
        with self.timer:
            action = self.player.action(turns)
        _space_check(self.space_limit)
        return action

# HELPER CLASSES AND FUNCTIONS

class _ResourceLimitException(Exception):
    """For when a player or both players exceed specified space / time limits"""

# MEMORY MANAGEMENT

def _get_space_usage():
    """
    Find the current and peak Virtual Memory usage of the current process, in MB
    """
    # on linux, we can find the memory usage of our program we are looking for 
    # inside /proc/self/status (specifically, fields VmSize and VmPeak)
    with open("/proc/self/status") as proc_status:
        for line in proc_status:
            if 'VmSize:' in line:
                curr_mem_usage = int(line.split()[1]) / 1024 # kB -> MB
            elif 'VmPeak:' in line:
                peak_mem_usage = int(line.split()[1]) / 1024 # kB -> MB
    return curr_mem_usage, peak_mem_usage

# by default, the python interpreter uses a significant amount of space
# measure this first to later subtract from all measurements
try:
    _DEFAULT_MEM_USAGE, _ = _get_space_usage()
except:
    #print("note: unable to measure memory usage on this platform (try dimefox)")
    pass

def _space_check(limit):
    """
    Check up on the current and peak space usage of the process, printing
    stats and ensuring that peak usage is not exceeding limits
    """
    try:
        curr_mem_usage, peak_mem_usage = _get_space_usage()
    except:
        #print("unable to measure memory usage on this platform")
        return
    
    # adjust measurements to reflect usage of players and referee, not
    # the Python interpreter itself
    curr_mem_usage -= _DEFAULT_MEM_USAGE
    peak_mem_usage -= _DEFAULT_MEM_USAGE

    print(f"space: {curr_mem_usage:.3f}MB (current usage) "
        + f"{peak_mem_usage:.3f}MB (max usage) (both players)")
    
    # if we are limited, let's hope we are not out of space!
    # double the limit because space usage is shared
    if limit and peak_mem_usage > 2 * limit:
        raise _ResourceLimitException("Players exceeded shared space limit")

# TIME MANAGEMENT

class _CountdownTimer:
    """
    Reusable context manager for timing specific sections of code

    * measures CPU time, not wall-clock time
    * if limit is not 0, throws an exception upon exiting the context after the 
      allocated time has passed
    """
    def __init__(self, limit):
        """
        Create a new countdown timer with time limit `limit`, in seconds
        (0 for unlimited time)
        """
        self.limit = limit
        self.clock = 0

    def __enter__(self):
        # start timing
        self.start = time.process_time()
        return self # unused

    def __exit__(self, exc_type, exc_val, exc_tb):
        # accumulate elapsed time since __enter__
        elapsed = time.process_time() - self.start
        self.clock += elapsed
        #print(f"time: {elapsed:.3f}s (this turn), {self.clock:.3f}s (total)")

        # if we are limited, let's hope we aren't out of time!
        if self.limit and self.clock > self.limit:
            raise _ResourceLimitException("Player exceeded available time")


# --------------------------------------------------------------------------- #

# REFEREE'S INTERNAL GAME STATE REPRESENTATION

#                        NOT INTENDED FOR STUDENT USE
# 
# This part of the referee is designed to store the state of a game for the
# purpose of validating actions and providing helpful error messages for when
# players suggest invalid actions. It is not intended to be used by Players.
# You should design and use your own representation of the game and board
# state, optimised with your specific usage in mind: deciding which action to
# to choose each turn.

class _InvalidActionException(Exception):
    """For when an action breaks the rules of the game"""

class _Game:
    """Represent the state of a game of Watch Your Back!"""
    def __init__(self):
        """
        Initializes the representation of the game.

        This 'state' includes the current configuration of the board and 
        information pertaining to the game's progression between phases
        """
        # board configuration (initially empty)
        self.board = [['-' for _ in range(8)] for _ in range(8)]
        for square in [(0, 0), (7, 0), (7, 7), (0, 7)]:
            x, y = square
            self.board[y][x] = 'X'
        self.n_shrinks = 0

        # tracking progress through game phases
        self.turns  = 0
        self.phase  = 'placing'
        self.pieces = {'W': 0, 'B': 0}
        self.winner = None
        self.loser  = None

    _DISPLAY = {'B': '@', 'W': 'O', 'X': 'X', '-': '-', ' ': ' '}
    def __str__(self):
        """String representation of the current game state."""
        displayboard = [[_Game._DISPLAY[p] for p in row] for row in self.board]
        board = '\n'.join(' '.join(row) for row in displayboard)
        if self.playing():
            progress = f'{self.turns} turns into the {self.phase} phase'
        else:
            progress = 'game over!'
        return f'{board}\n{progress}'

    def playing(self):
        """:return: True iff the game is still in progress"""
        return self.phase == 'placing' or self.phase == 'moving'

    def update(self, action):
        """
        Validate an action and update the current state accordingly.

        :raises _InvalidActionException: for any action that is not legal
        according to the rules of the game
        """
        # update the board
        if self.phase == 'placing':
            self._place(action)
        elif self.phase == 'moving':
            if action is None:
                self._forfeit()
            else:
                self._move(action)

        # progress the game
        self.turns += 1
        if self.phase == 'placing':
            if self.turns == 24:
                # time to enter the moving phase!
                self.phase = 'moving'
                self.turns = 0
        if self.phase == 'moving':
            self._check_win()
            if self.phase != 'completed' and self.turns in [128, 192]:
                self._shrink_board()
                self._check_win()

    def _place(self, place):
        """
        Validate a 'place' action and update board configuration accordingly.
        
        :param place: (x, y) tuple representing the square on which to place
        the piece
        """
        # unpack and validate piece representation
        try:
            x, y = place
            assert(isinstance(x, int) and isinstance(y, int))
        except:
            self._invalidate(f"invalid place action representation: {place!r}")

        # validate place itself
        piece = self._piece()

        if not self._within_board(x, y):
            self._invalidate(f"player's place contained invalid coordinates: "
                f"{place}")
        if piece == 'W' and y > 5 or piece == 'B' and y < 2:
            self._invalidate(f"player tried to place outside their starting "
                f"zone: {place}")
        if not self.board[y][x] == '-':
            self._invalidate(f"player tried to place on an occupied square or "
                f"corner: {place}")

        # if that was all okay... we can carry out the place action!
        self.board[y][x] = piece
        self.pieces[piece] += 1
        self._eliminate_about((x, y))


    def _move(self, move):

        """
        Validate a move a -> b and update the board configuration accordingly.

        :param move: nested tuple ((xa, ya), (xb, yb)) representing move
        (xa, ya) -> (xb, yb)
        """
        # unpack and validate move representation
        try:
            (xa, ya), (xb, yb) = a, b = move
            assert(all(isinstance(coordinate, int) for coordinate in a+b))
        except:
            self._invalidate(f"invalid move action representation: {move!r}")
        
        # validate move itself
        piece = self._piece()
        if not (self._within_board(xa, ya) and self._within_board(xb, yb)):
            self._invalidate(f"player's move contained invalid coordinates: "
                f"({a}) -> ({b})")
        if self.board[ya][xa] != piece:
            self._invalidate(f"player tried to move from a square it doesn't "
                f"have a piece on: ({a}) -> ({b})")
        if self.board[yb][xb] != '-':
            self._invalidate(f"player tried to move to an occupied square or "
                f"corner: ({a}) -> ({b})")
        if not (self._is_jump(move) or self._is_move(move)):
            self._invalidate(f"player tried to move to a non-reachable square "
                "(a square that is neither adjacent nor opposite an adjacent "
                f"occupied square): ({a}) -> ({b})")

        # if that was all okay... we can carry out the move!
        self.board[yb][xb] = piece
        self.board[ya][xa] = '-'
        self._eliminate_about(b)

    def _forfeit(self):
        """
        Validate a 'forfeit' (no move) action, which must not be taken unless
        the player has no legal moves available.
        """
        piece = self._piece()
        message = f'player tried to forfeit a move, but had available moves'

        # check for any possible moves for any of the player's pieces
        for xa, ya in self._squares_with_piece(piece):
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                # is the adjacent square unoccupied?
                xb, yb = xa + dx, ya + dy
                if self._within_board(xb, yb) and self.board[yb][xb] == '-':
                    self._invalidate(message)
                # if not, how about the opposite square?
                xb, yb = xb + dx, yb + dy
                if self._within_board(xb, yb) and self.board[yb][xb] == '-':
                    self._invalidate(message)

        # if that was all okay... there are no available moves and so the
        # forfeit was legal! no action required.

    def _squares_with_piece(self, piece):
        """
        Generate coordinates of squares currently containing a piece

        :param piece: string representation of the piece type to check for
        """
        for x in range(8):
            for y in range(8):
                if self.board[y][x] == piece:
                    yield (x, y)

    def _piece(self):
        """:return: the piece of the player with the current turn"""
        return 'W' if self.turns % 2 == 0  else 'B'

    def _other(self):
        """:return: the piece of the other player (not the current turn)"""
        return 'W' if self._piece() == 'B' else 'B'

    def _within_board(self, x, y):
        """
        Check if a given pair of coordinates is 'on the board'.

        :param x: column value
        :param y: row value
        :return: True iff the coordinate is on the board
        """
        for coord in [y, x]:
            if coord < 0 or coord > 7:
                return False
        if self.board[y][x] == ' ':
            return False
        return True

    def _check_win(self):
        """
        Check the board to see if the game has concluded.

        Count the number of pieces remaining for each player: if either player
        has run out of pieces, decide the winner and transition to the 
        'completed' state
        """
        # print(self)

        n_whites = self.pieces['W']
        n_blacks = self.pieces['B']
        if n_whites >= 2 and n_blacks >= 2:
            pass # game continues...
        elif n_whites < 2 and n_blacks >= 2:
            self.winner = 'B'
            self.phase = 'completed'
        elif n_blacks < 2 and n_whites >= 2:
            self.winner = 'W'
            self.phase = 'completed'
        elif n_whites < 2 and n_blacks < 2:
            self.winner = 'draw'
            self.phase = 'completed'

    def _invalidate(self, reason):
        """
        In response to an error, invalidate the game state.
        
        Transition to the 'invalid' state, declare the non-current player
        the winner (the current player has played an invalid action), and 
        raise an exception describing the problem
        
        :param reason: message describing what went wrong (to be included in
        the exception).
        :raises _InvalidActionException: (every time)
        """
        self.phase = 'invalid'
        self.loser  = self._piece()
        self.winner = self._other()
        raise _InvalidActionException(reason)

    def _shrink_board(self):
        """
        Shrink the board, eliminating all pieces along the outermost layer,
        and replacing the corners.

        This method can be called up to two times only.
        """
        s = self.n_shrinks # number of shrinks so far, or 's' for short
        # Remove edges
        for i in range(s, 8 - s):
            for square in [(i, s), (s, i), (i, 7-s), (7-s, i)]:
                x, y = square
                piece = self.board[y][x]
                if piece in self.pieces:
                    self.pieces[piece] -= 1
                self.board[y][x] = ' '
        
        # we have now shrunk the board once more!
        self.n_shrinks = s = s + 1

        # replace the corners (and perform corner elimination)
        for corner in [(s, s), (s, 7-s), (7-s, 7-s), (7-s, s)]:
            x, y = corner
            piece = self.board[y][x]
            if piece in self.pieces:
                self.pieces[piece] -= 1
            self.board[y][x] = 'X'
            self._eliminate_about(corner)

    def _eliminate_about(self, square):
        """
        A piece has entered this square: look around to eliminate adjacent
        (surrounded) enemy pieces, then possibly eliminate this piece too.
        
        :param square: the square to look around
        """
        x, y = square
        piece = self.board[y][x]
        targets = self._targets(piece)
        
        # Check if piece in square eliminates other pieces
        for dx, dy in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            target_x, target_y = x + dx, y + dy
            targetval = None
            if self._within_board(target_x, target_y):
                targetval = self.board[target_y][target_x]
            if targetval in targets:
                if self._surrounded(target_x, target_y, -dx, -dy):
                    self.board[target_y][target_x] = '-'
                    self.pieces[targetval] -= 1

        # Check if the current piece is surrounded and should be eliminated
        if piece in self.pieces:
            if self._surrounded(x, y, 1, 0) or self._surrounded(x, y, 0, 1):
                self.board[y][x] = '-'
                self.pieces[piece] -= 1

    def _surrounded(self, x, y, dx, dy):
        """
        Check if piece on (x, y) is surrounded on (x + dx, y + dy) and
        (x - dx, y - dy).
        
        :param x: column of the square to be checked
        :param y: row of the square to be checked
        :param dx: 1 if adjacent cols are to be checked (dy should be 0)
        :param dy: 1 if adjacent rows are to be checked (dx should be 0)
        :return: True iff the square is surrounded
        """
        xa, ya = x + dx, y + dy
        firstval = None
        if self._within_board(xa, ya):
            firstval = self.board[ya][xa]

        xb, yb = x - dx, y - dy
        secondval = None
        if self._within_board(xb, yb):
            secondval = self.board[yb][xb]

        # If both adjacent squares have enemies then this piece is surrounded!
        piece = self.board[y][x]
        enemies = self._enemies(piece)
        return (firstval in enemies and secondval in enemies)

    def _enemies(self, piece):
        """
        Which pieces can eliminate a piece of this type?

        :param piece: the type of piece ('B', 'W', or 'X')
        :return: set of piece types that can eliminate a piece of this type
        """
        if piece == 'B':
            return {'W', 'X'}
        elif piece == 'W':
            return {'B', 'X'}
        return set()

    def _targets(self, piece):
        """
        Which pieces can a piece of this type eliminate?
        
        :param piece: the type of piece ('B', 'W', or 'X')
        :return: the set of piece types that a piece of this type can eliminate
        """
        if piece == 'B':
            return {'W'}
        elif piece == 'W':
            return {'B'}
        elif piece == 'X':
            return {'B', 'W'}
        return set()

    def _is_move(self, move):
        """
        Check if a move is a 'simple' move in terms of distance.
        
        :return: True is the move is a correct 'simple' move
        """
        (xa, ya), (xb, yb) = move
        if xa == xb and abs(ya - yb) == 1:
            return True
        if ya == yb and abs(xa - xb) == 1:
            return True
        return False

    def _is_jump(self, move):
        """
        Check if a move is a 'jump' move in terms of distance.
        
        :return: True iff the move is a correct 'jump' move
        """
        (xa, ya), (xb, yb) = move
        if xa == xb and abs(ya - yb) == 2:
            if self.board[min(ya, yb) + 1][xa] in self.pieces:
                return True
        elif ya == yb and abs(xa - xb) == 2:
            if self.board[ya][min(xa, xb) + 1] in self.pieces:
                return True
        return False

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()
