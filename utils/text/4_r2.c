#define out_width 64
#define out_height 64
static unsigned char out_bits[] = {
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff,
0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00,
0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff,
0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00,
0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff,
0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x00, 0x3f, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xfc, 0x00, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc,
0x00, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x00, 0xfc, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xfc, 0x01, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc,
0x01, 0xf8, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x03, 0xf8, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xfc, 0x07, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc,
0x07, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x0f, 0xe0, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xfc, 0x1f, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc,
0x1f, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x3f, 0x80, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xfc, 0x3f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc,
0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0xfe, 0x00, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xfc, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfd,
0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfd, 0xf8, 0x00, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xff, 0xf8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xff,
0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xff, 0xf0, 0x00, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xff, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xff,
0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xff, 0xc0, 0x00, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xff, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xff,
0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xff, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x0f, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};
