#!/usr/bin/env python

import os.path

from utils import dword


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
