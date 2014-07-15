#!/usr/bin/env python

import os.path
import png
import struct
import zlib

from dat import DatFile


def rgb565(c):
    r, g, b = c // 2048, (c // 32) % 64, c % 32
    return r * 8, g * 4, b * 8


def image_0x15(header_id, width, height, data):
    pixels = {}
    apixels = {}
    for y in range(height):
        for x in range(width):
            o = (y * width + x) * 4
            c1, c2, c3, c4 = map(ord, data[o:o + 4])
            pixels[(x, y)] = (c3, c2, c1)
            apixels[(x, y)] = (c4, c4, c4)
    png.output_png("surface/%08X_015.png" % header_id, width, height, pixels)
    png.output_png("surface/%08X_015_a.png" % header_id, width, height, apixels)


def image_0x14(header_id, width, height, data):
    pixels = {}
    for y in range(height):
        for x in range(width):
            o = (y * width + x) * 3
            c1, c2, c3 = map(ord, data[o:o + 3])
            pixels[(x, y)] = (c3, c2, c1)
    png.output_png("surface/%08X_014.png" % header_id, width, height, pixels)


def image_0x31545844(header_id, width, height, data):
    pixels = {}

    lngth = width * height // 2
    for bb in range(lngth // 8):
        o = bb * 8
        blk = map(ord, data[o:o + 8])

        c0 = blk[1] * 256 + blk[0]
        c1 = blk[3] * 256 + blk[2]

        c0r, c0g, c0b = rgb565(c0)
        c1r, c1g, c1b = rgb565(c1)

        if c0 > c1:
            c2r = (2 * c0r + 1 * c1r) // 3
            c2g = (2 * c0g + 1 * c1g) // 3
            c2b = (2 * c0b + 1 * c1b) // 3
            c3r = (1 * c0r + 2 * c1r) // 3
            c3g = (1 * c0g + 2 * c1g) // 3
            c3b = (1 * c0b + 2 * c1b) // 3
        else:
            c2r = (1 * c0r + 1 * c1r) // 2
            c2g = (1 * c0g + 1 * c1g) // 2
            c2b = (1 * c0b + 1 * c1b) // 2
            c3r = 0  # @@@
            c3g = 0  # @@@
            c3b = 0  # @@@

        for i in range(4):
            for j in range(4):
                b = blk[4 + i]
                if j == 0:
                    b2 = (b // 1) % 4
                elif j == 1:
                    b2 = (b // 4) % 4
                elif j == 2:
                    b2 = (b // 16) % 4
                elif j == 3:
                    b2 = (b // 64) % 4

                x = (bb % (width // 4)) * 4 + j
                y = (bb // (width // 4)) * 4 + i

                if b2 == 0:
                    pixels[(x, y)] = c0r, c0g, c0b
                elif b2 == 1:
                    pixels[(x, y)] = c1r, c1g, c1b
                elif b2 == 2:
                    pixels[(x, y)] = c2r, c2g, c2b
                elif b2 == 3:
                    pixels[(x, y)] = c3r, c3g, c3b

    png.output_png("surface/%08X_DXT1.png" % header_id, width, height, pixels)


def image_0x33545844(header_id, width, height, data):
    pixels = {}

    lngth = width * height
    for bb in range(lngth // 16):
        o = bb * 16
        # ignore alpha for now
        blk = map(ord, data[o + 8:o + 16])

        c0 = blk[1] * 256 + blk[0]
        c1 = blk[3] * 256 + blk[2]

        c0r, c0g, c0b = rgb565(c0)
        c1r, c1g, c1b = rgb565(c1)

        c2r = (2 * c0r + 1 * c1r) // 3
        c2g = (2 * c0g + 1 * c1g) // 3
        c2b = (2 * c0b + 1 * c1b) // 3
        c3r = (1 * c0r + 2 * c1r) // 3
        c3g = (1 * c0g + 2 * c1g) // 3
        c3b = (1 * c0b + 2 * c1b) // 3

        for i in range(4):
            for j in range(4):
                b = blk[4 + i]
                if j == 0:
                    b2 = (b // 1) % 4
                elif j == 1:
                    b2 = (b // 4) % 4
                elif j == 2:
                    b2 = (b // 16) % 4
                elif j == 3:
                    b2 = (b // 64) % 4

                x = (bb % (width // 4)) * 4 + j
                y = (bb // (width // 4)) * 4 + i

                if b2 == 0:
                    pixels[(x, y)] = c0r, c0g, c0b
                elif b2 == 1:
                    pixels[(x, y)] = c1r, c1g, c1b
                elif b2 == 2:
                    pixels[(x, y)] = c2r, c2g, c2b
                elif b2 == 3:
                    pixels[(x, y)] = c3r, c3g, c3b

    png.output_png("surface/%08X_DXT3.png" % header_id, width, height, pixels)


def image_0x35545844(header_id, width, height, data):
    pixels = {}

    lngth = width * height
    for bb in range(lngth // 16):
        o = bb * 16
        # ignore alpha for now
        blk = map(ord, data[o + 8:o + 16])

        c0 = blk[1] * 256 + blk[0]
        c1 = blk[3] * 256 + blk[2]

        c0r, c0g, c0b = rgb565(c0)
        c1r, c1g, c1b = rgb565(c1)

        c2r = (2 * c0r + 1 * c1r) // 3
        c2g = (2 * c0g + 1 * c1g) // 3
        c2b = (2 * c0b + 1 * c1b) // 3
        c3r = (1 * c0r + 2 * c1r) // 3
        c3g = (1 * c0g + 2 * c1g) // 3
        c3b = (1 * c0b + 2 * c1b) // 3

        for i in range(4):
            for j in range(4):
                b = blk[4 + i]
                if j == 0:
                    b2 = (b // 1) % 4
                elif j == 1:
                    b2 = (b // 4) % 4
                elif j == 2:
                    b2 = (b // 16) % 4
                elif j == 3:
                    b2 = (b // 64) % 4

                x = (bb % (width // 4)) * 4 + j
                y = (bb // (width // 4)) * 4 + i

                if b2 == 0:
                    pixels[(x, y)] = c0r, c0g, c0b
                elif b2 == 1:
                    pixels[(x, y)] = c1r, c1g, c1b
                elif b2 == 2:
                    pixels[(x, y)] = c2r, c2g, c2b
                elif b2 == 3:
                    pixels[(x, y)] = c3r, c3g, c3b

    png.output_png("surface/%08X_DXT5.png" % header_id, width, height, pixels)


def image_0x1C(header_id, width, height, data):
    pixels = {}
    for y in range(height):
        for x in range(width):
            o = (y * width + x)
            c = ord(data[o])
            pixels[(x, y)] = (c, c, c)
    png.output_png("surface/%08X_1C.png" % header_id, width, height, pixels)


def image_0x1F4(header_id, data):
    with open("surface/%08X.jpg" % header_id, "w") as nf:
        nf.write(data)


filename = "LOTRO/client_surface.dat"

f = DatFile(filename)


def dump_image_file(entry):
    j, unk1, file_id, offset, size1, timestamp, version, size2, unk2 = entry

    f.stream.seek(offset)
    j, k, l, m, n = struct.unpack("<LLLHH", f.stream.read(0x10))

    assert j == 0
    assert k == 0

    if m == 0xDA78:
        assert unk1 % 0x100 == 0x03
        f.stream.seek(offset)
        data = f.stream.read(size1 + 0x08)[12:]
        content = zlib.decompress(data)
        assert l == len(content)
        header_id, unk1, width, height, unk2, lngth = struct.unpack("<LLLLLL", content[:24])
        assert lngth + 24 == l
    else:
        assert unk1 % 0x100 == 0x02
        f.stream.seek(offset)
        data = f.stream.read(size1 + 0x08)[8:]
        header_id, unk1, width, height, unk2, lngth = struct.unpack("<LLLLLL", data[:24])
        assert lngth + 24 == size1
        content = data

    print hex(file_id)
    if unk2 == 0x15:
        assert width * height * 4 == lngth
        image_0x15(header_id, width, height, content[24:])
    elif unk2 == 0x14:
        assert width * height * 3 == lngth
        image_0x14(header_id, width, height, content[24:])
    elif unk2 == 0x31545844:  # DXT1
        assert width * height == lngth * 2
        image_0x31545844(header_id, width, height, content[24:])
    elif unk2 == 0x33545844:  # DXT3
        assert width * height == lngth
        image_0x33545844(header_id, width, height, content[24:])
    elif unk2 == 0x35545844:  # DXT5
        assert width * height == lngth
        image_0x35545844(header_id, width, height, content[24:])
    elif unk2 == 0x1C:
        assert width * height == lngth
        image_0x1C(header_id, width, height, content[24:])
    elif unk2 == 0x1F4:
        image_0x1F4(header_id, content[24:])
    else:
        print "%08X %04X %04X" % (l, m, n)
        print "%08s %08s %08s %08s %08s %08s" % ("file_id", "unk1", "width", "height", "unk2", "lngth")
        print "%08X %08X %08X %08X %08X %08X" % (header_id, unk1, width, height, unk2, lngth)
        dump(content[24:])


f.visit_file_entries(dump_image_file)
