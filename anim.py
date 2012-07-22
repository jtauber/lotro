#!/usr/bin/env python

import struct
import time
import zlib

from dat import DatFile
from utils import dump


filename = "LOTRO/client_anim.dat"

f = DatFile(filename)


def dump_anim_file(entry):
    j, unk1, file_id, offset, size1, timestamp, version, size2, unk2 = entry
    print "%08X %08X %08X %s %08X | %08X %08X %08X | %08X" % (file_id, offset, size1, time.ctime(timestamp), version, size2, unk1, unk2, size2 - size1)
    
    f.stream.seek(offset)
    
    j, k, l, m, n = struct.unpack("<LLLHH", f.stream.read(0x10))
    print "%08X %08X %08X %04X %04X" % (j, k, l, m, n)
    
    assert j == 0
    assert k == 0
    
    if m == 0xDA78:
        f.stream.seek(offset)
        data = f.stream.read(size1 + 0x08)[12:]
        content = zlib.decompress(data)
        assert l == len(content)
        print "compressed"
    else:
        print "uncompressed"
        f.stream.seek(offset)
        data = f.stream.read(size1 + 0x08)[8:]
        content = data
    
    dump(content[:0x100])


f.visit_file_entries(dump_anim_file)
