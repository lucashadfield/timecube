import uasyncio as asyncio
import ujson
import utime
from machine import Pin

from accelerometer import Accelerometer
from battery import Battery
from display import Display
from screen import Screen
from state import Interval, Pause, Summary
from timecube import TimeCube


def load_config() -> dict:
    with open('config.json', 'r') as f:
        return ujson.loads(f.read())


async def main():
    # turn off board LED
    red_led = Pin(18, Pin.OUT)
    green_led = Pin(19, Pin.OUT)

    red_led.value(1)
    green_led.value(1)

    config = load_config()
    if config['force_diagnostics']:
        show_diagnostics = True
    else:
        # check for diagnostics
        # todo: work out better way to do this
        show_diagnostics = False
        boot_pin = Pin(23)
        diagnostics_check_start = utime.ticks_ms()

        # if boot button is pressed while blue led is on, then show diagnostics
        while utime.ticks_diff(utime.ticks_ms(), diagnostics_check_start) < 1000:
            if not boot_pin.value():
                show_diagnostics = True
                red_led.value(0)
                utime.sleep_ms(100)
                red_led.value(1)

    blue_led = Pin(20, Pin.OUT)
    blue_led.value(1)

    display = Display(
        config['screen']['spi'],
        config['screen']['cs_pin'],
        config['screen']['dc_pin'],
        config['screen']['rst_pin'],
        config['screen']['busy_pin'],
    )
    screen = Screen(
        display, config['screen']['annulus_radius'], config['screen']['annulus_thickness'], show_diagnostics
    )

    diagnostics_callback = screen.update_diagnostics if show_diagnostics else lambda x, y: None

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
        diagnostics_callback,
        config['timecube']['delay_recency_weight'],
        config['timecube']['goto_prev_timeout_s'],
    )

    battery = Battery(
        config['battery']['voltage_pin'],
        config['battery']['charge_pin'],
        config['battery']['sample_period_ms'],
        diagnostics_callback,
    )

    accelerometer = Accelerometer(
        config['accelerometer']['x_pin'],
        config['accelerometer']['y_pin'],
        config['accelerometer']['z_pin'],
        timecube.run,
        timecube.next,
        timecube.prev,
        timecube.pause,
        timecube.pause,
        config['accelerometer']['sample_period_ms'],
        diagnostics_callback,
    )

    while True:
        await asyncio.sleep(0)


asyncio.run(main())
