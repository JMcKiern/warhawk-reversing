#!/usr/bin/env python3

import os
import sys
import struct

def int32_to_bytes(number):
    return struct.pack("<I", number)

def get_img_data_size(width, height, num_mipmaps, bytes_per_pixel, bytes_per_group):
    return int(sum([max(bytes_per_pixel * width * height * ((1/(2.0 ** i)) ** 2), bytes_per_group) for i in range(0, num_mipmaps)]))

def get_DDS_pixelformat_flags(isCompressed, hasAlpha, hasAlphaOnly, isYUV, isLUM):
    # Flags
    DDPF_ALPHAPIXELS = 0x1
    DDPF_ALPHA       = 0x2
    DDPF_FOURCC      = 0x4
    DDPF_RGB         = 0x40
    DDPF_YUV         = 0x200
    DDPF_LUMINANCE   = 0x20000

    required = 0

    flags = required
    if hasAlpha:
        flags |= DDPF_ALPHAPIXELS
    if hasAlphaOnly:
        flags |= DDPF_ALPHA
    if isCompressed:
        flags |= DDPF_FOURCC
    else:
        flags |= DDPF_RGB # TODO: Should this flags be added when hasAlpha?
    if isYUV:
        flags |= DDPF_YUV
    if isLUM:
        flags |= DDPF_LUMINANCE
    return flags

def create_DDS_pixelformat(fourCC, isCompressed, hasAlpha, hasAlphaOnly, isYUV, isLUM, RGBBitCount, RBitMask, GBitMask, BBitMask, ABitMask):
    '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-pixelformat
    '''
    size        = int32_to_bytes(32)
    flags       = int32_to_bytes(get_DDS_pixelformat_flags(isCompressed, hasAlpha, hasAlphaOnly, isYUV, isLUM))
    # fourCC passed as argument
    RGBBitCount = int32_to_bytes(RGBBitCount)
    RBitMask    = int32_to_bytes(RBitMask)
    GBitMask    = int32_to_bytes(GBitMask)
    BBitMask    = int32_to_bytes(BBitMask)
    ABitMask    = int32_to_bytes(ABitMask)
    return bytearray(size + flags + fourCC + RGBBitCount + RBitMask + GBitMask + BBitMask + ABitMask)

def get_DDS_header_flags(isCompressed, isPitch, isMipmapped, hasDepth):
    # Flags
    DDSD_CAPS        = 0x1
    DDSD_HEIGHT      = 0x2
    DDSD_WIDTH       = 0x4
    DDSD_PITCH       = 0x8
    DDSD_PIXELFORMAT = 0x1000
    DDSD_MIPMAPCOUNT = 0x20000
    DDSD_LINEARSIZE  = 0x80000
    DDSD_DEPTH       = 0x800000

    required = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT

    flags = required
    if isPitch:
        if isCompressed:
            flags |= DDSD_LINEARSIZE
        else:
            flags |= DDSD_PITCH
    if isMipmapped:
        flags |= DDSD_MIPMAPCOUNT
    if hasDepth:
        flags |= DDSD_DEPTH
    return flags

def get_DDS_header_caps(isComplex, isMipmapped):
    # Flags
    DDSCAPS_COMPLEX = 0x8
    DDSCAPS_MIPMAP  = 0x400000
    DDSCAPS_TEXTURE = 0x1000

    required = DDSCAPS_TEXTURE

    flags = required
    if isComplex:
        flags |= DDSCAPS_COMPLEX
    if isMipmapped:
        flags |= DDSCAPS_MIPMAP
    return flags

def create_DDS_header(fourCC, width, height, num_mipmaps, hasAlpha, isPitch,
        isMipmapped, hasDepth, isComplex, hasAlphaOnly, isYUV, isLUM,
        RGBBitCount, RBitMask, GBitMask, BBitMask, ABitMask):
    '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
    '''
    isCompressed = (fourCC != (b'\x00' * 4))

    dds_magic            = b'DDS '
    header_size          = int32_to_bytes(124) #dwSize
    flags                = int32_to_bytes(get_DDS_header_flags(isCompressed, isPitch, isMipmapped, hasDepth))
    height               = int32_to_bytes(height)
    width                = int32_to_bytes(width)
    pitch_or_linear_size = int32_to_bytes(0) # TODO
    depth                = int32_to_bytes(0) # TODO
    mipmapcount          = int32_to_bytes(num_mipmaps)
    reserved             = int32_to_bytes(0) * 11
    ddspf                = create_DDS_pixelformat(fourCC, isCompressed, hasAlpha, hasAlphaOnly, isYUV, isLUM, RGBBitCount, RBitMask, GBitMask, BBitMask, ABitMask)
    caps                 = int32_to_bytes(get_DDS_header_caps(isComplex, isMipmapped))
    caps2                = int32_to_bytes(0) # TODO: deals with cubemaps/volume textures
    caps3                = int32_to_bytes(0)
    caps4                = int32_to_bytes(0)
    reserved2            = int32_to_bytes(0)

    return bytearray(dds_magic +
    header_size +
    flags +
    height +
    width +
    pitch_or_linear_size +
    depth +
    mipmapcount +
    reserved +
    ddspf +
    caps +
    caps2 +
    caps3 +
    caps4 +
    reserved2)

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
        raise ValueError('Expecting 0x80 at pos 0')

    # File size (+4 since points to start of last DWORD)
    filesize = (data[0x1] << 16) + (data[0x2] << 8) + (data[0x3]) + 4
    if len(data) != filesize:
        raise ValueError('Filesize does not match header')

    # Find compression method
    if data[0x4] == 0x01 or data[0x4] == 0x05: # No compression
        fourCC = int32_to_bytes(0)
    elif data[0x4] == 0x06:
        fourCC = b'DXT1'
    elif data[0x4] == 0x07:
        fourCC = b'DXT3'
    elif data[0x4] == 0x08:
        fourCC = b'DXT5'
    else:
        raise ValueError('Unknown compression method')

    if data[0x5] != 0x0:
        raise ValueError('Expecting 0x0 at pos 5')

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
    if len(data) - 0x80 != get_img_data_size(width, height, num_mipmaps, bytes_per_pixel, bytes_per_group):
        raise ValueError('Mipmap number to filesize mismatch')

    DDS_header = create_DDS_header(fourCC, width, height, num_mipmaps, hasAlpha,
            isPitch, isMipmapped, hasDepth, isComplex, hasAlphaOnly, isYUV,
            isLUM, RGBBitCount, RBitMask, GBitMask, BBitMask, ABitMask)
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
