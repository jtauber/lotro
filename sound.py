#!/usr/bin/env python

import struct
import time

from dat import DatFile


filename = "LOTRO/client_sound.dat"

f = DatFile(filename)


def dump_sound_file(entry):
    j, unk1, file_id, offset, size1, timestamp, version, size2, unk2 = entry
    f.stream.seek(offset)
    j, k, l, m = struct.unpack("<LLLL", f.stream.read(0x10))

    if j == 0 and k == 0 and l == file_id and m == size1 - 0x10:
        magic = f.stream.read(0x04)
        print "%08X %08X %08X %s %08X | %08X %08X %08X | %08X |" % (file_id, offset, size1, time.ctime(timestamp), version, size2, unk1, unk2, size2 - size1),
        print "%08X %08X" % (l, m),
        print magic

        f.stream.seek(offset + 0x10)
        data = f.stream.read(m + 0x08)

        if magic == "RIFF":
            with open("sound/%08X.wav" % file_id, "w") as sound_file:
                sound_file.write(data)
        elif magic == "OggS":
            with open("sound/%08X.ogg" % file_id, "w") as sound_file:
                sound_file.write(data)


f.visit_file_entries(dump_sound_file)
