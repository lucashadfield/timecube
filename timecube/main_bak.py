from machine import Pin
import time
import pyb

a = Pin(14, Pin.IN, Pin.PULL_DOWN)
b = Pin(7, Pin.IN, Pin.PULL_DOWN)
c = Pin(10, Pin.IN, Pin.PULL_DOWN)

while True:
    print(a.value(), b.value(), c.value(), 'yo')
    time.sleep(0.1)


# from machine import Pin, SPI
# import framebuf
# import utime
# import math
#
# # Display resolution
# EPD_WIDTH = 128
# EPD_HEIGHT = 296
#
# RST_PIN = 12
# DC_PIN = 8
# CS_PIN = 9
# BUSY_PIN = 13
#
# WF_PARTIAL_2IN9 = [
#     0x0,
#     0x40,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x80,
#     0x80,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x40,
#     0x40,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x80,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0A,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x1,
#     0x1,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x1,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x0,
#     0x22,
#     0x22,
#     0x22,
#     0x22,
#     0x22,
#     0x22,
#     0x0,
#     0x0,
#     0x0,
#     0x22,
#     0x17,
#     0x41,
#     0xB0,
#     0x32,
#     0x36,
# ]
#
#
# class EPaperDisplay(framebuf.FrameBuffer):
#     def __init__(self):
#         self.reset_pin = Pin(RST_PIN, Pin.OUT)
#
#         self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
#         self.cs_pin = Pin(CS_PIN, Pin.OUT)
#         self.width = EPD_WIDTH
#         self.height = EPD_HEIGHT
#
#         self.lut = WF_PARTIAL_2IN9
#
#         self.spi = SPI(1)
#         self.spi.init(baudrate=4000_000)
#         self.dc_pin = Pin(DC_PIN, Pin.OUT)
#
#         self.buffer = bytearray(self.height * self.width // 8)
#         super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
#         self.init()
#
#     @staticmethod
#     def digital_write(pin, value):
#         pin.value(value)
#
#     @staticmethod
#     def digital_read(pin):
#         return pin.value()
#
#     @staticmethod
#     def delay_ms(delaytime):
#         utime.sleep(delaytime / 1000.0)
#
#     def spi_writebyte(self, data):
#         self.spi.write(bytearray(data))
#
#     def module_exit(self):
#         self.digital_write(self.reset_pin, 0)
#
#     # Hardware reset
#     def reset(self):
#         self.digital_write(self.reset_pin, 1)
#         self.delay_ms(50)
#         self.digital_write(self.reset_pin, 0)
#         self.delay_ms(2)
#         self.digital_write(self.reset_pin, 1)
#         self.delay_ms(50)
#
#     def send_command(self, command):
#         self.digital_write(self.dc_pin, 0)
#         self.digital_write(self.cs_pin, 0)
#         self.spi_writebyte([command])
#         self.digital_write(self.cs_pin, 1)
#
#     def send_data(self, data):
#         self.digital_write(self.dc_pin, 1)
#         self.digital_write(self.cs_pin, 0)
#         self.spi_writebyte([data])
#         self.digital_write(self.cs_pin, 1)
#
#     def read_busy(self):
#         # print("e-Paper busy")
#         while self.digital_read(self.busy_pin) == 1:  # 0: idle, 1: busy
#             self.delay_ms(1)
#             # print("e-Paper busy release")
#
#     def turn_on_display(self):
#         self.send_command(0x22)  # DISPLAY_UPDATE_CONTROL_2
#         self.send_data(0xF7)
#         self.send_command(0x20)  # MASTER_ACTIVATION
#         self.read_busy()
#
#     def turn_on_display_partial(self):
#         self.send_command(0x22)  # DISPLAY_UPDATE_CONTROL_2
#         self.send_data(0x0F)
#         self.send_command(0x20)  # MASTER_ACTIVATION
#         self.read_busy()
#
#     def send_lut(self):
#         self.send_command(0x32)
#         for i in range(0, 153):
#             self.send_data(self.lut[i])
#         self.read_busy()
#
#     def set_window(self, x_start, y_start, x_end, y_end):
#         self.send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
#         # x point must be the multiple of 8 or the last 3 bits will be ignored
#         self.send_data((x_start >> 3) & 0xFF)
#         self.send_data((x_end >> 3) & 0xFF)
#         self.send_command(0x45)  # SET_RAM_Y_ADDRESS_START_END_POSITION
#         self.send_data(y_start & 0xFF)
#         self.send_data((y_start >> 8) & 0xFF)
#         self.send_data(y_end & 0xFF)
#         self.send_data((y_end >> 8) & 0xFF)
#
#     def set_cursor(self, x, y):
#         self.send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
#         self.send_data(x & 0xFF)
#
#         self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
#         self.send_data(y & 0xFF)
#         self.send_data((y >> 8) & 0xFF)
#         self.read_busy()
#
#     def init(self):
#         # EPD hardware init start
#         self.reset()
#
#         self.read_busy()
#         self.send_command(0x12)  # SWRESET
#         self.read_busy()
#
#         self.send_command(0x01)  # Driver output control
#         self.send_data(0x27)
#         self.send_data(0x01)
#         self.send_data(0x00)
#
#         self.send_command(0x11)  # data entry mode
#         self.send_data(0x03)
#
#         self.set_window(0, 0, self.width - 1, self.height - 1)
#
#         self.send_command(0x21)  # Display update control
#         self.send_data(0x00)
#         self.send_data(0x80)
#
#         self.set_cursor(0, 0)
#         self.read_busy()
#         # EPD hardware init end
#         return 0
#
#     def display(self, image):
#         if image is None:
#             return
#         self.send_command(0x24)  # WRITE_RAM
#         for j in range(0, self.height):
#             for i in range(0, int(self.width / 8)):
#                 self.send_data(image[i + j * int(self.width / 8)])
#         self.turn_on_display()
#
#     def display_base(self, image):
#         if image is None:
#             return
#         self.send_command(0x24)  # WRITE_RAM
#         for j in range(0, self.height):
#             for i in range(0, int(self.width / 8)):
#                 self.send_data(image[i + j * int(self.width / 8)])
#
#         self.send_command(0x26)  # WRITE_RAM
#         for j in range(0, self.height):
#             for i in range(0, int(self.width / 8)):
#                 self.send_data(image[i + j * int(self.width / 8)])
#
#         self.turn_on_display()
#
#     def display_partial(self, image):
#         if image is None:
#             return
#
#         self.digital_write(self.reset_pin, 0)
#         self.delay_ms(2)
#         self.digital_write(self.reset_pin, 1)
#         self.delay_ms(2)
#
#         self.send_lut()
#         self.send_command(0x37)
#         self.send_data(0x00)
#         self.send_data(0x00)
#         self.send_data(0x00)
#         self.send_data(0x00)
#         self.send_data(0x00)
#         self.send_data(0x40)
#         self.send_data(0x00)
#         self.send_data(0x00)
#         self.send_data(0x00)
#         self.send_data(0x00)
#
#         self.send_command(0x3C)  # BorderWavefrom
#         self.send_data(0x80)
#
#         self.send_command(0x22)
#         self.send_data(0xC0)
#         self.send_command(0x20)
#         self.read_busy()
#
#         self.set_window(0, 0, self.width - 1, self.height - 1)
#         self.set_cursor(0, 0)
#
#         self.send_command(0x24)  # WRITE_RAM
#         for j in range(0, self.height):
#             for i in range(0, int(self.width / 8)):
#                 self.send_data(image[i + j * int(self.width / 8)])
#         self.turn_on_display_partial()
#
#     def clear(self, color):
#         self.send_command(0x24)  # WRITE_RAM
#         for j in range(0, self.height):
#             for i in range(0, int(self.width / 8)):
#                 self.send_data(color)
#         self.turn_on_display()
#
#     def sleep(self):
#         self.send_command(0x10)  # DEEP_SLEEP_MODE
#         self.send_data(0x01)
#
#         self.delay_ms(2000)
#         self.module_exit()
#
#     @staticmethod
#     def colour(colour):
#         if colour == 'black':
#             return 0x00
#         if colour == 'white':
#             return 0xFF
#         raise AssertionError('unsupported colour')
#
#     def circle(self, x0, y0, radius, colour):
#         # Circle drawing function.  Will draw a single pixel wide circle with
#         # center at x0, y0 and the specified radius.
#         colour = self.colour(colour)
#
#         f = 1 - radius
#         ddF_x = 1
#         ddF_y = -2 * radius
#         x = 0
#         y = radius
#         self.pixel(x0, y0 + radius, colour)
#         self.pixel(x0, y0 - radius, colour)
#         self.pixel(x0 + radius, y0, colour)
#         self.pixel(x0 - radius, y0, colour)
#         while x < y:
#             if f >= 0:
#                 y -= 1
#                 ddF_y += 2
#                 f += ddF_y
#             x += 1
#             ddF_x += 2
#             f += ddF_x
#             self.pixel(x0 + x, y0 + y, colour)
#             self.pixel(x0 - x, y0 + y, colour)
#             self.pixel(x0 + x, y0 - y, colour)
#             self.pixel(x0 - x, y0 - y, colour)
#             self.pixel(x0 + y, y0 + x, colour)
#             self.pixel(x0 - y, y0 + x, colour)
#             self.pixel(x0 + y, y0 - x, colour)
#             self.pixel(x0 - y, y0 - x, colour)
#
#     def fill_circle(self, x0, y0, radius, colour):
#         # Filled circle drawing function.  Will draw a filled circule with
#         # center at x0, y0 and the specified radius.
#         colour = self.colour(colour)
#
#         self.vline(x0, y0 - radius, 2 * radius + 1, colour)
#         f = 1 - radius
#         ddF_x = 1
#         ddF_y = -2 * radius
#         x = 0
#         y = radius
#         while x < y:
#             if f >= 0:
#                 y -= 1
#                 ddF_y += 2
#                 f += ddF_y
#             x += 1
#             ddF_x += 2
#             f += ddF_x
#             self.vline(x0 + x, y0 - y, 2 * y + 1, colour)
#             self.vline(x0 + y, y0 - x, 2 * x + 1, colour)
#             self.vline(x0 - x, y0 - y, 2 * y + 1, colour)
#             self.vline(x0 - y, y0 - x, 2 * x + 1, colour)
#
#     def fill_triangle(self, x0, y0, x1, y1, x2, y2, colour):
#         # Filled triangle drawing function.  Will draw a filled triangle around
#         # the points (x0, y0), (x1, y1), and (x2, y2).
#         colour = self.colour(colour)
#
#         x0 = round(x0)
#         y0 = round(y0)
#         x1 = round(x1)
#         y1 = round(y1)
#         x2 = round(x2)
#         y2 = round(y2)
#
#         if y0 > y1:
#             y0, y1 = y1, y0
#             x0, x1 = x1, x0
#         if y1 > y2:
#             y2, y1 = y1, y2
#             x2, x1 = x1, x2
#         if y0 > y1:
#             y0, y1 = y1, y0
#             x0, x1 = x1, x0
#
#         a = 0
#         b = 0
#         y = 0
#         last = 0
#         if y0 == y2:
#             a = x0
#             b = x0
#             if x1 < a:
#                 a = x1
#             elif x1 > b:
#                 b = x1
#             if x2 < a:
#                 a = x2
#             elif x2 > b:
#                 b = x2
#             self.hline(a, y0, b - a + 1, colour)
#             return
#         dx01 = x1 - x0
#         dy01 = y1 - y0
#         dx02 = x2 - x0
#         dy02 = y2 - y0
#         dx12 = x2 - x1
#         dy12 = y2 - y1
#         if dy01 == 0:
#             dy01 = 1
#         if dy02 == 0:
#             dy02 = 1
#         if dy12 == 0:
#             dy12 = 1
#         sa = 0
#         sb = 0
#         if y1 == y2 or y0 == y1:
#             last = y1
#         else:
#             last = y1 - 1
#         for y in range(y0, last + 1):
#             a = x0 + sa // dy01
#             b = x0 + sb // dy02
#             sa += dx01
#             sb += dx02
#             if a > b:
#                 a, b = b, a
#             self.hline(a, y, b - a + 1, colour)
#         sa = dx12 * (y - y1)
#         sb = dx02 * (y - y0)
#         while y <= y2:
#             a = x1 + sa // dy12
#             b = x0 + sb // dy02
#             sa += dx12
#             sb += dx02
#             if a > b:
#                 a, b = b, a
#             self.hline(a, y, b - a + 1, colour)
#             y += 1
#
#     def donut_outline(self, centre_x, centre_y, radius, thickness, colour='black'):
#         self.circle(centre_x, centre_y, radius, colour)
#         self.circle(centre_x, centre_y, radius - thickness, colour)
#
#     def donut_segment(self, centre_x, centre_y, radius, thickness, percent, colour):
#         self.fill_circle(centre_x, centre_y, radius, 'black')
#         self.fill_circle(centre_x, centre_y, radius - thickness, 'white')
#
#         zero = (centre_x, centre_y - radius)
#         top_right = (centre_x + radius, centre_y - radius)
#         bottom_right = (centre_x + radius, centre_y + radius)
#         bottom_left = (centre_x - radius, centre_y + radius)
#         top_left = (centre_x - radius, centre_y - radius)
#
#         # fmt: off
#         angle = (percent / 100) * 360
#         if colour == 'black':
#             if angle == 360:
#                 return
#             if angle <= 315:
#                 # 1
#                 self.fill_triangle(centre_x, centre_y, zero[0], zero[1], top_left[0], top_left[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, zero[0], zero[1], centre_x + radius * math.tan(math.radians(angle - 360)), zero[1], 'white')
#                 return
#             if angle <= 225:
#                 # 2
#                 self.fill_triangle(centre_x, centre_y, top_left[0], top_left[1], bottom_left[0], bottom_left[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, top_left[0], top_left[1], top_left[0], centre_y - radius * math.tan(math.radians(angle - 270)), 'white')
#                 return
#             if angle <= 135:
#                 # 3
#                 self.fill_triangle(centre_x, centre_y, bottom_left[0], bottom_left[1], bottom_right[0], bottom_right[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, bottom_left[0], bottom_left[1], centre_x - radius * math.tan(math.radians(angle - 180)), bottom_left[1], 'white')
#                 return
#             if angle <= 45:
#                 # 4
#                 self.fill_triangle(centre_x, centre_y, bottom_right[0], bottom_right[1], top_right[0], top_right[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, bottom_right[0], bottom_right[1], top_right[0], centre_y + radius * math.tan(math.radians(angle - 90)), 'white',)
#                 return
#             if angle == 0:
#                 # 5
#                 self.fill_triangle(centre_x, centre_y, top_right[0], top_right[1], zero[0], zero[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, top_right[0], top_right[1], centre_x + radius * math.tan(math.radians(angle)), zero[1], 'white')
#         else:
#             if angle == 0:
#                 return
#             if angle >= 45:
#                 # 1
#                 self.fill_triangle(centre_x, centre_y, zero[0], zero[1], top_right[0], top_right[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, zero[0], zero[1], centre_x + radius * math.tan(math.radians(angle)), zero[1], 'white')
#                 return
#             if angle >= 135:
#                 # 2
#                 self.fill_triangle(centre_x, centre_y, top_right[0], top_right[1], bottom_right[0], bottom_right[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, top_right[0], top_right[1], top_right[0], centre_y + radius * math.tan(math.radians(angle - 90)), 'white')
#                 return
#             if angle >= 225:
#                 # 3
#                 self.fill_triangle(centre_x, centre_y, bottom_right[0], bottom_right[1], bottom_left[0], bottom_left[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, bottom_right[0], bottom_right[1], centre_x - radius * math.tan(math.radians(angle - 180)), bottom_left[1], 'white')
#                 return
#             if angle >= 315:
#                 # bug in here
#                 # 4
#                 self.fill_triangle(centre_x, centre_y, bottom_left[0], bottom_left[1], top_left[0], top_left[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, bottom_left[0], bottom_left[1], top_left[0], centre_y - radius * math.tan(math.radians(angle - 270)), 'white',)
#                 return
#             if angle == 360:
#                 # 5
#                 self.fill_triangle(centre_x, centre_y, top_left[0], top_left[1], zero[0], zero[1], 'white')
#             else:
#                 self.fill_triangle(centre_x, centre_y, top_left[0], top_left[1], centre_x + radius * math.tan(math.radians(angle - 360)), zero[1], 'white')
#         # fmt: on
#
#
# if __name__ == '__test__':
#     epd = EPaperDisplay()
#     epd.clear(0xFF)
#     epd.fill(0xFF)
#
#     epd.donut_segment(63, 147, 62, 18, 5, 'black')
#     epd.donut_outline(63, 147, 62, 18)
#     epd.display(epd.buffer)
#
#
# if __name__ == '__main__':
#     epd = EPaperDisplay()
#     epd.clear(0xFF)
#     epd.fill(0xFF)
#
#     epd.donut_segment(63, 147, 62, 18, 100, 'black')
#     epd.donut_outline(63, 147, 62, 18)
#     epd.display(epd.buffer)
#     epd.donut_segment(63, 147, 62, 18, 0, 'black')
#     epd.donut_outline(63, 147, 62, 18)
#     epd.text('WORK', 48, 144, 0x00)
#     epd.display(epd.buffer)
#     epd.display_partial(epd.buffer)
#
#     timer_mins = 20
#     for i in range(timer_mins):
#         epd.delay_ms(100)
#         epd.donut_segment(63, 147, 62, 18, (100 * (i + 1)) / timer_mins, 'black')
#         epd.donut_outline(63, 147, 62, 18)
#         epd.text('WORK', 48, 144, 0x00)
#         epd.display_partial(epd.buffer)
#
#     epd.text('WORK', 48, 144, 0xFF)
#     epd.display_partial(epd.buffer)
#     epd.text('BREAK', 44, 144, 0x00)
#     epd.display_partial(epd.buffer)
#
#     for i in range(timer_mins):
#         epd.delay_ms(100)
#         epd.donut_segment(63, 147, 62, 18, (100 * (i + 1)) / timer_mins, 'white')
#         epd.donut_outline(63, 147, 62, 18)
#         epd.text('WORK', 48, 144, 0x00)
#         epd.display_partial(epd.buffer)
