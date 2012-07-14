#!/usr/bin/env python

import sys
import time

from dat import DatFile


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
        print "%02X : %08X %08X" % (i, block_size, dir_offset)
    for i, unk1, unk2, file_id, offset, size1, timestamp, version, size2 in d.file_ptrs:
        print "%02X : %08X %08X %08X %s %08X | %08X %08X %08X | %08X |" % (i, file_id, offset, size1, time.ctime(timestamp), version, size2, unk1, unk2, size2 - size1)


## mainline

def show_usage(argv0):
    print("%s header <filename>" % argv0)
    print("%s directory <filename>" % argv0)

if len(sys.argv) < 3:
    show_usage(sys.argv[0])
else:
    command = sys.argv[1]
    if command == "header":
        filename = sys.argv[2]
        show_header(filename)
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
    else:
        show_usage(sys.argv[0])
