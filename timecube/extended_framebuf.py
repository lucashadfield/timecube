import framebuf
import math

MONO_VLSB = framebuf.MONO_VLSB
MONO_HLSB = framebuf.MONO_HLSB


class FrameBuffer(framebuf.FrameBuffer):
    N = 200

    def rotate(self, x, y, rotation_index):
        if rotation_index == 0:
            return x, y
        if rotation_index == 1:
            return self.N - y, x
        if rotation_index == 2:
            return self.N - x, self.N - y
        if rotation_index == 3:
            return y, self.N - x

    def pixel(self, x: int, y: int, c: int, rotation_index: int) -> None:
        x, y = self.rotate(x, y, rotation_index)
        super().pixel(x, y, c)

    def vline(self, x: int, y: int, h: int, c: int, rotation_index: int) -> None:
        x, y = self.rotate(x, y, rotation_index)
        if rotation_index == 0:
            super().vline(x, y, h, c)
        elif rotation_index == 1:
            super().hline(x - h + 1, y, h, c)
        elif rotation_index == 2:
            super().vline(x, y - h + 1, h, c)
        elif rotation_index == 3:
            super().hline(x, y, h, c)

    def hline(self, x: int, y: int, w: int, c: int, rotation_index: int) -> None:
        x, y = self.rotate(x, y, rotation_index)
        if rotation_index == 0:
            super().hline(x, y, w, c)
        elif rotation_index == 1:
            super().vline(x, y, w, c)
        elif rotation_index == 2:
            super().hline(x - w + 1, y, w, c)
        elif rotation_index == 3:
            super().vline(x, y - w + 1, w, c)

    def circle(self, x0: int, y0: int, r: int, c: int, rotation_index: int) -> None:
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
        self.pixel(x0, y0 + r, c, rotation_index)
        self.pixel(x0, y0 - r, c, rotation_index)
        self.pixel(x0 + r, y0, c, rotation_index)
        self.pixel(x0 - r, y0, c, rotation_index)
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            self.pixel(x0 + x, y0 + y, c, rotation_index)
            self.pixel(x0 - x, y0 + y, c, rotation_index)
            self.pixel(x0 + x, y0 - y, c, rotation_index)
            self.pixel(x0 - x, y0 - y, c, rotation_index)
            self.pixel(x0 + y, y0 + x, c, rotation_index)
            self.pixel(x0 - y, y0 + x, c, rotation_index)
            self.pixel(x0 + y, y0 - x, c, rotation_index)
            self.pixel(x0 - y, y0 - x, c, rotation_index)

    def fill_circle(self, x0: int, y0: int, r: int, c: int, rotation_index: int):
        self.vline(x0, y0 - r, 2 * r + 1, c, rotation_index)
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            self.vline(x0 + x, y0 - y, 2 * y + 1, c, rotation_index)
            self.vline(x0 + y, y0 - x, 2 * x + 1, c, rotation_index)
            self.vline(x0 - x, y0 - y, 2 * y + 1, c, rotation_index)
            self.vline(x0 - y, y0 - x, 2 * x + 1, c, rotation_index)

    def fill_triangle(
        self, x0: int, y0: int, x1: int, y1: int, x2: int, y2: int, colour: int, rotation_index: int
    ) -> None:
        x0 = int(x0)
        y0 = int(y0)
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0
        if y1 > y2:
            y2, y1 = y1, y2
            x2, x1 = x1, x2
        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0

        a = 0
        b = 0
        y = 0
        last = 0
        if y0 == y2:
            a = x0
            b = x0
            if x1 < a:
                a = x1
            elif x1 > b:
                b = x1
            if x2 < a:
                a = x2
            elif x2 > b:
                b = x2
            self.hline(a, y0, b - a + 1, colour, rotation_index)
            return
        dx01 = x1 - x0
        dy01 = y1 - y0
        dx02 = x2 - x0
        dy02 = y2 - y0
        dx12 = x2 - x1
        dy12 = y2 - y1
        if dy01 == 0:
            dy01 = 1
        if dy02 == 0:
            dy02 = 1
        if dy12 == 0:
            dy12 = 1
        sa = 0
        sb = 0
        if y1 == y2 or y0 == y1:
            last = y1
        else:
            last = y1 - 1
        for y in range(y0, last + 1):
            a = x0 + sa // dy01
            b = x0 + sb // dy02
            sa += dx01
            sb += dx02
            if a > b:
                a, b = b, a
            self.hline(a, y, b - a + 1, colour, rotation_index)
        sa = dx12 * (y - y1)
        sb = dx02 * (y - y0)
        while y <= y2:
            a = x1 + sa // dy12
            b = x0 + sb // dy02
            sa += dx12
            sb += dx02
            if a > b:
                a, b = b, a
            self.hline(a, y, b - a + 1, colour, rotation_index)
            y += 1

    def annulus(
        self, centre_x: int, centre_y: int, radius: int, thickness: int, colour: int, rotation_index: int
    ) -> None:
        self.circle(centre_x, centre_y, radius, colour, rotation_index)
        self.circle(centre_x, centre_y, radius - thickness, colour, rotation_index)

    def fill_annulus(
        self,
        centre_x: int,
        centre_y: int,
        radius: int,
        thickness: int,
        prop: float,
        colour: int,
        rotation_index: int,
    ) -> None:
        self.fill_circle(centre_x, centre_y, radius, 0xFF, rotation_index)
        self.fill_circle(centre_x, centre_y, radius - thickness, 0x00, rotation_index)

        zero = (centre_x, centre_y - radius)
        top_right = (centre_x + radius, centre_y - radius)
        bottom_right = (centre_x + radius, centre_y + radius)
        bottom_left = (centre_x - radius, centre_y + radius)
        top_left = (centre_x - radius, centre_y - radius)

        # fmt: off
        angle = prop * 360
        if colour == 0xff:
            if angle == 360:
                return
            if angle <= 315:
                # 1
                self.fill_triangle(centre_x, centre_y, zero[0], zero[1], top_left[0], top_left[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, zero[0], zero[1], centre_x + radius * math.tan(math.radians(angle - 360)), zero[1], 0x00, rotation_index)
                return
            if angle <= 225:
                # 2
                self.fill_triangle(centre_x, centre_y, top_left[0], top_left[1], bottom_left[0], bottom_left[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, top_left[0], top_left[1], top_left[0], centre_y - radius * math.tan(math.radians(angle - 270)), 0x00, rotation_index)
                return
            if angle <= 135:
                # 3
                self.fill_triangle(centre_x, centre_y, bottom_left[0], bottom_left[1], bottom_right[0], bottom_right[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, bottom_left[0], bottom_left[1], centre_x - radius * math.tan(math.radians(angle - 180)), bottom_left[1], 0x00, rotation_index)
                return
            if angle <= 45:
                # 4
                self.fill_triangle(centre_x, centre_y, bottom_right[0], bottom_right[1], top_right[0], top_right[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, bottom_right[0], bottom_right[1], top_right[0], centre_y + radius * math.tan(math.radians(angle - 90)), 0x00, rotation_index)
                return
            if angle == 0:
                # 5
                self.fill_triangle(centre_x, centre_y, top_right[0], top_right[1], zero[0], zero[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, top_right[0], top_right[1], centre_x + radius * math.tan(math.radians(angle)), zero[1], 0x00, rotation_index)
        else:
            if angle == 0:
                return
            if angle >= 45:
                # 1
                self.fill_triangle(centre_x, centre_y, zero[0], zero[1], top_right[0], top_right[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, zero[0], zero[1], centre_x + radius * math.tan(math.radians(angle)), zero[1], 0x00, rotation_index)
                return
            if angle >= 135:
                # 2
                self.fill_triangle(centre_x, centre_y, top_right[0], top_right[1], bottom_right[0], bottom_right[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, top_right[0], top_right[1], top_right[0], centre_y + radius * math.tan(math.radians(angle - 90)), 0x00, rotation_index)
                return
            if angle >= 225:
                # 3
                self.fill_triangle(centre_x, centre_y, bottom_right[0], bottom_right[1], bottom_left[0], bottom_left[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, bottom_right[0], bottom_right[1], centre_x - radius * math.tan(math.radians(angle - 180)), bottom_left[1], 0x00, rotation_index)
                return
            if angle >= 315:
                # bug in here
                # 4
                self.fill_triangle(centre_x, centre_y, bottom_left[0], bottom_left[1], top_left[0], top_left[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, bottom_left[0], bottom_left[1], top_left[0], centre_y - radius * math.tan(math.radians(angle - 270)), 0x00, rotation_index)
                return
            if angle == 360:
                # 5
                self.fill_triangle(centre_x, centre_y, top_left[0], top_left[1], zero[0], zero[1], 0x00, rotation_index)
            else:
                self.fill_triangle(centre_x, centre_y, top_left[0], top_left[1], centre_x + radius * math.tan(math.radians(angle - 360)), zero[1], 0x00, rotation_index)
        # fmt: on
