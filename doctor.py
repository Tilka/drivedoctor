#!/usr/bin/env python3

# Copyright 2025 Tillmann Karras
# SPDX-License-Identifier: GPL-3.0-or-later

import usb.core
from struct import pack
from progressbar import ProgressBar

class DriveDoctor:
    def __init__(self):
        self.dev = usb.core.find(idVendor=0x05fd, idProduct=0x1290)
        self.dev.set_configuration()

    def write_byte(self, addr, byte):
        req = pack('<6I', 0x87654321, 0x3E8, addr, byte, 1, 0)
        self.dev.write(endpoint=0x0E, data=req)

    def write_word(self, addr, word):
        req = pack('<6I', 0x87654321, 0x3E8, addr, word, 2, 0)
        self.dev.write(endpoint=0x0E, data=req)

    def read(self, addr, size):
        while size:
            chunk_size = min(4096, size)
            req = pack('<6I', 0x87654321, 0x3E9, addr, chunk_size, 0, 0)
            addr += chunk_size
            size -= chunk_size
            self.dev.write(endpoint=0x0E, data=req)
            yield bytes(self.dev.read(endpoint=0x8F, size_or_buffer=chunk_size, timeout=3000))

    def dump(self, path, addr, size):
        f = open(path, 'wb+')
        progress = ProgressBar(max_value=size).start()
        for chunk in self.read(addr, size):
            f.write(chunk)
            progress.increment(len(chunk))
        progress.finish()

    def dump_rom(self, path):
        # This takes about a minute.
        self.dump(path, addr=0x80000, size=0x20000)

if __name__ == '__main__':
    dr = DriveDoctor()
    dr.dump_rom('/tmp/wii_disc_drive.bin')
