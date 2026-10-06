from time import monotonic

class Timer:
    def __init__(self, time : int):
        Deadline : float = monotonic() + time
        Interval : int = 0
        Callback = None
        Cancelled = False

