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

def print_entry(entry):
    j, unk1, file_id, offset, size1, timestamp, version, size2, unk2 = entry
    print "%08X %08X %08X %s %08X | %08X %08X %08X | %08X" % (file_id, offset, size1, time.ctime(timestamp), version, size2, unk1, unk2, size2 - size1)


def show_directory(filename, offset=None):
    """
    show the directory at the given offset
    or the root directory if no offset given
    """
    f = DatFile(filename)
    d = f.directory()

    if d.subdir_ptrs:
        for i, block_size, dir_offset in d.subdir_ptrs:
            print "         %08X" % dir_offset
            if i < d.count:
                print_entry(d.file_ptrs[i])
    else:  # leaf
        for entry in d.file_ptrs:
            print_entry(entry)


## list

def show_list(filename):
    """
    list all the files in the DAT
    """
    f = DatFile(filename)
    f.visit_file_entries(print_entry)


## fine_file

def show_find_file(filename, file_id):
    """
    find the directory entry for the file with the given id
    """
    f = DatFile(filename)
    print_entry(f.find_file(file_id))


## mainline

def show_usage(argv0):
    print("%s header <filename>" % argv0)
    print("%s block <filename> <hex-offset>" % argv0)
    print("%s file_block <filename> <hex-offset>" % argv0)
    print("%s directory <filename>" % argv0)
    print("%s directory <filename> <hex-offset>" % argv0)
    print("%s list <filename>" % argv0)
    print("%s find_file <filename> <file-id>" % argv0)

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
    elif command == "find_file":
        filename = sys.argv[2]
        file_id = int(sys.argv[3], 16)
        show_find_file(filename, file_id)
    else:
        show_usage(sys.argv[0])
