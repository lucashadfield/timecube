import uasyncio as asyncio
from machine import ADC


class Accelerometer:
    v_per_g = 0.33
    # fmt:off
    state_lookup = {
        (0, 0, 1): 1,
        (-1, 0, 0): 2,
        (0, 0, -1): 3,
        (1, 0, 0): 4,
        (0, -1, 0): 5, # pause
        (0, 1, 0): 5
    }
    # fmt: on

    def __init__(
        self,
        pin_x: int,
        pin_y: int,
        pin_z: int,
        next_fn,
        prev_fn,
        pause_fn,
        resume_fn,
    ):
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
