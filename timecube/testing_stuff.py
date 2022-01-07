def fill_triangle(x0, y0, x1, y1, x2, y2, colour):
    if colour == 'black':
        colour = 0x00
    else:
        colour = 0xff

    #         x0 = round(x0)
    #         y0 = round(y0)
    #         x1 = round(x1)
    #         y1 = round(y1)
    #         x2 = round(x2)
    #         y2 = round(y2)

    if y0 > y1:
        print('A')
        y0, y1 = y1, y0
        x0, x1 = x1, x0
    if y1 > y2:
        print('B')
        y2, y1 = y1, y2
        x2, x1 = x1, x2
    if y0 > y1:
        print('C')
        y0, y1 = y1, y0
        x0, x1 = x1, x0

    print('values', x0, y0, x1, y1, x2, y2)

    a = 0
    b = 0
    y = 0
    last = 0
    if y0 == y2:
        print('D')
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
        # self.hline(a, y0, b - a + 1, colour)
        print('hline A:', a, y0, b - a + 1)
        return
    dx01 = x1 - x0
    dy01 = y1 - y0
    dx02 = x2 - x0
    dy02 = y2 - y0
    dx12 = x2 - x1
    dy12 = y2 - y1
    if dy01 == 0:
        print('E')
        dy01 = 1
    if dy02 == 0:
        print('F')
        dy02 = 1
    if dy12 == 0:
        print('G')
        dy12 = 1
    sa = 0
    sb = 0
    if y1 == y2:# or y0 == y1:
        print('H')
        last = y1
    else:
        print('I')
        last = y1 - 1
    for y in range(y0, last + 1):
        print('J')
        a = x0 + sa // dy01
        b = x0 + sb // dy02
        sa += dx01
        sb += dx02
        if a > b:
            a, b = b, a
        # self.hline(a, y, b - a + 1, colour)
        print('hline B:', a, y, b - a + 1)
    sa = dx12 * (y - y1)
    sb = dx02 * (y - y0)
    iii = 0
    while y <= y2:
        a = x1 + sa // dy12
        b = x0 + sb // dy02
        sa += dx12
        sb += dx02
        if a > b:
            a, b = b, a
        # self.hline(a, y, b - a + 1, colour)
        print('hline C:', a, y, b - a + 1, iii)
        iii+=1
        y += 1

if __name__ == '__main__':
    fill_triangle(50,100,30,100,50,105,'black')