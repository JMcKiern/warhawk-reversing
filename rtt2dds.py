#!/usr/bin/env python3

import os
import sys

import ffutils
import dds_header

def rtt2dds(filepath):
    with open(filepath, 'rb') as f:
        data = bytearray(f.read())

    # Default values
    hasAlpha    = False # TODO: why False?
    isPitch     = False # TODO: why False?
    isMipmapped = False # TODO: why False?
    hasDepth    = False # TODO: why False?
    isComplex   = False # TODO: why False?

    # "Used in some older DDS files..."
    # Let's just ignore for now
    hasAlphaOnly = False # TODO: why False?
    isYUV        = False # TODO: why False?
    isLUM        = False # TODO: why False?

    RGBBitCount = 0
    RBitMask = 0
    GBitMask = 0
    BBitMask = 0
    ABitMask = 0

    # Magic
    if data[0x0] != 0x80:
        raise ValueError('Expecting 0x80 at pos 0x00')

    # File size (+4 since points to start of last DWORD)
    filesize = (data[0x1] << 16) + (data[0x2] << 8) + (data[0x3]) + 4
    if len(data) != filesize:
        raise ValueError('Filesize does not match header')

    # Find compression method
    if data[0x4] == 0x01 or data[0x4] == 0x05: # No compression
        fourCC = ffutils.int32_to_bytes(0)
    elif data[0x4] == 0x06:
        fourCC = b'DXT1'
    elif data[0x4] == 0x07:
        fourCC = b'DXT3'
    elif data[0x4] == 0x08:
        fourCC = b'DXT5'
    else:
        raise ValueError('Unknown compression method')

    if data[0x5] != 0x0:
        raise ValueError('Expecting 0x00 at pos 0x05')

    # Get image format
    img_fmt = (data[0x6] << 8) + data[0x7]
    if img_fmt == 0xAAE4:
        pass # Already set above
    elif img_fmt == 0xA9FF:
        # Boundary Mask
        hasAlpha = True
        hasAlphaOnly = True
        RGBBitCount = 8
        ABitMask    = 0xFF
    elif img_fmt == 0xAA1B:
        raise ValueError('Image format not yet reversed')
    else:
        raise ValueError('Unknown image format')

    # Get resolution
    width = (data[0x8] << 8) + data[0x9]
    height = (data[0xa] << 8) + data[0xb]

    # Not sure what this data is but I'm using it to block formats not reversed
    if data[0xd] == 0x1 and data[0xf] == 0x2:
        pass
    else:
        # Files that reach here are the defaultfog files (but not the
        # aqua ones)
        raise ValueError('Image format not yet reversed (defaultfog)')

    num_mipmaps = data[0xe]
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
    if len(data) - 0x80 != ffutils.get_img_data_size(width, height, num_mipmaps, bytes_per_pixel, bytes_per_group):
        raise ValueError('Mipmap number to filesize mismatch')

    DDS_header = dds_header.create_DDS_header(fourCC, width, height,
            num_mipmaps, hasAlpha, isPitch, isMipmapped, hasDepth, isComplex,
            hasAlphaOnly, isYUV, isLUM, RGBBitCount, RBitMask, GBitMask,
            BBitMask, ABitMask)
    for i in range(0, len(DDS_header)):
        data[i] = DDS_header[i]

    out_filename = '.'.join(os.path.basename(filepath).split('.')[:-1]) + '.dds'
    with open(os.path.join(os.path.dirname(filepath), out_filename), 'wb') as f:
        f.write(data)

def main():
    for arg in sys.argv[1:]:
        print("Processing " + arg)
        try:
            rtt2dds(arg)
        except ValueError as err:
            print('ValueError: {}'.format(err))

if __name__ == '__main__':
    main()
