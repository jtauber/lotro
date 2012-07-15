#!/usr/bin/env python

import struct
import sys
import time

from dat import DatFile
from utils import dump


## header

def show_header(filename):
    f = DatFile(filename)
    print("File Header Information:")
    print("  Version: %08X %08X" % (f.version, f.version_2))
    print("  Block Size: %08X bytes" % f.block_size)
    print("  File Size: %08X bytes" % f.file_size)
    print("  Root Directory Block: %08X" % f.directory_offset)
    print("  Free Block Chain Head: %08X" % f.free_head)
    print("  Free Blocks: %08X blocks" % f.free_size)


## block

def show_block(filename, offset):
    f = DatFile(filename)
    f.stream.seek(offset)
    block_data = f.stream.read(f.block_size)
    dump(block_data)
    print "---"
    dump(f.stream.read(0x40))


## file_block

def show_file_block(filename, offset):
    f = DatFile(filename)
    f.stream.seek(offset)
    block_data = f.stream.read(f.block_size)
    zero1, zero2, file_id, size = struct.unpack("<LLLL", block_data[:0x10])
    assert zero1 == 0
    assert zero2 == 0
    print("%08X %08X" % (file_id, size))
    file_data = f.stream.read(size)
    dump(file_data[0x10:])


## directory

def show_directory(filename, offset=None):
    """
    show the directory at the given offset
    or the root directory if no offset given
    """
    f = DatFile(filename)
    if offset is None:
        offset = f.directory_offset
    
    d = f.directory(offset)
    
    for i, block_size, dir_offset in d.subdir_ptrs:
        print "         %08X" % dir_offset
        if i < d.count:
            j, unk1, file_id, offset, size1, timestamp, version, size2, unk2 = d.file_ptrs[i]
            print "%08X %08X %08X %s %08X | %08X %08X %08X | %08X" % (file_id, offset, size1, time.ctime(timestamp), version, size2, unk1, unk2, size2 - size1)


## list

def show_list(filename):
    """
    list all the files in the DAT
    """
    f = DatFile(filename)
    go_list(f, f.directory_offset)


def go_list(f, offset):
    d = f.directory(offset)

    for i, block_size, dir_offset in d.subdir_ptrs:
        go_list(f, dir_offset)
        if i < d.count:
            j, unk1, file_id, offset, size1, timestamp, version, size2, unk2 = d.file_ptrs[i]
            print "%08X %08X %08X %s %08X | %08X %08X %08X | %08X" % (file_id, offset, size1, time.ctime(timestamp), version, size2, unk1, unk2, size2 - size1)


## mainline

def show_usage(argv0):
    print("%s header <filename>" % argv0)
    print("%s block <filename> <hex-offset>" % argv0)
    print("%s file_block <filename> <hex-offset>" % argv0)
    print("%s directory <filename>" % argv0)
    print("%s directory <filename> <hex-offset>" % argv0)
    print("%s list <filename>" % argv0)

if len(sys.argv) < 3:
    show_usage(sys.argv[0])
else:
    command = sys.argv[1]
    if command == "header":
        filename = sys.argv[2]
        show_header(filename)
    elif command == "block":
        filename = sys.argv[2]
        offset = int(sys.argv[3], 16)
        show_block(filename, offset)
    elif command == "file_block":
        filename = sys.argv[2]
        offset = int(sys.argv[3], 16)
        show_file_block(filename, offset)
    elif command == "directory":
        if len(sys.argv) == 3:
            filename = sys.argv[2]
            show_directory(filename)
        elif len(sys.argv) == 4:
            filename = sys.argv[2]
            offset = int(sys.argv[3], 16)
            show_directory(filename, offset)
        else:
            show_usage()
    elif command == "list":
        filename = sys.argv[2]
        show_list(filename)
    else:
        show_usage(sys.argv[0])
