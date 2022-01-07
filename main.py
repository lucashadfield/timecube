import uasyncio as asyncio
import sys
import utime

# from dataclasses import dataclass
from collections import namedtuple
from math import ceil, floor

from machine import Pin, ADC


# @dataclass
# class Interval:
#     type: str  # 'work', 'break', 'longbreak'
#     duration: int
#     alarm: str

Interval = namedtuple('Interval', ['type', 'duration', 'alarm'])


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
        now = utime.ticks_ms()
        duration = utime.ticks_diff(now, self.state_start) / 1000
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
        print({k: round(v, 2) for k, v in self.summary_stats.items()})

    async def start_interval_task(self, offset=0):
        duration = self.current_interval.duration - offset
        if duration > 0:
            print('starting {} for {} seconds'.format(self.current_interval.type, duration))

            step_size = 1  # 1 second
            n_steps = ceil(duration / step_size)
            first_step = duration - (n_steps - 1) * step_size

            start_time_tmp = utime.ticks_ms()
            for i in range(n_steps):
                await asyncio.sleep(step_size if i else first_step)
                print('{:.0%}'.format((floor(offset) + (i + 1)) / self.current_interval.duration))

            print('finished {} ->  {}'.format(self.current_interval.type, self.next_interval.alarm))

            # print(utime.ticks_diff(utime.ticks_ms(), start_time_tmp))

            # do end of task changes here + alarm

    def start(self):
        self.state_start = utime.ticks_ms()
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

            self.summary_stats['{}_restarts'.format(self.current_interval.type)] += 1
            self.transition_state(self.current_interval)
            self.interval_task = asyncio.create_task(self.start_interval_task())

    def pause_resume(self):
        if isinstance(self.state, Interval):
            self.interval_task.cancel()
            if isinstance(self.state, Interval):
                self.saved_interval_duration += self.transition_state('pause')
            else:
                self.transition_state('pause')
            print(self.state)
        elif self.state in ('pause', 'summary'):
            self.transition_state(self.current_interval)
            print(self.state)
            self.interval_task = asyncio.create_task(self.start_interval_task(self.saved_interval_duration))

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
        print('configuring {}: {}'.format(config_item, self.config[config_item]))

    def config_increment(self):
        config_item = list(self.config.keys())[self.config_id]
        self.config[config_item] = min(self.config[config_item] + 1, 30000)
        print('{}: {}'.format(config_item, self.config[config_item]))

    def config_decrement(self):
        config_item = list(self.config.keys())[self.config_id]
        self.config[config_item] = max(self.config[config_item] - 1, 1)
        print('{}: {}'.format(config_item, self.config[config_item]))


class Config:
    pass


class Button:
    def __init__(self, pin, on_press=None, on_release=None, debounce_ms=50):
        self.pin = pin
        self.on_press = on_press
        self.on_release = on_release
        self.debounce_ms = debounce_ms
        self.state = self.pin.value()
        asyncio.create_task(self.check())

    def __call__(self):
        return self.state

    async def check(self):
        while True:
            state = self.pin.value()
            if state != self.state:
                self.state = state
                if state == 0 and self.on_release:
                    self.on_release()
                elif state == 1 and self.on_press:
                    self.on_press()
            await asyncio.sleep_ms(self.debounce_ms)


