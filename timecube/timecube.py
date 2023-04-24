from math import ceil

import uasyncio as asyncio
import utime

from screen import Screen
from state import State, Interval, Pause, Summary

# number of observations: precomputed denominator for gradient calculation
REGRESSION_PRECOMPUTED = {2: 1, 3: 6, 4: 20}


class TimeCube:
    def __init__(
        self,
        screen: Screen,
        interval_cycle: list,
        pause: Pause,
        summary: Summary,
        diagnostics_callback,
        delay_recency_weight,
        goto_prev_timeout_s,
    ):
        self.screen = screen
        self.interval_cycle = interval_cycle
        self.pause_state = pause
        self.summary_state = summary
        self.diagnostics_callback = diagnostics_callback
        self.delay_recency_weight = delay_recency_weight
        self.goto_prev_timeout_s = goto_prev_timeout_s

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
        diagnostics_callback,
        delay_recency_weight,
        goto_prev_timeout_s,
    ):
        interval_cycle = []
        for n in range(n_work_loops - 1):
            interval_cycle.append(work_interval)
            interval_cycle.append(break_interval)
        interval_cycle.append(work_interval)
        interval_cycle.append(longbreak_interval)

        return cls(
            screen, interval_cycle, pause, summary, diagnostics_callback, delay_recency_weight, goto_prev_timeout_s
        )

    def run(self, starting_accelerometer_state):
        self.state_start = utime.ticks_ms()
        print('self.state_start set now')
        self.state = self._current_interval
        self.interval_task = asyncio.create_task(self._start_interval_task())
        self.screen.update_screen_rotation(starting_accelerometer_state)
        self._start_screen()

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
        update_start = utime.ticks_ms()

        if duration > 0:
            print(f'timecube: starting {self._current_interval.kind} interval for {duration} seconds')

            n_steps = ceil(duration / self.state.update_interval)
            first_step = duration - (n_steps - 1) * self.state.update_interval
            update_delay_total = 0

            time_left = duration - self.start_delay

            update_times = []
            error = 0
            for i in range(n_steps):
                if i:
                    sleep_duration = self.state.update_interval - predicted_next_update_time - error
                    self.diagnostics_callback('delay', f'{predicted_next_update_time:.2f}')
                else:
                    sleep_duration = first_step - self.start_delay

                print(f'timecube: sleeping for {sleep_duration} seconds')
                await asyncio.sleep(sleep_duration)

                # update screen value and annulus
                remaining_time = n_steps - i - 1
                self._update_screen(remaining_time, remaining_time / n_steps)

                update_end = utime.ticks_ms()
                update_time = (utime.ticks_diff(update_end, update_start) / 1000) - sleep_duration
                update_start = utime.ticks_ms()

                update_times.append(update_time)
                update_delay_total += update_time

                predicted_next_update_time = self._predict_update_time(update_times)

                # accumulate errors
                time_left_new = duration - utime.ticks_diff(utime.ticks_ms(), self.state_start) / 1000
                error += time_left - time_left_new - self.state.update_interval
                if i == 0:
                    error += self.start_delay - update_time
                time_left = time_left_new

                print(f'timecube: i={i}, update_time={update_time}, update_delay_total={update_delay_total}, predicted_next_update_time={predicted_next_update_time}, time_left={time_left}')

            print(f'timecube: finished {self._current_interval.kind} interval')

    def _predict_update_time(self, prev):
        '''
        Predict the next delay based on linear regression of the last (up to) 4 measured times.
        Update times are dependent on how much is being drawn on screen so go up/down linearly.
        4 points is enough for a decent estimate.

        Args:
            prev (List[float]): list of up to last 4 measured `update_time`s

        Returns (float): prediction for next `update_time`
        '''
        prev = prev[-4:]
        n = len(prev)
        if n == 1:
            return prev[0]
        else:
            x = [0, 1, 2, 3][:n]
            sum_xy = sum([x * y for x, y in zip(x, prev)])
            m = (n * sum_xy - sum(x) * sum(prev)) / REGRESSION_PRECOMPUTED[n]
            # y = mx + b
            return n * m + prev[0]

    def _start_screen(self):
        next_interval = self._next_interval.kind

        # update diagnostics
        self.diagnostics_callback(['interval', 'interval_id'], [self._current_interval.kind, self.interval_id])

        screen_start_time = utime.ticks_ms()
        self.screen.display_new_interval(
            is_fill_black=True if self._current_interval.kind == 'work' else False,
            starting_time=self._current_interval.duration // 60,
            starting_prop=1.0,
            draw_longbreak_icon=next_interval == 'longbreak',
        )
        self.start_delay = utime.ticks_diff(utime.ticks_ms(), screen_start_time) / 1000
        print(f'timecube: start screen delay={self.start_delay:.3f} seconds')

    def _update_screen(self, remaining_time: int, remaining_prop: float):
        self.screen.update_interval_display(
            remaining_time=remaining_time,
            remaining_prop=remaining_prop,
            draw_longbreak_icon=self._next_interval.kind == 'longbreak',
        )

    def next(self, accelerometer_state):
        '''Start a new next interval'''
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            self.interval_id += 1
            self._transition_state(self._current_interval)
            self.screen.update_screen_rotation(accelerometer_state)
            self._start_screen()
            self.interval_task = asyncio.create_task(self._start_interval_task())
            self.last_action = 'next'

    def prev(self, accelerometer_state):
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            time_since_start = utime.ticks_diff(utime.ticks_ms(), self.state_start) / 1000
            if time_since_start < self.goto_prev_timeout_s and self.interval_id and self.last_action == 'prev':
                # if you double back, go back to previous interval
                self.summary_stats[f'{self._current_interval.kind}_restarts'] -= 1
                self.interval_id -= 1
            else:
                # else go back to start of current one
                self.summary_stats[f'{self._current_interval.kind}_restarts'] += 1
            self._transition_state(self._current_interval)
            self.screen.update_screen_rotation(accelerometer_state)
            self._start_screen()
            self.interval_task = asyncio.create_task(self._start_interval_task())
            self.last_action = 'prev'

    def pause(self):
        if isinstance(self.state, Interval):
            # if in interval -> pause
            self.interval_task.cancel()
            self.saved_interval_duration += self._transition_state(self.pause_state)
            self.screen.pause()
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
        stats = {k: round(v, 2) for k, v in self.summary_stats.items()}
        print(f'timecube: summary_stats={stats}')
