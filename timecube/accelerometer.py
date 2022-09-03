import uasyncio as asyncio
from machine import ADC


class Accelerometer:
    V_PER_G = 0.33
    X_OFFSET = 1.636004
    Y_OFFSET = 1.644265
    Z_OFFSET = 1.968865
    READING_RANGE_MIN = 0
    READING_RANGE_MAX = 65535
    VOLT_RANGE_MIN = 0
    VOLT_RANGE_MAX = 3.3

    # fmt:off
    state_lookup = {
        (0, 0, 1): 0,
        (0, -1, 0): 1, # pause
        (0, 0, -1): 2,
        (0, 1, 0): 3,
        (1, 0, 0): 4,
        (-1, 0, 0): 4
    }
    # fmt: on

    def __init__(
        self,
        x_pin: int,
        y_pin: int,
        z_pin: int,
        run_fn,
        next_fn,
        prev_fn,
        pause_fn,
        resume_fn,
        async_sleep_ms,
        diagnostics_callback,
    ):
        self.x = ADC(x_pin)
        self.y = ADC(y_pin)
        self.z = ADC(z_pin)
        self.run_fn = run_fn
        self.next_fn = next_fn
        self.prev_fn = prev_fn
        self.pause_fn = pause_fn
        self.resume_fn = resume_fn
        self.async_sleep_ms = async_sleep_ms
        self.diagnostics_callback = diagnostics_callback

        self.current_state = None
        asyncio.create_task(self.read_state())

    @staticmethod
    def map_range(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    async def read_state(self):
        while True:
            x_volt = self.map_range(
                self.x.read_u16(),
                self.READING_RANGE_MIN,
                self.READING_RANGE_MAX,
                self.VOLT_RANGE_MIN,
                self.VOLT_RANGE_MAX,
            )
            y_volt = self.map_range(
                self.y.read_u16(),
                self.READING_RANGE_MIN,
                self.READING_RANGE_MAX,
                self.VOLT_RANGE_MIN,
                self.VOLT_RANGE_MAX,
            )
            z_volt = self.map_range(
                self.z.read_u16(),
                self.READING_RANGE_MIN,
                self.READING_RANGE_MAX,
                self.VOLT_RANGE_MIN,
                self.VOLT_RANGE_MAX,
            )

            x_g = (x_volt - self.X_OFFSET) / self.V_PER_G
            y_g = (y_volt - self.Y_OFFSET) / self.V_PER_G
            z_g = (z_volt - self.Z_OFFSET + self.V_PER_G) / self.V_PER_G

            state = self.state_lookup.get((round(x_g), round(y_g), round(z_g)), None)

            if state is not None:
                if self.current_state is None:
                    # set initial state
                    self.current_state = state
                    self.run_fn(state)
                    self.diagnostics_callback('rot_state', self.current_state)
                else:
                    # check running state
                    if state != self.current_state:
                        # state changed
                        print(
                            f'accelerometer: updating state, current_state={self.current_state}, state={state}',
                        )
                        if state == 4:
                            self.pause_fn()
                        elif self.current_state == 4:
                            self.resume_fn()
                        elif (state - self.current_state == 1) or (state == 0 and self.current_state == 3):
                            self.next_fn(state)
                        elif (state - self.current_state == -1) or (state == 3 and self.current_state == 0):
                            self.prev_fn(state)
                        else:
                            print(
                                f'accelerometer: unmapped state transition, current_state={self.current_state}, state={state}'
                            )

                        self.current_state = state
                        self.diagnostics_callback('rot_state', self.current_state)

            await asyncio.sleep_ms(self.async_sleep_ms)
