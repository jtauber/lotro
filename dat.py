#!/usr/bin/env python

import os.path
import struct

from utils import dword, zeros


class DatFile:
    def __init__(self, filename):
        self.filename = filename
        self.file_size = os.stat(filename).st_size
        self.stream = open(filename, "rb")
        self.block_cache = {}
        self.dir_cache = {}
        buf = self.stream.read(1024)
        self.read_super_block(buf)
    
    def read_super_block(self, buf):
        assert dword(buf, 0x101) == 0x4C50
        assert dword(buf, 0x140) == 0x5442
        
        self.block_size = dword(buf, 0x144)
        self.size = dword(buf, 0x148)
        self.version = dword(buf, 0x14C)
        self.version_2 = dword(buf, 0x150)
        self.free_head = dword(buf, 0x154)
        self.free_tail = dword(buf, 0x158)
        self.free_size = dword(buf, 0x15C)
        self.directory_offset = dword(buf, 0x160)
        
        assert self.file_size == self.size

    def directory(self, offset=None):
        if offset is None:
            offset = self.directory_offset
        if offset in self.dir_cache:
            return self.dir_cache[offset]
        d = Directory(self, offset)
        self.dir_cache[offset] = d
        return d


class Directory:
    def __init__(self, dat_file, offset):
        self.dat_file = dat_file
        self.offset = offset
        
        self.subdir_ptrs = []
        self.file_ptrs = []
        
        f = self.dat_file.stream
        f.seek(offset)
        row = f.read(0x08)
        assert zeros(row)
        
        # sub-directories
        
        for i in range(62):
            f.seek(offset + 0x08 + (0x08 * i))
            row = f.read(0x08)
            if zeros(row):
                break
            block_size, dir_offset = struct.unpack("<LL", row)
            assert block_size == self.dat_file.block_size
            self.subdir_ptrs.append((i, block_size, dir_offset))
        
        self.count = struct.unpack("<L", f.read(4))[0]
        
        # files
        
        for i in range(61):
            f.seek(offset + 0x04 + (0x08 * 63) + (0x20 * i))
            d = f.read(0x20)
            unk1, file_id, file_offset, size1, timestamp, version, size2, unk2 = \
                struct.unpack("<LLLLLLLL", d)
            if size1 > 0:
                self.file_ptrs.append((i, unk1, file_id, file_offset, size1, timestamp, version, size2, unk2))
