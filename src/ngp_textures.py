#!/usr/bin/env python3

import os
import sys
import struct

import ffutils
import DdsHeader

def parseNGPTextureHeader(rttmod_header, ngp_data, vram_data):
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
    return bytearray(rttHeader + texture_data)

def dereferenceRelativePointer(data, locOfPointer):
    relativeOffset, = struct.unpack(">i", data[locOfPointer:locOfPointer+4])
    offset = locOfPointer + relativeOffset
    return offset

def main():
    filename = sys.argv[1]

    with open(filename, 'rb') as f:
        ngp_data = bytearray(f.read())
    vram_filename = '.'.join(filename.split(".")[:-1]) + ".vram"
    with open(vram_filename, 'rb') as f:
        vram_data = bytearray(f.read())

    texturePointersOffset = dereferenceRelativePointer(ngp_data, 0x10)
    numberOfTextures, = struct.unpack(">I", ngp_data[texturePointersOffset:texturePointersOffset+4])
    print("There are " + str(numberOfTextures) + " textures")
    for i in range(texturePointersOffset+4, texturePointersOffset+((numberOfTextures+1)*4), 4):
        textureHeaderOffset = dereferenceRelativePointer(ngp_data, i)
        header = ngp_data[textureHeaderOffset:textureHeaderOffset+0x10]
        print("Parsing: " + str([hex(j) for j in header]))
        rttdata = parseNGPTextureHeader(header, ngp_data, vram_data)
        with open(hex(i) + ".rtt", 'wb') as f:
            f.write(rttdata)

if __name__ == '__main__':
    main()
