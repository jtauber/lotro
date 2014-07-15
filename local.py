#!/usr/bin/env python

import struct
import time
import zlib

from dat import DatFile
import png
from utils import dump


filename = "LOTRO/client_local_English.dat"

f = DatFile(filename)


def image_0x15(header_id, width, height, data):
    pixels = {}
    apixels = {}
    for y in range(height):
        for x in range(width):
            o = (y * width + x) * 4
            c1, c2, c3, c4 = map(ord, data[o:o + 4])
            pixels[(x, y)] = (c3, c2, c1)
            apixels[(x, y)] = (c4, c4, c4)
    png.output_png("local/%08X_015.png" % header_id, width, height, pixels)
    png.output_png("local/%08X_015_a.png" % header_id, width, height, apixels)


def image_0x1F4(header_id, data):
    with open("local/%08X.jpg" % header_id, "w") as nf:
        nf.write(data)


def dump_local_file(entry):
    j, unk1, file_id, offset, size1, timestamp, version, size2, unk2 = entry

    # print "%08X %08X %08X %s %08X | %08X %08X %08X | %08X" % (file_id, offset, size1, time.ctime(timestamp), version, size2, unk1, unk2, size2 - size1)

    f.stream.seek(offset)

    j, k, l, m, n = struct.unpack("<LLLHH", f.stream.read(0x10))
    # print "%08X %08X %08X %04X %04X" % (j, k, l, m, n)

    assert k == 0

    if j == 0:
        if m == 0xDA78:
            # print "compressed"
            assert unk1 % 0x100 == 0x03
            f.stream.seek(offset)
            data = f.stream.read(size1 + 0x08)[12:]
            content = zlib.decompress(data)
            assert l == len(content)
        else:
            # print "uncompressed"
            assert unk1 % 0x100 == 0x02
            f.stream.seek(offset)
            data = f.stream.read(size1 + 0x08)[8:]
            content = data

        # print "%08X %08X" % struct.unpack("<LL", content[:8]),
        magic = content[8:12]
        if magic == "OggS":
            pass  # print "OGG"
        else:
            # print "%08X %08X %08X %08X %08X" % struct.unpack("<LLLLL", content[:20])
            if len(content) > 24:
                header_id, unk1, width, height, unk2, lngth = struct.unpack("<LLLLLL", data[:24])
                if unk2 == 0x1F4:
                    print "%08X" % file_id
                    # image_0x1F4(file_id, content[24:])
                elif unk2 == 0x15:
                    print "%08X %08X %08X %08X %08X %08X" % struct.unpack("<LLLLLL", content[:24])
                    assert width * height * 4 == lngth
                    image_0x15(header_id, width, height, content[24:])

    else:
        pass

f.visit_file_entries(dump_local_file)
