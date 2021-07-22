import asyncio
import sys
import time
from dataclasses import dataclass
from math import ceil, floor


@dataclass
class Interval:
    type: str  # 'work', 'break', 'longbreak'
    duration: int
    alarm: str


class TimeCube:
    def __init__(
        self, work_duration_s, break_duration_s, longbreak_duration_s, n_work_loops
    ):  # remove defaults
        self.work_duration_s = work_duration_s
        self.break_duration_s = break_duration_s
        self.longbreak_duration_s = longbreak_duration_s
        self.n_work_loops = n_work_loops

        self.interval_id = 0
        self.interval_task = None
        self.saved_interval_duration = 0

        self.state_start = None
        self.state = None

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

        # each object is only created once - need to re-zero after they end
        work_interval = Interval('work', work_duration_s, 'knock')
        break_interval = Interval('break', break_duration_s, 'knock knock')
        longbreak_interval = Interval('longbreak', longbreak_duration_s, 'knock knock knock')

        self.cycle = []
        for n in range(n_work_loops - 1):
            self.cycle.append(work_interval)
            self.cycle.append(break_interval)
        self.cycle.append(work_interval)
        self.cycle.append(longbreak_interval)

    @property
    def current_interval(self):
        return self.cycle[self.interval_id % len(self.cycle)]

    @property
    def next_interval(self):
        return self.cycle[(self.interval_id + 1) % len(self.cycle)]

    def transition_state(self, new_state):
        now = time.time()
        duration = now - self.state_start
        if isinstance(self.state, Interval):
            self.summary_stats[self.state.type] += duration
            self.saved_interval_duration = 0
        else:
            self.summary_stats[self.state] += duration

        self.state_start = now
        self.state = new_state
        self.print_summary_stats()

        return duration

    def print_summary_stats(self):
        print({k: round(v, 1) for k, v in self.summary_stats.items()})

    async def start_interval_task(self, offset=0):
        duration = self.current_interval.duration - offset
        if duration > 0:
            print(f'starting {self.current_interval.type} for {duration} seconds')

            n_steps = ceil(duration)
            first_step = duration - (n_steps - 1)

            for i in range(n_steps):
                await asyncio.sleep(1 if i else first_step)
                print(f'{(floor(offset) + (i + 1)) / self.current_interval.duration:.0%}')

            print(f'finished {self.current_interval.type} ->  {self.next_interval.alarm}')
            # do end of task changes here + alarm

    def start(self):
        self.state_start = time.time()
        self.state = self.current_interval
        self.interval_task = asyncio.create_task(self.start_interval_task())

    def start_next_interval(self):
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            self.interval_id += 1
            self.transition_state(self.current_interval)
            self.interval_task = asyncio.create_task(self.start_interval_task())

    def restart_current_interval(self):
        if isinstance(self.state, Interval):
            self.interval_task.cancel()

            self.summary_stats[f'{self.current_interval.type}_restarts'] += 1
            self.transition_state(self.current_interval)
            self.interval_task = asyncio.create_task(self.start_interval_task())

    def pause(self):
        if self.state != 'pause':
            self.interval_task.cancel()
            if isinstance(self.state, Interval):
                self.saved_interval_duration += self.transition_state('pause')
            else:
                self.transition_state('pause')

            # do pause things

    def summary(self):
        if self.state != 'summary':
            self.interval_task.cancel()
            if isinstance(self.state, Interval):
                self.saved_interval_duration += self.transition_state('summary')
            else:
                self.transition_state('summary')

            # do summary things

    def config(self):
        if self.state != 'config':
            self.interval_task.cancel()
            if isinstance(self.state, Interval):
                self.saved_interval_duration += self.transition_state('config')
            else:
                self.transition_state('config')

            # do config things

    def resume(self):
        if self.state in ('pause', 'summary', 'config'):
            self.transition_state(self.current_interval)
            self.interval_task = asyncio.create_task(self.start_interval_task(self.saved_interval_duration))


class Config:
    pass


async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader


async def main():
    timecube = TimeCube(5, 1, 2, 3)

    timecube.start()
    print('this prints first')

    reader = await connect_stdin_stdout()
    while True:
        await asyncio.sleep(0)
        res = await reader.read(10)
        if res == b'l\n':
            timecube.start_next_interval()
        elif res == b'j\n':
            timecube.restart_current_interval()
        elif res == b'k\n':
            timecube.pause()
        elif res == b'i\n':
            timecube.resume()
        elif res == b's\n':
            timecube.summary()
        elif res == b'c\n':
            timecube.config()


if __name__ == '__main__':
    # read config from file...
    asyncio.run(main())
