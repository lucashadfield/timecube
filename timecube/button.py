import uasyncio as asyncio


class Button:
    def __init__(
        self,
        pin: int,
        on_press=None,
        on_release=None,
        debounce_ms: int = 50,
    ):
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
