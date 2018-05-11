import time


class Timer:
    """
    ---------------------------------------------------------------------------
    Taken from _CountdownTimer written by Matt Farrugia and Shreyash Patodia.
    Utilized the given timer from referee.py in order to keep the timing of our
    own AI as close to the one used by the referee.
    ---------------------------------------------------------------------------
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
        print(f"time: {elapsed:.3f}s (this turn), {self.clock:.3f}s (total)")

        # if we are limited, let's hope we aren't out of time!
        if self.limit and self.clock > self.limit:
            # Slightly modified.
            raise RuntimeError("Player exceeded available time")