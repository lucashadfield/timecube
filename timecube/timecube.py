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
    def __init__(self, config):
        self.config = config

        self.interval_id = None
        self.interval_task = None
        self.saved_interval_duration = None

        self.state_start = None
        self.state = None

        self.summary_stats = None
        self.interval_cycle = None

    def initialise(self):
        work_interval = Interval('work', self.config['work_duration_s'], 'knock')
        break_interval = Interval('break', self.config['break_duration_s'], 'knock knock')
        longbreak_interval = Interval('longbreak', self.config['longbreak_duration_s'], 'knock knock knock')

        self.interval_cycle = []
        for n in range(self.config['n_work_loops'] - 1):
            self.interval_cycle.append(work_interval)
            self.interval_cycle.append(break_interval)
        self.interval_cycle.append(work_interval)
        self.interval_cycle.append(longbreak_interval)

        self.interval_id = 0
        self.saved_interval_duration = 0

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

    @property
    def current_interval(self):
        return self.interval_cycle[self.interval_id % len(self.interval_cycle)]

    @property
    def next_interval(self):
        return self.interval_cycle[(self.interval_id + 1) % len(self.interval_cycle)]

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
        if isinstance(self.state, Interval):
            self.interval_task.cancel()
            if isinstance(self.state, Interval):
                self.saved_interval_duration += self.transition_state('pause')
            else:
                self.transition_state('pause')

            # do pause things

    def summary(self):
        if isinstance(self.state, Interval) or self.state == 'pause':
            self.interval_task.cancel()
            if isinstance(self.state, Interval):
                self.saved_interval_duration += self.transition_state('summary')
            else:
                self.transition_state('summary')

            # do summary things

    def config_mode(self):
        if self.state != 'config':
            # enter config mode
            self.interval_task.cancel()
            if isinstance(self.state, Interval):
                self.saved_interval_duration += self.transition_state('config')
            else:
                self.transition_state('config')

            self.config_hash = hash(str(self.config))
            self.config_id = 0
            self.config_next()
            # do config things
        else:
            # exit config mode
            if self.config_hash != hash(str(self.config)):
                print('diff')
                # new config
                self.initialise()
                self.start()
            else:
                self.transition_state(self.current_interval)
                self.interval_task = asyncio.create_task(
                    self.start_interval_task(self.saved_interval_duration)
                )

    def resume(self):
        if self.state in ('pause', 'summary'):
            self.transition_state(self.current_interval)
            self.interval_task = asyncio.create_task(self.start_interval_task(self.saved_interval_duration))

    def config_next(self):
        self.config_id = (self.config_id + 1) % len(self.config)
        config_item = list(self.config.keys())[self.config_id]
        print(f'configuring {config_item}: {self.config[config_item]}')

    def config_increment(self):
        config_item = list(self.config.keys())[self.config_id]
        self.config[config_item] = min(self.config[config_item] + 1, 30000)
        print(f'{config_item}: {self.config[config_item]}')

    def config_decrement(self):
        config_item = list(self.config.keys())[self.config_id]
        self.config[config_item] = max(self.config[config_item] - 1, 1)
        print(f'{config_item}: {self.config[config_item]}')


class Config:
    pass


async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader


async def main():
    config = {'n_work_loops': 3, 'work_duration_s': 5, 'break_duration_s': 1, 'longbreak_duration_s': 2}

    timecube = TimeCube(config)

    timecube.initialise()
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
            timecube.config_mode()
        elif res == b'0\n':
            timecube.config_next()
        elif res == b'-\n':
            timecube.config_decrement()
        elif res == b'=\n':
            timecube.config_increment()


if __name__ == '__main__':
    # read config from file...
    asyncio.run(main())
