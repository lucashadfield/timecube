class State:
    update_interval = 1

    def __init__(
        self,
        kind: str,
        duration,
        start_callback,
        update_callback,
        end_callback,
    ):
        self.kind = kind
        self.duration = duration
        self.start_callback = start_callback
        self.update_callback = update_callback
        self.end_callback = end_callback


class Interval(State):
    def __init__(
        self,
        kind: str,
        duration: int,
        start_callback,
        update_callback,
        end_callback,
    ):
        super().__init__(kind, duration, start_callback, update_callback, end_callback)


class Pause(State):
    def __init__(self, kind: str, start_callback):
        super().__init__(kind, None, start_callback, None, None)


class Summary(State):
    def __init__(self, kind: str, start_callback):
        super().__init__(kind, None, start_callback, None, None)
