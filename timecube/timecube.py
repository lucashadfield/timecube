import uasyncio as asyncio
import utime
from math import ceil, floor

from state import State, Interval, Pause, Summary
from screen import Screen


class TimeCube:
    def __init__(self, screen: Screen, interval_cycle: list, pause: Pause, summary: Summary):
        self.screen = screen
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
        screen: Screen,
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

        return cls(screen, interval_cycle, pause, summary)

    def __call__(self):
        self.state_start = utime.ticks_ms()
        self.state = self._current_interval
        self._start_screen()
        self.interval_task = asyncio.create_task(self._start_interval_task())

    @property
    def _next_interval(self) -> Interval:
        return self.interval_cycle[(self.interval_id + 1) % len(self.interval_cycle)]

    @property
    def _current_interval(self) -> Interval:
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
            print('starting {} for {} seconds'.format(self._current_interval.kind, duration))

            n_steps = ceil(duration / self.state.update_interval)
            first_step = duration - (n_steps - 1) * self.state.update_interval
            update_delay_total = 0

            # todo: work out what the base rate should be, should have an average partial refresh too
            update_delay_average = 1.7
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

                screen_time_remaining = max(round((duration - elapsed_time - update_delay_total) / 60), 0)
                print(f'screen_time_remaining: {duration}, {elapsed_time} - {(duration - elapsed_time - update_delay_total) / 60}')
                screen_prop_remaining = 1 - (i + 1) / n_steps

                update_start = utime.ticks_ms()
                self._update_screen(screen_time_remaining, screen_prop_remaining)
                update_delay_total += utime.ticks_diff(utime.ticks_ms(), update_start) / 1000
                print('update_delay_total', update_delay_total)

                if i < n_steps - 1:
                    print('{:.0%}'.format((floor(offset) + (i + 1)) / n_steps))
                    update_delay_average = update_delay_total / (i + 1)
                    time_left = duration - utime.ticks_diff(utime.ticks_ms(), self.state_start) / 1000

                # print(update_delay_total, update_delay_average, time_left)

            print('finished {}'.format(self._current_interval.kind))
            # print('Before end callback:', utime.ticks_diff(utime.ticks_ms(), self.state_start) / 1000)
            # if self.state.end_callback is not None:
            #     self.state.end_callback()
            # print('After end callback:', utime.ticks_diff(utime.ticks_ms(), self.state_start) / 1000)

    def _start_screen(self):
        next_interval = self._next_interval.kind

        self.screen.start_interval(
            is_fill_black=True if self._current_interval.kind == 'work' else False,
            remaining_time=self._current_interval.duration // 60,
            remaining_prop=1,
            next_interval=next_interval if next_interval == 'longbreak' else None,
        )

    def _update_screen(self, remaining_time: int, remaining_prop: float):
        next_interval = self._next_interval.kind

        self.screen.update_interval(
            remaining_time=remaining_time,
            remaining_prop=remaining_prop,
            next_interval=next_interval if next_interval == 'longbreak' else None,
        )

    def next(self):
        '''Start a new next interval'''
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            self.interval_id += 1
            self._transition_state(self._current_interval)
            self.screen.rotate_left()  # screen rotates opposite direction
            self._start_screen()
            self.interval_task = asyncio.create_task(self._start_interval_task())
            self.last_action = 'next'

    def prev(self):
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            time_since_start = utime.ticks_diff(utime.ticks_ms(), self.state_start) / 1000
            if time_since_start < 5 and self.interval_id and self.last_action == 'prev':
                # if you double back, go back to previous interval
                self.summary_stats[f'{self._current_interval.kind}_restarts'] -= 1
                self.interval_id -= 1
            else:
                # else go back to start of current one
                self.summary_stats[f'{self._current_interval.kind}_restarts'] += 1
            self._transition_state(self._current_interval)
            self.screen.rotate_right()  # screen rotates opposite direction
            self._start_screen()
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
