#!/usr/bin/env python

import math
import struct
import time
import zlib

from dat import DatFile
import png
from utils import dump


filename = "LOTRO/client_cell_2.dat"

f = DatFile(filename)


def dump_cell_file(entry):
    j, unk1, file_id, offset, size1, timestamp, version, size2, unk2 = entry

    if 0x27010000 <= file_id <= 0x2701FFFF or 0x27020000 <= file_id <= 0x2702FFFF:
        pass
    elif 0x80210000 <= file_id <= 0x8021FFFF or 0x80220000 <= file_id <= 0x8022FFFF:
        pass
    elif 0x80410000 <= file_id <= 0x8041FFFF or 0x80420000 <= file_id <= 0x8042FFFF:
        pass
    elif 0x80510000 <= file_id <= 0x8051FFFF or 0x80520000 <= file_id <= 0x8052FFFF:
        pass
    elif 0x80010000 <= file_id <= 0x8001FFFF or 0x80020000 <= file_id <= 0x8002FFFF:
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
            
            header_id, unk1, unk2, unk3 = struct.unpack("<LLLL", content[:0x10])
            print "%08X %08X %08X %08X" % (header_id, unk1, unk2, unk3)
            assert header_id == file_id
            if unk1 != 0:
                assert unk1 == 0x00200000 + header_id
            assert unk2 == 0x00000000
            assert unk3 == 0x00000441
            
            if len(content) == 0x1168:
                data = content[0x10:0x10 + (0x441 * 2)]
                pixels = {}
                for y in range(32):
                    for x in range(32):
                        o = (y * (33) + x) * 2
                        h = struct.unpack("<H", data[o:o + 2])[0]
                        c = int(math.log(((16 * h) % 65535) + 1, 1.045))
                        pixels[(y, 32 - x - 1)] = (c, c, c)
                png.output_png("cells/%08X.png" % file_id, 32, 32, pixels)
            else:
                # @@@ just grab the first 0x441 * 2 anyway
                data = content[0x10:0x10 + (0x441 * 2)]
                pixels = {}
                for y in range(32):
                    for x in range(32):
                        o = (y * (33) + x) * 2
                        h = struct.unpack("<H", data[o:o + 2])[0]
                        c = int(math.log(((16 * h) % 65535) + 1, 1.045))
                        pixels[(y, 32 - x - 1)] = (c, c, c)
                png.output_png("cells/%08X.png" % file_id, 32, 32, pixels)
        else:
            if m == 0xDA78:
                # print "compressed"
                assert unk1 % 0x100 == 0x03
                f.stream.seek(offset)
                data = f.stream.read(size1 + 0x08)[12:]
                try:
                    content = zlib.decompress(data)
                except zlib.error:
                    return
                # assert l == len(content)
            else:
                # print "uncompressed"
                assert unk1 % 0x100 == 0x02
                f.stream.seek(offset)
                data = f.stream.read(size1 + 0x08)[8:]
                content = data
            
            header_id, unk1, unk2, unk3 = struct.unpack("<LLLL", content[:0x10])
            print "%08X %08X %08X %08X" % (header_id, unk1, unk2, unk3)
            assert header_id == file_id
            if unk1 != 0:
                assert unk1 == 0x00200000 + header_id
            assert unk2 == 0x00000000
            assert unk3 == 0x00000441

            # @@@ just grab the first 0x441 * 2 anyway
            data = content[0x10:0x10 + (0x441 * 2)]
            if len(data) < 0x441 * 2:
                return
            pixels = {}
            for y in range(32):
                for x in range(32):
                    o = (y * (33) + x) * 2
                    h = struct.unpack("<H", data[o:o + 2])[0]
                    c = int(math.log(((16 * h) % 65535) + 1, 1.045))
                    pixels[(y, 32 - x - 1)] = (c, c, c)
            png.output_png("cells/%08X.png" % file_id, 32, 32, pixels)
    else:
        print "%08X" % file_id


f.visit_file_entries(dump_cell_file)
