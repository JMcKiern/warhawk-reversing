#!/usr/bin/env python3

import os
import sys
import struct

import ffutils
import DdsHeader

def findZeroesAfter(data, start):
    for i in range(start, len(data), 0x10):
        if (data[i:i+0x10] == b'\x00' * 0x10):
            return i

def parseSingleHeader(rttmod_header, ngp_data, vram_data, num):
    print("Parsing: " + str(rttmod_header))
    if (len(rttmod_header) != 0x10):
        raise ValueError('rttmod_header should be size 0x10')
    loc, = struct.unpack(">I", rttmod_header[0xc:])

    if rttmod_header[0x0] == 0x01 or rttmod_header[0x0] == 0x05: # No compression
        fourCC = struct.pack("<I", 0)
    elif rttmod_header[0x0] == 0x06:
        fourCC = b'DXT1'
    elif rttmod_header[0x0] == 0x07:
        fourCC = b'DXT3'
    elif rttmod_header[0x0] == 0x08:
        fourCC = b'DXT5'
    else:
        raise ValueError('Unknown compression method')

    width = (rttmod_header[0x4] << 8) + rttmod_header[0x5]
    height = (rttmod_header[0x6] << 8) + rttmod_header[0x7]
    num_mipmaps = rttmod_header[0xa]
    if fourCC == b'DXT1':
        bits_per_group = 64
        pixels_per_group = 16
        bytes_per_group = bits_per_group / 8.0
        bytes_per_pixel = bytes_per_group / (1.0 * pixels_per_group)
    elif fourCC == b'DXT3' or fourCC == b'DXT5':
        bits_per_group = 128
        pixels_per_group = 16
        bytes_per_group = bits_per_group / 8.0
        bytes_per_pixel = bytes_per_group / (1.0 * pixels_per_group)
    else:
        bytes_per_pixel = RGBBitCount / 8.0
        bytes_per_group = RGBBitCount / 8.0
    img_data_size = ffutils.get_img_data_size(width, height, num_mipmaps, bytes_per_pixel, bytes_per_group)

    isInNGP = rttmod_header[0x8] == 0x1
    rttmod_header[0x8] = 0x0 # Setting it to 0 to get through rtt2dds. Could change it there but idk

    if (isInNGP):
        print("Reading from NGP")
        texture_data = ngp_data[loc:loc+img_data_size]
    else:
        print("Reading from VRAM")
        texture_data = vram_data[loc:loc+img_data_size]

    size = 0x80 + img_data_size
    rttHeader = b'\x80' + struct.pack(">I", size - 4)[1:] + rttmod_header[:0xc] + ((b'\x00' * 0x10) * 7)

    with open(hex(num) + ".rtt", 'wb') as f:
        f.write(rttHeader + texture_data)

def main():
    start_header = int(sys.argv[1], 16)
    end_header = int(sys.argv[2], 16)
    filename = sys.argv[3]
    print(hex(start_header) + " " + hex(end_header) + " " + filename)
    with open(filename + '.ngp', 'rb') as f:
        ngp_data = bytearray(f.read())
    with open(filename + '.vram', 'rb') as f:
        vram_data = bytearray(f.read())
    for i in range(start_header, end_header, 0x10):
        if (ngp_data[i:i+0x10] != b'\x00' * 0x10):
            parseSingleHeader(ngp_data[i:i+0x10], ngp_data, vram_data, i)

if __name__ == '__main__':
    main()
