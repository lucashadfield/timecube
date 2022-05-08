class State:
    update_interval = 60

    def __init__(self, kind: str, duration):
        self.kind = kind
        self.duration = duration


class Interval(State):
    def __init__(self, kind: str, duration: int):
        super().__init__(kind, duration)


class Pause(State):
    def __init__(self, kind: str):
        super().__init__(kind, None)


class Summary(State):
    def __init__(self, kind: str):
        super().__init__(kind, None)


#
