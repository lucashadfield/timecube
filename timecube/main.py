import ujson

import uasyncio as asyncio

from accelerometer import Accelerometer
from epaper1in54v2 import EPD
from screen import Screen
from state import Interval, Pause, Summary
from timecube import TimeCube


def load_config() -> dict:
    with open('config.json', 'r') as f:
        return ujson.loads(f.read())


async def main():
    config = load_config()

    display = EPD(
        config['screen']['spi'],
        config['screen']['cs_pin'],
        config['screen']['dc_pin'],
        config['screen']['rst_pin'],
        config['screen']['busy_pin'],
    )
    screen = Screen(display, config['screen']['annulus_radius'], config['screen']['annulus_thickness'])

    work_interval = Interval('work', config['timecube']['work_duration_s'])
    break_interval = Interval('break', config['timecube']['break_duration_s'])
    longbreak_interval = Interval('longbreak', config['timecube']['longbreak_duration_s'])
    pause = Pause('pause')
    summary = Summary('summary')

    timecube = TimeCube.from_config(
        screen,
        config['timecube']['n_work_loops'],
        work_interval,
        break_interval,
        longbreak_interval,
        pause,
        summary,
    )
    timecube()

    accelerometer = Accelerometer(
        config['accelerometer']['x_pin'],
        config['accelerometer']['y_pin'],
        config['accelerometer']['z_pin'],
        timecube.next,
        timecube.prev,
        timecube.pause,
        timecube.pause,
    )

    while True:
        await asyncio.sleep(0)


asyncio.run(main())
