#!/usr/bin/env python

# for x, r in enumerate([0xF4, 0xF3, 0xF2]):
#     for y, c in enumerate([0xEB, 0xEC, 0xED]):
#         file_id = 0x80010000 + c * 0x100 + r
#         print "%08X (%d, %d)" % (file_id, x, y)


import math
from numpy import *
import struct
import zlib

from dat import DatFile
import png


def heights(entry):
    j, unk1, file_id, offset, size1, timestamp, version, size2, unk2 = entry

    f.stream.seek(offset)

    j, k, l, m, n = struct.unpack("<LLLHH", f.stream.read(0x10))

    assert k == 0

    if m == 0xDA78:
        assert unk1 % 0x100 == 0x03
        f.stream.seek(offset)
        data = f.stream.read(size1 + 0x08)[12:]
        if j == 0:
            content = zlib.decompress(data)
            assert l == len(content)
        else:
            try:
                content = zlib.decompress(data)
            except zlib.error:
                return
    else:
        if unk1 % 0x100 == 0x02:
            f.stream.seek(offset)
            data = f.stream.read(size1 + 0x08)[8:]
            content = data
        else:
            return zeros((32, 32), dtype=uint16)

    header_id, unk1, unk2, unk3 = struct.unpack("<LLLL", content[:0x10])
    # print "%08X %08X %08X %08X" % (header_id, unk1, unk2, unk3)
    assert header_id == file_id
    if unk1 != 0:
        assert unk1 == 0x00200000 + header_id
    assert unk2 == 0x00000000
    assert unk3 == 0x00000441

    # len(content) may or may not be 0x1168 but we'll grab first 0x882 either way
    data = content[0x10:0x10 + (0x441 * 2)]
    height_map = zeros((32, 32), dtype=uint16)
    for y in range(32):
        for x in range(32):
            o = (y * (33) + x) * 2
            if len(data) > o + 2:
                h = struct.unpack("<H", data[o:o + 2])[0]
            else:
                h = 0  # @@@
            height_map[y, x] = h

    return height_map


# file_id = 0x80010CFA

# filename = "LOTRO/client_cell_1.dat"
# f = DatFile(filename)
# height_map = heights(f.find_file(file_id))

## text

# for row in height_map:
#     for height in row:
#         print "%4X" % height,
#     print


## log zebra

# import math
# pixels = {}
# for y in range(32):
#     for x in range(32):
#         height = height_map[y][x]
#         c = int(math.log(((16 * height) % 65535) + 1, 1.045))
#         pixels[(y, 32 - x - 1)] = (c, c, c)
# png.output_png("%08X.png" % file_id, 32, 32, pixels)

# 0 46 154 88 1800 251 255 128 2800 224 108 31 3500 200 55 55 4000 215 244 244


def hillshade(cell, xres=1, yres=1, azimuth=315.0, altitude=45.0, z=1.0, scale=0.5):
    window = []

    for row in range(3):
        for col in range(3):
            window.append(cell[row:(row + cell.shape[0] - 2), col:(col + cell.shape[1] - 2)])

    x = ((z * window[0] + z * window[3] + z * window[3] + z * window[6]) \
       - (z * window[2] + z * window[5] + z * window[5] + z * window[8])) \
      / (8.0 * xres * scale)

    y = ((z * window[6] + z * window[7] + z * window[7] + z * window[8]) \
       - (z * window[0] + z * window[1] + z * window[1] + z * window[2])) \
      / (8.0 * yres * scale)

    rad2deg = 180.0 / math.pi

    slope = 90.0 - arctan(sqrt(x * x + y * y)) * rad2deg
    aspect = arctan2(x, y)
    deg2rad = math.pi / 180.0

    shaded = sin(altitude * deg2rad) * sin(slope * deg2rad) \
           + cos(altitude * deg2rad) * cos(slope * deg2rad) \
           * cos((azimuth - 90.0) * deg2rad - aspect)

    shaded = shaded * 255

    return shaded


colour_map = [
    (0, 46, 154, 88),
    (1800, 251, 255, 128),
    (2800, 224, 108, 31),
    (3500, 200, 55, 55),
    (4000, 215, 244, 244),
]


def interpolate(height, hstart, hfinish, start, finish):
    ratio = float(height - hstart) / (hfinish - hstart)
    return (
        int(start[0] + ratio * (finish[0] - start[0])),
        int(start[1] + ratio * (finish[1] - start[1])),
        int(start[2] + ratio * (finish[2] - start[2])),
    )

colour_map = [
    (1, (255, 0, 255)),
    (1024, (0, 0, 255)),
    (8192, (46, 154, 88)),
    (16384, (251, 255, 128)),
    (32768, (224, 108, 31)),
    (50000, (200, 55, 55)),
    (65536, (255, 255, 255)),
]


def colour_for_height(height):
    lbound = 0
    lcolor = (0, 0, 0)

    for ubound, ucolor in colour_map:
        if height < ubound:
            return interpolate(height, lbound, ubound, lcolor, ucolor)
        lbound, lcolor = ubound, ucolor


filename = "LOTRO/client_cell_1.dat"
f = DatFile(filename)

height_map = {}
hill_shade = {}

SIZE = 7682

pixels = zeros((SIZE, SIZE, 3), dtype=uint8)

for y in range(64, SIZE - 32):
    for x in range(32, SIZE - 32):
# for y in range(1000, 2000):
#     for x in range(4500, 5500):
        cy, py = divmod(y, 30)
        cx, px = divmod(x, 30)
        file_id = 0x80020000 + cy * 0x100 + cx
        if file_id not in height_map:
            print "loading %08X" % file_id
            height_map[file_id] = heights(f.find_file(file_id))
            if height_map[file_id] is not None:
                print "calculating hillshade"
                hill_shade[file_id] = hillshade(height_map[file_id])
            else:
                hill_shade[file_id] = None
        if hill_shade[file_id] is not None:
            hs = hill_shade[file_id]
            hm = height_map[file_id]
            c = 128 - int(hs[py, px]) / 4
            r, g, b = [cc * (c / 255.) for cc in colour_for_height(hm[py, px])]
            pixels[y, SIZE - x] = (r, g, b)
#             height = hm[py][px]
#             pixels[y, SIZE - x] = colour_for_height(height)
print "outputing"
png.output_png("heights.png", SIZE, SIZE, pixels)
