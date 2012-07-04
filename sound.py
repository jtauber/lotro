#!/usr/bin/env python

import os.path
import struct
import sys
import time


def assert_zero(s):
    assert s == "\0" * len(s)


def printable(byte):
    if 0x20 <= ord(byte) < 0x7F:
        return True
    else:
        return False


def dump(bytes, cols=16, unprintable=".", print_all=False):
    
    rows, last_row = divmod(len(bytes), cols)
    
    for row in range(rows + 1):
        for i in range(last_row if row == rows else cols):
            byte = bytes[cols * row + i]
            sys.stdout.write("%02X " % ord(byte))
        if row == rows:
            sys.stdout.write("   " * (cols - last_row))
        for i in range(last_row if row == rows else cols):
            byte = bytes[cols * row + i]
            if print_all:
                sys.stdout.write(chr(0x20 + ((ord(byte) - 0x20) % 0x5F)))
            else:
                if printable(byte):
                    sys.stdout.write(byte)
                else:
                    sys.stdout.write(unprintable)
        sys.stdout.write("\n")


filename = "LOTRO/client_sound.dat"

file_size = os.path.getsize(filename)
with open(filename) as f:
    header = f.read(0x200)
    
    assert_zero(header[0x000:0x100])
    assert header[0x100:0x104] == "\x00\x50\x4C\x00"
    assert_zero(header[0x104:0x140])
    assert header[0x140:0x144] == "\x42\x54\x00\x00"
    a, size, c, part, e, zero, g, h = struct.unpack("<LLLLLLLL", header[0x144:0x164])
    # print "%30s %08X - %08X - %08X - %08X %08X" % (filename, a, c, e, g, h)
    
    assert file_size == size
    assert part in [0, 1, 2] # 1 or 2 if a two-parter otherwise 0 (local_English is 2)
    assert zero == 0
    
    assert_zero(header[0x164:0x170])
    # @@@
    assert_zero(header[0x1A8:0x1FF])
    
    def tree(start, indent=0):
        f.seek(start)
        row = f.read(0x08)
        assert_zero(row)
        for i in range(0x3E):
            f.seek(start + 0x08 + (0x08 * i))
            row = f.read(0x08)
            if row == "\0" * 0x08:
                break
            x, y = struct.unpack("<LL", row)
            # print "  " * indent + "%08X %08X" % (x, y)
            assert x == a
            tree(y, indent + 1)
        for i in range(0x3B):
            f.seek(start + 0x08 + (0x08 * 0x3E) + (0x20 * i))
            # version is of dat file (or game) not individual file
            unk1, unk2, file_id, offset, size1, timestamp, version, size2 = struct.unpack("<LLLLLLLL", f.read(0x20))
            if 0 < file_id < 0xFFFF0000:
                print "%08X %08X %08X %s %08X | %08X %08X %08X | %08X |" % (file_id, offset, size1, time.ctime(timestamp), version, size2, unk1, unk2, size2 - size1),
                f.seek(offset)
                j, k, l, m = struct.unpack("<LLLL", f.read(0x10))
                assert j == 0
                assert k == 0 
                print "%08X %08X" % (l, m),
                assert l == file_id
                assert m == size1 - 0x10
                magic = f.read(0x04)
                print magic
                f.seek(offset + 0x10)
                data = f.read(m + 0x08)
                if magic == "RIFF":
                    with open("sound/%08X.wav" % file_id, "w") as sound_file:
                        sound_file.write(data)
                elif magic == "OggS":
                    with open("sound/%08X.ogg" % file_id, "w") as sound_file:
                        sound_file.write(data)
    tree(h)
