#!/usr/bin/env python3

import os
import struct
import argparse

import ffutils
import DdsHeader

def rtt2dds(data: bytearray, isPermissiveMode: bool=False):
    dds_header = DdsHeader.DdsHeader()

    # Default values
    dds_header.hasAlpha    = False # TODO: why False?
    dds_header.isPitch     = False # TODO: why False?
    dds_header.hasDepth    = False # TODO: why False?
    dds_header.isComplex   = False # TODO: why False?

    # "Used in some older DDS files..."
    # Let's just ignore for now
    dds_header.hasAlphaOnly = False # TODO: why False?
    dds_header.isYUV        = False # TODO: why False?
    dds_header.isLUM        = False # TODO: why False?

    dds_header.RGBBitCount = 0
    dds_header.RBitMask    = 0
    dds_header.GBitMask    = 0
    dds_header.BBitMask    = 0
    dds_header.ABitMask    = 0

    # Magic
    if data[0x0] != 0x80:
        msg = 'Expecting 0x80 at pos 0x00'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)

    # File size (+4 since points to start of last DWORD)
    filesize = (struct.unpack(">I", data[:0x4])[0] & 0x00FFFFFF) + 4
    if len(data) != filesize:
        msg = 'Filesize does not match header'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)

    # Find compression method
    if data[0x4] == 0x01 or data[0x4] == 0x05: # No compression
        dds_header.fourCC = struct.pack("<I", 0)
    elif data[0x4] == 0x06:
        dds_header.fourCC = b'DXT1'
    elif data[0x4] == 0x07:
        dds_header.fourCC = b'DXT3'
    elif data[0x4] == 0x08:
        dds_header.fourCC = b'DXT5'
    else:
        msg = 'Unknown compression method'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)

    if data[0x5] != 0x0:
        msg = 'Expecting 0x00 at pos 0x05'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)

    # Get image format
    img_fmt = struct.unpack(">H", data[0x6:0x8])[0]
    if img_fmt == 0xAAE4:
        pass # Already set above
    elif img_fmt == 0xA9FF:
        # Boundary Mask
        dds_header.hasAlpha     = True
        dds_header.hasAlphaOnly = True
        dds_header.RGBBitCount  = 8
        dds_header.ABitMask     = 0xFF
    elif img_fmt == 0xAA1B:
        dds_header.hasAlpha    = True
        dds_header.RGBBitCount = 32
        dds_header.ABitMask    = 0xFF000000
        dds_header.RBitMask    = 0x00FF0000
        dds_header.BBitMask    = 0x0000FF00
        dds_header.GBitMask    = 0x000000FF
        msg = 'Image format (0xAA1B) not yet reversed'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)
    else:
        msg = 'Unknown image format'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)

    # Get resolution
    dds_header.width = struct.unpack(">H", data[0x8:0xa])[0]
    dds_header.height = struct.unpack(">H", data[0xa:0xc])[0]

    if data[0xc] != 0x0:
        msg = 'Expecting 0x0 at pos 0x0C'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)

    # Not sure what this data is but I'm using it to block formats not reversed
    if data[0xd] == 0x1 and data[0xf] == 0x2:
        pass
    else:
        # Files that reach here are the defaultfog files (but not the
        # aqua ones)
        msg = 'Image format not yet reversed (defaultfog)'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)

    dds_header.num_mipmaps = data[0xe]
    if dds_header.fourCC == b'DXT1':
        bits_per_group = 64
        pixels_per_group = 16
        bytes_per_group = bits_per_group / 8.0
        bytes_per_pixel = bytes_per_group / (1.0 * pixels_per_group)
    elif dds_header.fourCC == b'DXT3' or dds_header.fourCC == b'DXT5':
        bits_per_group = 128
        pixels_per_group = 16
        bytes_per_group = bits_per_group / 8.0
        bytes_per_pixel = bytes_per_group / (1.0 * pixels_per_group)
    else:
        bytes_per_pixel = dds_header.RGBBitCount / 8.0
        bytes_per_group = dds_header.RGBBitCount / 8.0
    if len(data) - 0x80 != ffutils.get_img_data_size(dds_header.width,
            dds_header.height, dds_header.num_mipmaps, bytes_per_pixel,
            bytes_per_group):
        msg = 'Mipmap number to filesize mismatch'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)

    dds_header_bytes = dds_header.create()
    for i in range(0, len(dds_header_bytes)):
        data[i] = dds_header_bytes[i]

    return data

def main():
    parser = argparse.ArgumentParser(
            description="Convert .rtt files to .dds files")
    parser.add_argument("--permissive", action="store_true", help="run in permissve mode (don't throw on unexpected values)")
    parser.add_argument("filepath", nargs="+", help="path to .rtt file")
    args = parser.parse_args()
    if args.permissive:
        print("Running in permissive mode")

    for filepath in args.filepath:
        print("Processing " + filepath, end="")
        try:
            with open(filepath, 'rb') as f:
                rttdata = bytearray(f.read())
            ddsdata = rtt2dds(rttdata, args.permissive)
            out_filename = '.'.join(os.path.basename(filepath).split('.')[:-1]) + '.dds'
            with open(os.path.join(os.path.dirname(filepath), out_filename), 'wb') as f:
                f.write(ddsdata)
            print(" - Done")
        except ValueError as err:
            print(' - ValueError: {}'.format(err))

if __name__ == '__main__':
    main()
