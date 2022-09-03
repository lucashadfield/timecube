import uasyncio as asyncio
from machine import ADC
from machine import Pin


class Battery:
    def __init__(self, voltage_pin: int, charge_pin: int, async_sleep_ms, diagnostics_callback):
        self.voltage = ADC(voltage_pin)
        self.charge = Pin(charge_pin, Pin.IN, Pin.PULL_DOWN)
        self.async_sleep_ms = async_sleep_ms
        self.diagnostics_callback = diagnostics_callback

        asyncio.create_task(self.read_state())

    async def read_state(self):
        while True:
            # 2 * 3.3 * self.pin_voltage.read_u16() / 65535 -> / 9930
            voltage_reading = self.voltage.read_u16() / 9930
            # max voltage reading = 3.71
            # min voltage reading = 3.22
            # range = 0.49

            if voltage_reading > 4.2:
                # must be usb
                battery_level = '?'
            else:
                battery_level = f'{max(min((voltage_reading - 3.22) / 0.49, 1), 0):.0%}'
            self.diagnostics_callback(
                ['battery', 'charging'], [f'{battery_level} {voltage_reading:.2f}V', self.charge.value()]
            )

            await asyncio.sleep_ms(self.async_sleep_ms)
