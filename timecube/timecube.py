import uasyncio as asyncio
import sys
import utime
from math import ceil, floor

from machine import Pin

from accelerometer import Accelerometer
from button import Button
from state import State, Interval, Pause, Summary


class TimeCube:
    def __init__(self, interval_cycle: list, pause: Pause, summary: Summary):
        self.interval_cycle = interval_cycle
        self.pause_state = pause
        self.summary_state = summary

        self.interval_id = 0  # id num of which interval we're on
        self.interval_task = None  # the asyncio task object for the current task
        self.saved_interval_duration = 0  # elapsed time on current task needed for pause/resume

        self.state_start = None  # when the task started
        self.state = None  # current state
        self.last_action = None

        self.summary_stats = {
            'work': 0,
            'break': 0,
            'longbreak': 0,
            'pause': 0,
            'summary': 0,
            'config': 0,
            'work_restarts': 0,
            'break_restarts': 0,
            'longbreak_restarts': 0,
        }

    @classmethod
    def from_config(
        cls,
        n_work_loops: int,
        work_interval: Interval,
        break_interval: Interval,
        longbreak_interval: Interval,
        pause: Pause,
        summary: Summary,
    ):
        interval_cycle = []
        for n in range(n_work_loops - 1):
            interval_cycle.append(work_interval)
            interval_cycle.append(break_interval)
        interval_cycle.append(work_interval)
        interval_cycle.append(longbreak_interval)

        return cls(interval_cycle, pause, summary)

    def __call__(self):
        self.state_start = utime.ticks_ms()
        self.state = self._current_interval
        self.interval_task = asyncio.create_task(self._start_interval_task())

    @property
    def _current_interval(self):
        return self.interval_cycle[self.interval_id % len(self.interval_cycle)]

    def _transition_state(self, new_state: State):
        now = utime.ticks_ms()
        duration = utime.ticks_diff(now, self.state_start) / 1000
        self.summary_stats[self.state.kind] += duration
        if isinstance(self.state, Interval):
            self.saved_interval_duration = 0
        self.state_start = now
        self.state = new_state
        self.print_summary_stats()

        return duration

    async def _start_interval_task(self, offset: float = 0):
        duration = self._current_interval.duration - offset
        if duration > 0:
            print(f'starting {self._current_interval.kind} for {duration} seconds')

            n_steps = ceil(duration / self.state.update_interval)
            first_step = duration - (n_steps - 1) * self.state.update_interval

            elapsed_time = 0
            for i in range(
                n_steps
            ):  # todo: dynamically update based on actual elapsed time (accounts for screen update delay)
                sleep_duration = self.state.update_interval if i else first_step
                await asyncio.sleep(sleep_duration)
                elapsed_time += sleep_duration
                if self.state.update_callback is not None:
                    self.state.update_callback(elapsed_time, duration)
                print(f'{(floor(offset) + (i + 1)) / self._current_interval.duration:.0%}')

            print(f'finished {self._current_interval.kind}')
            if self.state.end_callback is not None:
                self.state.end_callback()

    def next(self):
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            self.interval_id += 1
            self._transition_state(self._current_interval)
            self.interval_task = asyncio.create_task(self._start_interval_task())
            self.last_action = 'next'

    def prev(self):
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            time_since_start = utime.ticks_diff(utime.ticks_ms(), self.state_start) / 1000
            if time_since_start < 1 and self.interval_id and self.last_action == 'prev':
                self.summary_stats[f'{self._current_interval.kind}_restarts'] -= 1
                self.interval_id -= 1
            else:
                self.summary_stats['{self._current_interval.kind}_restarts'] += 1
            self._transition_state(self._current_interval)
            self.interval_task = asyncio.create_task(self._start_interval_task())
            self.last_action = 'prev'

    def pause(self):
        if isinstance(self.state, Interval):
            # if in interval -> pause
            self.interval_task.cancel()
            self.saved_interval_duration += self._transition_state(self.pause_state)
        elif isinstance(self.state, Summary):
            # if in summary -> pause
            pass  # todo: do something here?
        elif isinstance(self.state, Pause):
            # if in pause -> resume
            self._transition_state(self._current_interval)
            self.interval_task = asyncio.create_task(self._start_interval_task(self.saved_interval_duration))
        self.last_action = 'pause'

    def summary(self):
        if isinstance(self.state, Interval) or self.state == 'pause':
            self.interval_task.cancel()
            if isinstance(self.state, Interval):
                self.saved_interval_duration += self._transition_state(self.summary_state)
            else:
                self._transition_state(self.summary_state)
        self.last_action = 'summary'

        # do summary things

    # debug methods
    def print_summary_stats(self):
        print({k: round(v, 2) for k, v in self.summary_stats.items()})


async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader


async def main():
    config = {'n_work_loops': 3, 'work_duration_s': 5, 'break_duration_s': 1, 'longbreak_duration_s': 2}
    work_interval = Interval('work', 5, None, None, None)
    break_interval = Interval('break', 1, None, None, None)
    longbreak_interval = Interval('longbreak', 2, None, None, None)
    pause = Pause('pause', None)
    summary = Summary('summary', None)

    timecube = TimeCube.from_config(3, work_interval, break_interval, longbreak_interval, pause, summary)
    timecube()

    # buttons
    restart_pin = Pin(14, Pin.IN, Pin.PULL_DOWN)
    restart = Button(restart_pin, timecube.prev)

    next_pin = Pin(10, Pin.IN, Pin.PULL_DOWN)
    next = Button(next_pin, timecube.next)

    pause_pin = Pin(7, Pin.IN, Pin.PULL_DOWN)
    pause = Button(pause_pin, timecube.pause)

    sensor = Accelerometer(28, 27, 26, timecube.next, timecube.prev, timecube.pause, timecube.pause)

    while True:
        await asyncio.sleep(0)


asyncio.run(main())
