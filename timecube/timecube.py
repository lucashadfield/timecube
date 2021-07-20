import asyncio
import sys
import time
from dataclasses import dataclass


def cycle(one_cycle):
    cycle_len = len(one_cycle)
    while True:
        for i in range(cycle_len):
            yield one_cycle[i], one_cycle[i + 1] if i + 1 < cycle_len else one_cycle[0]


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
        self.interval_state_start = None
        self.saved_interval_duration = 0
        self.state = 'run'

        self.summary_stats = {
            'work': 0,
            'break': 0,
            'longbreak': 0,
            'pause': 0,
            'work_overflow': 0,
            'break_overflow': 0,
            'longbreak_overflow': 0,
            'work_restarts': 0,
            'break_restarts': 0,
            'longbreak_restarts': 0,
        }

        # each object is only created once - need to re-zero after they end
        work_interval = Interval('work', work_duration_s, 'knock')
        break_interval = Interval('break', break_duration_s, 'knock knock')
        longbreak_interval = Interval(
            'longbreak', longbreak_duration_s, 'knock knock knock'
        )

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

    def print_summary_stats(self):
        print({k: round(v) for k, v in self.summary_stats.items()})

    def log_interval_stats(self, actual_duration):
        interval = self.current_interval
        self.summary_stats[interval.type] += actual_duration
        self.summary_stats[f'{interval.type}_overflow'] += max(
            actual_duration - interval.duration, 0
        )
        self.print_summary_stats()

    def log_stats(self, key, increment):
        self.summary_stats[key] += increment
        # self.print_summary_stats()

    async def start_interval_task(self):
        duration = self.current_interval.duration - self.saved_interval_duration
        print(f'starting {self.current_interval.type} for {duration} seconds')
        await asyncio.sleep(duration)
        print(f'finished {self.current_interval.type} ->  {self.next_interval.alarm}')
        # do end of task changes here + alarm

    def start_next_interval(self):
        if self.state == 'run':
            # logging
            print('next interval')
            interval_duration = time.time() - self.interval_state_start
            self.log_interval_stats(interval_duration + self.saved_interval_duration)

            # cancel current task (does nothing if not running)
            self.interval_task.cancel()

            # start next task
            self.saved_interval_duration = 0
            self.interval_id += 1
            self.interval_state_start = time.time()
            self.interval_task = asyncio.create_task(self.start_interval_task())

    def start_current_interval(self):
        if self.state == 'run':
            # start current task
            if (
                self.interval_state_start is not None
            ):  # skip if it's the very first task
                # logging
                print('this interval')
                interval_duration = time.time() - self.interval_state_start
                self.log_interval_stats(
                    interval_duration + self.saved_interval_duration
                )
                self.log_stats(f'{self.current_interval.type}_restarts', 1)

                # cancel current task (does nothing if not running)
                self.interval_task.cancel()

            # start current task
            self.saved_interval_duration = 0
            self.interval_state_start = time.time()
            self.interval_task = asyncio.create_task(self.start_interval_task())

    def pause(self):
        if self.state == 'run':
            self.state = 'pause'

            # logging
            print('paused')
            interval_duration = time.time() - self.interval_state_start

            # cancel current task (does nothing if not running)
            self.interval_task.cancel()

            # save the amount of time already spent on current interval
            self.saved_interval_duration += interval_duration
            # print(f'offset_duration = {self.offset_duration}')

            # start timer for pause
            self.interval_state_start = time.time()

    def resume(self):
        if self.state == 'pause':
            self.state = 'run'

            # logging
            print('resuming')
            pause_duration = time.time() - self.interval_state_start
            self.log_stats('pause', pause_duration)

            # restart the current task if it
            self.interval_state_start = time.time()
            if (
                self.saved_interval_duration < self.cycle[self.interval_id].duration
            ):  # time is still left on the current interval
                self.interval_task = asyncio.create_task(self.start_interval_task())

    def config(self):
        pass

    def summary(self):
        pass


@dataclass
class Interval:
    type: str  # 'work', 'break', 'longbreak'
    duration: int
    alarm: str


class Config:
    pass


async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader


async def main():
    timecube = TimeCube(3, 1, 2, 3)

    timecube.start_current_interval()
    print('this prints first')

    reader = await connect_stdin_stdout()
    while True:
        await asyncio.sleep(0)
        res = await reader.read(10)
        if res == b'l\n':
            timecube.start_next_interval()
        elif res == b'j\n':
            timecube.start_current_interval()
        elif res == b'k\n':
            timecube.pause()
        elif res == b'i\n':
            timecube.resume()
        elif res == b's\n':
            print(timecube.summary_stats)


if __name__ == '__main__':
    # read config from file...
    asyncio.run(main())
