#!/usr/bin/env python

import sys

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


##

def show_usage(argv0):
    print("%s header <filename>" % argv0)

if len(sys.argv) < 3:
    show_usage(sys.argv[0])
else:
    command = sys.argv[1]
    if command == "header":
        filename = sys.argv[2]
        show_header(filename)
    else:
        show_usage(sys.argv[0])
