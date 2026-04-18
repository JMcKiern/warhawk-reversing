#!/usr/bin/env python3

import os
import struct
import argparse

import ffutils
import DdsHeader

def _deinterleave_bits(n):
    n &= 0x55555555
    n = (n | (n >> 1)) & 0x33333333
    n = (n | (n >> 2)) & 0x0f0f0f0f
    n = (n | (n >> 4)) & 0x00ff00ff
    n = (n | (n >> 8)) & 0x0000ffff
    return n

def _deswizzle_mip(data, width, height):
    """Convert Morton-order (swizzled) pixel data to linear raster order."""
    out = bytearray(width * height * 4)
    for i in range(width * height):
        px = _deinterleave_bits(i)
        py = _deinterleave_bits(i >> 1)
        src = i * 4
        dst = (py * width + px) * 4
        out[dst:dst+4] = data[src:src+4]
    return out

def _deswizzle_and_flip(pixel_data, width, height, num_mipmaps, depth=1):
    """Deswizzle and vertically flip all mipmap levels.

    For volume textures (depth > 1), each mip level is stored as depth sequential
    2D-swizzled slices.
    """
    result = bytearray()
    offset = 0
    for mip in range(num_mipmaps):
        mip_w = max(1, width >> mip)
        mip_h = max(1, height >> mip)
        mip_d = max(1, depth >> mip)
        for _ in range(mip_d):
            size = mip_w * mip_h * 4
            mip_data = pixel_data[offset:offset+size]
            deswizzled = _deswizzle_mip(mip_data, mip_w, mip_h)
            rows = [deswizzled[r*mip_w*4:(r+1)*mip_w*4] for r in range(mip_h)]
            for row in reversed(rows):
                result += row
            offset += size
    return result

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

    dds_header.depth       = 1
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
        # BGRA8 uncompressed, Morton-swizzled. Bytes per pixel: [B, G, R, A].
        dds_header.hasAlpha    = True
        dds_header.RGBBitCount = 32
        dds_header.RBitMask    = 0x00FF0000
        dds_header.GBitMask    = 0x0000FF00
        dds_header.BBitMask    = 0x000000FF
        dds_header.ABitMask    = 0xFF000000
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

    num_dimensions = data[0xf]
    depth = data[0xd]
    dds_header.num_mipmaps = data[0xe]
    if num_dimensions == 0x3:
        dds_header.hasDepth  = True
        dds_header.isComplex = True
        dds_header.depth     = depth
    else:
        dds_header.hasDepth = False
        dds_header.depth    = 1
        depth               = 1

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
    if depth > 1:
        expected = sum(
            max(1, dds_header.width >> m) * max(1, dds_header.height >> m) *
            max(1, depth >> m) * int(bytes_per_pixel)
            for m in range(dds_header.num_mipmaps)
        )
    else:
        expected = ffutils.get_img_data_size(dds_header.width,
                dds_header.height, dds_header.num_mipmaps, bytes_per_pixel,
                bytes_per_group)
    if len(data) - 0x80 != expected:
        msg = 'Mipmap number to filesize mismatch'
        if isPermissiveMode:
            print(" - " + msg, end="")
        else:
            raise ValueError(msg)

    dds_header_bytes = dds_header.create()

    if img_fmt == 0xAA1B:
        pixel_data = _deswizzle_and_flip(data[0x80:], dds_header.width,
                                         dds_header.height, dds_header.num_mipmaps,
                                         depth)
        data = bytearray(dds_header_bytes) + pixel_data
    else:
        for i in range(len(dds_header_bytes)):
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
