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
    
    def find_file(self, target_id, directory_offset=None):
        d = self.directory(directory_offset)
        l = 0
        u = d.count - 1
        while l <= u:
            p = (l + u) / 2
            entry = d.file_ptrs[p]
            if entry[2] < target_id:
                l = p + 1
            elif entry[2] > target_id:
                u = p - 1
            else:  # found file
                return d.file_ptrs[p]
        subdir_offset = d.subdir_ptrs[l][2]
        return self.find_file(target_id, subdir_offset)
    
    def visit_file_entries(self, visitor, offset=None):
        d = self.directory(offset)
        if d.subdir_ptrs:
            for i, block_size, dir_offset in d.subdir_ptrs:
                self.visit_file_entries(visitor, dir_offset)
                if i < d.count:
                    visitor(d.file_ptrs[i])
        else:  # leaf
            for file_entry in d.file_ptrs:
                visitor(file_entry)


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
        
        f.seek(offset + 0x08)
        for i in range(62):
            row = f.read(0x08)
            block_size, dir_offset = struct.unpack("<LL", row)
            if block_size == 0:
                break
            # assert block_size == self.dat_file.block_size
            self.subdir_ptrs.append((i, block_size, dir_offset))
        
        f.seek(offset + (0x08 * 63))
        self.count = struct.unpack("<L", f.read(4))[0]
        self.subdir_ptrs = self.subdir_ptrs[:self.count + 1]
        
        # files
        
        for i in range(self.count):
            d = f.read(0x20)
            unk1, file_id, file_offset, size1, timestamp, version, size2, unk2 = \
                struct.unpack("<LLLLLLLL", d)
            if size1 > 0:
                self.file_ptrs.append((i, unk1, file_id, file_offset, size1, timestamp, version, size2, unk2))
