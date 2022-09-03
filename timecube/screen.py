import extended_framebuf as framebuf
import font

WHITE = 0x00
BLACK = 0xFF
ANNULUS_X = 100
ANNULUS_Y = 100


class Screen:
    def __init__(self, display, annulus_radius, annulus_thickness, show_diagnostics):
        '''
        Create a screen that can draw shapes and text to the framebuffer
        and write to the display

        Args:
            display (Display): display to write framebuffer to
            annulus_radius (int): outer radius of the screen annulus in pixels
            annulus_thickness (int): thickness of the screen annulus in pixels
            show_diagnostics (bool): whether to draw diagnostics panel into the framebuffer for debugging
        '''

        self.display = display
        self.annulus_radius = annulus_radius
        self.annulus_thickness = annulus_thickness
        self.show_diagnostics = show_diagnostics

        # no initial rotation, accelerometer will call `update_screen_rotation`
        self.rotation_index = None

        # refresh screen
        self.buf = bytearray(self.display.width * self.display.height // 8)
        self.fb = framebuf.FrameBuffer(self.buf, self.display.height, self.display.width, framebuf.MONO_VLSB)

        self.diagnostics = {
            'battery': '',
            'charging': '',
            'interval': '',
            'rot_state': '',
            'interval_id': '',
            'delay': '',
        }

    def display_new_interval(
        self,
        is_fill_black,
        starting_time,
        starting_prop,
        draw_longbreak_icon,
    ):
        '''
        Display a new annulus and remaining time to the screen.
        Initialises the screen for full refresh then delegates to `update_interval_display` to draw.

        Args:
            is_fill_black (bool): sets whether this is a white annulus that fills with black (true) or black annulus
                that fills with white (false). Is used in subsequent calls to `update_interval_display`
            starting_time (int): the remaining time [0-99] in the interval, drawn in the centre of the annulus
            starting_prop (float): proportion [0-1] of the annulus to fill with black or white (depending on `is_fill_black`)
            draw_longbreak_icon (bool): whether to draw the longbreak icon in the bottom right of the screen.
        '''

        print(f'screen: starting interval, starting_time={starting_time}, starting_prop={starting_prop}')

        self.is_fill_black = is_fill_black
        self.display.init(self.display.FULL_UPDATE)
        self.update_interval_display(starting_time, starting_prop, draw_longbreak_icon)
        self.display.init(self.display.PART_UPDATE)

    def update_interval_display(self, remaining_time, remaining_prop, draw_longbreak_icon):
        '''
        Update the remaining time and proportion on the current annulus and redraw to the screen.

        Args:
            remaining_time (int): the remaining time [0-99] in the interval, drawn in the centre of the annulus
            remaining_prop (float): proportion [0-1] of the annulus to fill with black or white (depending on `is_fill_black`)
            draw_longbreak_icon (bool): whether to draw the longbreak icon in the bottom right of the screen.
        '''

        assert self.rotation_index is not None, "rotation_index is None"

        print(f'screen: updating interval, remaining_time={remaining_time}, remaining_prop={remaining_prop}')

        # zero out all pixels
        self.fb.fill(WHITE)

        # update annulus
        fill = BLACK if self.is_fill_black else WHITE
        completed_prop = 1 - remaining_prop

        # self.fb.fill_circle(
        #     100, 100, self.annulus_radius - self.annulus_thickness - 4, WHITE, self.rotation_index
        # )  # clear the centre of the circle

        # draw annulus
        self.fb.fill_annulus(
            ANNULUS_X, ANNULUS_Y, self.annulus_radius, self.annulus_thickness, completed_prop, fill, self.rotation_index
        )

        # draw annulus outlines in black
        self.fb.annulus(ANNULUS_X, ANNULUS_Y, self.annulus_radius, self.annulus_thickness, BLACK, self.rotation_index)

        # draw remaining time
        self._draw_central_glyphs(str(int(remaining_time)), ANNULUS_X, ANNULUS_Y)

        # draw longbreak icon
        if draw_longbreak_icon:
            self._draw_longbreak_icon()

        # draw diagnostics window
        if self.show_diagnostics:
            self._draw_diagnostics(update_display=False)

        # write buffer to screen
        self._display()

    def pause(self):
        # todo
        pass

    def resume(self):
        # todo
        pass

    def update_screen_rotation(self, accelerometer_state):
        '''
        Updates the screen rotation index.
        Does not redraw to screen.
        '''

        self.rotation_index = (1 - accelerometer_state) % 4
        print(
            f'screen: rotating screen to rotation_index {self.rotation_index}. accelerometer_state={accelerometer_state}'
        )

    def update_diagnostics(self, keys, values):
        '''
        Updates the diagnostics dict with new values and draws to screen if self.show_diagnostics == true.

        Args:
            keys (Union[str, List[str]]: key or list of keys to update
            values (Union[str, List[str]]: value of list of values to update
        '''

        if not isinstance(keys, list):
            keys = [keys]
            values = [values]

        for key, value in zip(keys, values):
            if self.diagnostics[key] != value:
                self.diagnostics[key] = value

        if self.show_diagnostics:
            self._draw_diagnostics()

    def _display(self):
        '''
        Display the framebuffer to the screen.
        '''

        self.display.set_frame_memory(self.buf, 0, 0, self.display.width, self.display.height)
        self.display.display_frame()

    def _draw_longbreak_icon(self):
        '''
        Draw a circle in the bottom right corner of the screen.
        Used to signify if a longbreak is up next
        '''

        self.fb.circle(180, 180, 9, BLACK, self.rotation_index)

    def _rotate_char(self, char):
        '''
        Converts a character into the corresponding, correctly rotated glyph
        e.g. '1' rotated to the right -> 'L'

        Args:
            char (str): unrotated desired character

        Returns (str): character from font glyphs
        '''

        return chr(ord('A') + int(char) + (10 * self.rotation_index))

    def _draw_central_glyphs(self, s, x, y):
        '''
        Draws the glyphs (digits or symbols) in the centre of the annulus

        Args:
            s (str): string to draw
            x (int): x position of centre
            y (int): y position of centre
        '''

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
                        WHITE,
                    )
                    x += min_width
                elif self.rotation_index == 1:
                    self.fb.blit(
                        fbc,
                        x - (full_height // 2),
                        y - (full_width // 2) - ((max_width - min_width) // 2),
                        WHITE,
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
                        WHITE,
                    )
                    x += min_width
                elif self.rotation_index == 3:
                    self.fb.blit(
                        fbc,
                        x - (full_height // 2),
                        y - (full_width // 2) - ((max_width - min_width) // 2),
                        WHITE,
                    )
                    y += min_width

    def _draw_diagnostics(self, update_display=True):
        '''
        Draws an overlay box with diagnostic info.

        Args:
            update_display (bool): whether or not to do a screen update after writing the new
            values to the buffer
        '''

        box_width = 160
        box_height = (len(self.diagnostics) + 1) * 10
        for y in range(box_height):
            self.fb.hline(2, 2 + y, box_width, WHITE, 0)
        self.fb.rect(2, 2, box_width, box_height, BLACK)

        vert_pos = 10
        for k, v in self.diagnostics.items():
            self.fb.text(f'{k}: {v}', 10, vert_pos, BLACK)
            vert_pos += 10

        if update_display:
            self._display()
