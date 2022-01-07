from machine import Pin, ADC
import time
from math import atan2, sqrt, pi

x = ADC(28)
y = ADC(27)
z = ADC(26)

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
# fmt:on


def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


curr_state = 1
new_state = None
while True:
    x_raw = x.read_u16()
    y_raw = y.read_u16()
    z_raw = z.read_u16()

    x_volt = map_range(x_raw, 0, 65535, 0, 3.3)
    y_volt = map_range(y_raw, 0, 65535, 0, 3.3)
    z_volt = map_range(z_raw, 0, 65535, 0, 3.3)

    x_g = (x_volt - 1.636004) / v_per_g
    y_g = (y_volt - 1.644265) / v_per_g
    z_g = (z_volt - 1.968865 + v_per_g) / v_per_g

    state = state_lookup.get((round(x_g), round(y_g), round(z_g)), None)
    if state != curr_state and state is not None:
        if state == new_state:
            print(state)
            curr_state = state
        else:
            new_state = state

    time.sleep(0.1)