class TiltSensor:
    v_per_g = 0.33
    # fmt:off
    state_lookup = {
        (0, 0, 1): 1,
        (-1, 0, 0): 2,
        (0, 0, -1): 3,
        (1, 0, 0): 4,
        (0, -1, 0): 5,  # pause
        (0, 1, 0): 5 # pause
    }
    # fmt: on

    def __init__(self, pin_x, pin_y, pin_z, next_fn, prev_fn, pause_fn, resume_fn):
        self.x = ADC(pin_x)
        self.y = ADC(pin_y)
        self.z = ADC(pin_z)
        self.next_fn = next_fn
        self.prev_fn = prev_fn
        self.pause_fn = pause_fn
        self.resume_fn = resume_fn
        self.curr_state = 1
        self.new_state = None
        asyncio.create_task(self.read_state())

    @staticmethod
    def map_range(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    async def read_state(self):
        while True:
            x_raw = self.x.read_u16()
            y_raw = self.y.read_u16()
            z_raw = self.z.read_u16()

            x_volt = self.map_range(x_raw, 0, 65535, 0, 3.3)
            y_volt = self.map_range(y_raw, 0, 65535, 0, 3.3)
            z_volt = self.map_range(z_raw, 0, 65535, 0, 3.3)

            x_g = (x_volt - 1.636004) / self.v_per_g
            y_g = (y_volt - 1.644265) / self.v_per_g
            z_g = (z_volt - 1.968865 + self.v_per_g) / self.v_per_g

            state = self.state_lookup.get((round(x_g), round(y_g), round(z_g)), None)
            if state != self.curr_state and state is not None:
                if state == self.new_state:
                    # changed
                    if (state - self.curr_state == 1) or (state == 1 and self.curr_state == 4):
                        self.next_fn()
                    elif (state - self.curr_state == -1) or (state == 4 and self.curr_state == 1):
                        self.prev_fn()
                    elif state == 5:
                        self.pause_fn()
                    elif self.curr_state == 5 and state != 5:
                        self.resume_fn()

                    self.curr_state = state
                else:
                    self.new_state = state

            await asyncio.sleep_ms(100)


async def main():
    config = {'n_work_loops': 3, 'work_duration_s': 5, 'break_duration_s': 1, 'longbreak_duration_s': 2}

    timecube = TimeCube(config)

    timecube.initialise()
    timecube.start()
    print('this prints first')

    # buttons
    restart_pin = Pin(14, Pin.IN, Pin.PULL_DOWN)
    restart = Button(restart_pin, timecube.restart_current_interval)

    next_pin = Pin(10, Pin.IN, Pin.PULL_DOWN)
    next = Button(next_pin, timecube.start_next_interval)

    pause_pin = Pin(7, Pin.IN, Pin.PULL_DOWN)
    pause = Button(pause_pin, timecube.pause_resume)

    sensor = TiltSensor(
        28,
        27,
        26,
        timecube.start_next_interval,
        timecube.restart_current_interval,
        timecube.pause_resume,
        timecube.pause_resume,
    )

    while True:
        await asyncio.sleep(0)

    # config_decrement = Pin(14, Pin.IN, Pin.PULL_DOWN)
    # config_increment = Pin(15, Pin.IN, Pin.PULL_DOWN)

    # while True:
    #     if config_decrement.value() and config_increment.value():
    #         timecube.config_mode()
    #     elif next.value():
    #         timecube.start_next_interval()
    #     elif restart.value():
    #         timecube.restart_current_interval()
    #     elif pause.value():
    #         timecube.pause_resume()
    #     asyncio.sleep_ms(50)

    # reader = await connect_stdin_stdout()
    # while True:
    #     await asyncio.sleep(0)
    #     # res = await reader.read(10)
    #     res = b'x\n'
    #     if res == b'l\n':  # next
    #         timecube.start_next_interval()
    #     elif res == b'j\n':  # restart
    #         timecube.restart_current_interval()
    #     elif res == b'k\n':
    #         timecube.pause()
    #     elif res == b'i\n':
    #         timecube.resume()
    #     elif res == b's\n':
    #         timecube.summary()
    #     elif res == b'c\n':
    #         timecube.config_mode()
    #     elif res == b'0\n':
    #         timecube.config_next()
    #     elif res == b'-\n':
    #         timecube.config_decrement()
    #     elif res == b'=\n':
    #         timecube.config_increment()

    # read config from file...


asyncio.run(main())
# button = Button(14)
# while True:
#     print(button.pressed())
