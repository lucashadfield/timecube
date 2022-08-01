from epaper1in54v2 import EPD
import framebuffer
import framebuf
import font

WHITE = 0x00
BLACK = 0xFF


class Screen:
    N = 200

    def __init__(
        self,
        display: EPD,
        annulus_radius,
        annulus_thickness,
    ):
        self.annulus_radius = annulus_radius
        self.annulus_thickness = annulus_thickness

        self.display = display
        self.rotation_index = 1
        self.is_fill_black = True

        # refresh screen
        self.buf = bytearray(self.display.width * self.display.height // 8)
        self.fb = framebuffer.ExtendedFrameBuffer(
            self.buf, self.display.height, self.display.width, framebuffer.MONO_VLSB
        )
        self.fb.fill(0x00)
        self.display.init(self.display.FULL_UPDATE)
        self._display()
        self.display.init(self.display.PART_UPDATE)

    def _rotate_char(self, char):
        return chr(ord('A') + int(char) + (10 * self.rotation_index))

    def _print_string(self, s, x, y):
        glyphs = []
        for char in s:
            glyph = font.get_ch(self._rotate_char(char))
            glyphs.append((glyph[0], glyph[1], glyph[2], font._min_width[char]))
        # glyphs = [font.get_ch(self._rotate_char(char)) for char in s]
        full_width = sum([g[3] for g in glyphs])
        full_height = max([g[1] for g in glyphs])

        if self.rotation_index in (0, 1):
            for glyph, height, max_width, min_width in glyphs:
                fontbuf = bytearray(glyph)
                fbc = framebuf.FrameBuffer(fontbuf, max_width, height, framebuf.MONO_HLSB)
                if self.rotation_index == 0:
                    self.fb.blit(
                        fbc,
                        x - (full_width // 2) - ((max_width - min_width) // 2),
                        y - (full_height // 2),
                        0x00,
                    )
                    x += min_width
                elif self.rotation_index == 1:
                    self.fb.blit(
                        fbc,
                        x - (full_height // 2),
                        y - (full_width // 2) - ((max_width - min_width) // 2),
                        0x00,
                    )
                    y += min_width
        else:
            for glyph, height, max_width, min_width in glyphs[::-1]:
                fontbuf = bytearray(glyph)
                fbc = framebuf.FrameBuffer(fontbuf, max_width, height, framebuf.MONO_HLSB)
                if self.rotation_index == 2:
                    self.fb.blit(
                        fbc,
                        x - (full_width // 2) - ((max_width - min_width) // 2),
                        y - (full_height // 2),
                        0x00,
                    )
                    x += min_width
                elif self.rotation_index == 3:
                    self.fb.blit(
                        fbc,
                        x - (full_height // 2),
                        y - (full_width // 2) - ((max_width - min_width) // 2),
                        0x00,
                    )
                    y += min_width

    def _display(self):
        self.display.set_frame_memory(
            self.buf, 0, 0, self.display.width, self.display.height
        )  # todo: only set the diff pixels based on smallest bounding box
        self.display.display_frame()

    def _next_symbol(self, next_interval: str):
        # todo: fix this hack
        # draw circles in all corners
        for rotation_index in range(4):
            self.fb.fill_circle(190, 190, 9, 0x00, rotation_index)

        if next_interval == 'work':
            # solid circle left
            self.fb.fill_circle(190, 190, 9, 0xFF, self.rotation_index)
        elif next_interval in ('break', 'longbreak'):
            # open circle left
            self.fb.circle(190, 190, 9, 0xFF, self.rotation_index)
            if next_interval == 'longbreak':
                # open circle w/ line left
                self.fb.vline(190, 181, 18, 0xFF, self.rotation_index)

    def start_interval(
        self,
        is_fill_black: bool,
        remaining_time: int,
        remaining_prop: float = 1.0,
        next_interval: str = None,
    ):
        '''Create a annulus and remaining time value and perform full refresh'''
        assert remaining_time <= 99
        assert remaining_prop <= 1

        # start an annulus
        self.is_fill_black = is_fill_black
        self.display.init(self.display.FULL_UPDATE)
        self.update_interval(remaining_time, remaining_prop, next_interval)
        self.display.init(self.display.PART_UPDATE)

    def update_interval(self, remaining_time: int, remaining_prop: float, next_interval: str = None):
        '''Update existing annulus with new values and perform partial refresh'''
        print('screen: ', remaining_time, remaining_prop)
        assert remaining_time <= 99
        assert remaining_prop <= 1

        # update annulus
        fill = BLACK if self.is_fill_black else WHITE
        completed_prop = 1 - remaining_prop
        self.fb.fill_circle(
            100, 100, self.annulus_radius - self.annulus_thickness - 4, WHITE, self.rotation_index
        )  # clear the centre of the circle
        self.fb.fill_annulus(
            100, 100, self.annulus_radius, self.annulus_thickness, completed_prop, fill, self.rotation_index
        )
        self.fb.annulus(
            100, 100, self.annulus_radius, self.annulus_thickness, BLACK, self.rotation_index
        )  # outline

        # time
        self._print_string(str(int(remaining_time)), 100, 100)

        # next interval symbol
        if next_interval is not None:
            self._next_symbol(next_interval)

        self._display()

    def pause(self):
        # todo, right now just draw a circle
        self.fb.fill_circle(100, 100, 20, BLACK, self.rotation_index)
        self._display()

    def resume(self):
        # todo
        pass

    def rotate_right(self):
        print('rotating screen right')
        self.rotation_index = (self.rotation_index + 1) % 4

    def rotate_left(self):
        print('rotating screen left')
        self.rotation_index = (self.rotation_index - 1) % 4
