import asyncio as asyncio
import sys
import time
from math import ceil, floor

# from machine import Pin
#
# from accelerometer import Accelerometer
# from button import Button
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
        self.last_action = None  # to work out whether or not to actually go back if there are two backs

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
        self.state_start = time.time()
        self.state = self._current_interval
        self.interval_task = asyncio.create_task(self._start_interval_task())

    @property
    def _current_interval(self):
        return self.interval_cycle[self.interval_id % len(self.interval_cycle)]

    def _transition_state(self, new_state: State):
        now = time.time()
        duration = now - self.state_start
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
            print('starting {} for {} seconds'.format(self._current_interval.kind, duration))

            n_steps = ceil(duration / self.state.update_interval)
            first_step = duration - (n_steps - 1) * self.state.update_interval
            update_delay_total = 0
            update_delay_average = 0.1  # todo: work out what the base rate should be
            time_left = duration

            elapsed_time = 0
            for i in range(n_steps):
                sleep_duration = (
                    (time_left - update_delay_average * (n_steps - i)) / (n_steps - i)
                    if i
                    else first_step - update_delay_average
                )
                print(f'sleeping for {sleep_duration}, average delay: {update_delay_average}')
                await asyncio.sleep(sleep_duration)
                elapsed_time += sleep_duration
                if self.state.update_callback is not None:
                    update_start = time.time()
                    self.state.update_callback(
                        elapsed_time, duration
                    )  # todo: how should elapsed time be worked out?
                    update_delay_total += time.time() - update_start

                if i < n_steps - 1:
                    print('{:.0%}'.format((floor(offset) + (i + 1)) / self._current_interval.duration))
                    update_delay_average = update_delay_total / (i + 1)
                    time_left = duration - (time.time() - self.state_start)
                # print(update_delay_total, update_delay_average, time_left)

            print('finished {}'.format(self._current_interval.kind))
            print('Before end callback:', time.time() - self.state_start)
            if self.state.end_callback is not None:
                self.state.end_callback()
            print('After end callback:', time.time() - self.state_start)

    def next(self):
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            self.interval_id += 1
            self._transition_state(self._current_interval)
            self.interval_task = asyncio.create_task(self._start_interval_task())
            self.last_action = 'next'
        if self.state is None:
            # start the state machine
            self()

    def prev(self):
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            time_since_start = time.time() - self.state_start
            if time_since_start < 1 and self.interval_id and self.last_action == 'prev':
                self.summary_stats['{}_restarts'.format(self._current_interval.kind)] -= 1
                self.interval_id -= 1
            else:
                self.summary_stats['{}_restarts'.format(self._current_interval.kind)] += 1
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


def tmp_update_callback(elapsed_time, duration):
    time.sleep(0.1)


def tmp_end_callback():
    time.sleep(0.2)


async def main():
    config = {'n_work_loops': 3, 'work_duration_s': 5, 'break_duration_s': 1, 'longbreak_duration_s': 2}
    work_interval = Interval('work', 5, None, tmp_update_callback, tmp_end_callback)
    break_interval = Interval('break', 1, None, None, None)
    longbreak_interval = Interval('longbreak', 2, None, None, None)
    pause = Pause('pause', None)
    summary = Summary('summary', None)

    timecube = TimeCube.from_config(3, work_interval, break_interval, longbreak_interval, pause, summary)
    # timecube()

    reader = await connect_stdin_stdout()
    while True:
        await asyncio.sleep(0)
        res = await reader.read(10)
        if res == b'l\n':  # next
            print('next')
            timecube.next()
        elif res == b'j\n':  # restart
            timecube.prev()
        elif res == b'k\n':
            timecube.pause()
        elif res == b'i\n':
            timecube.pause()


asyncio.run(main())
