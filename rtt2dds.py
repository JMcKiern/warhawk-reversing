import math
import os
import sys
import struct

def create_DDS_pixelformat(fourCC):
    '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-pixelformat
    '''
    size        = int32_to_bytes(32)
    flags       =  b'\x04\x00\x00\x00' # TODO: dwFlags
    # fourCC passed as argument
    RGBBitCount = b'\x00\x00\x00\x00' #TODO
    RBitMask    = b'\x00\x00\x00\x00' #TODO
    GBitMask    = b'\x00\x00\x00\x00' #TODO
    BBitMask    = b'\x00\x00\x00\x00' #TODO
    ABitMask    = b'\x00\x00\x00\x00' #TODO
    return bytearray(size + flags + fourCC + RGBBitCount + RBitMask + GBitMask + BBitMask + ABitMask)

def int32_to_bytes(number):
    return struct.pack("<I", number)

def create_DDS_header(fourCC, res_width, res_height):
    '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
    '''
    dds_magic            = b'DDS '
    header_size          = int32_to_bytes(124) #dwSize
    flags                = b'\x07\x10\x00\x00' # TODO: dwFlags
    height               = int32_to_bytes(res_height)
    width                = int32_to_bytes(res_width)
    pitch_or_linear_size = b'\x00\x00\x00\x00' # TODO
    depth                = b'\x00\x00\x00\x00' # TODO
    mipmapcount          = b'\x00\x00\x00\x00' # TODO
    reserved             = b'\x00\x00\x00\x00' * 11
    ddspf                = create_DDS_pixelformat(fourCC)
    caps                 = b'\x08\x10\x40\x00' # TODO
    caps2                = b'\x00\x00\x00\x00' # TODO
    caps3                = b'\x00\x00\x00\x00'
    caps4                = b'\x00\x00\x00\x00'
    reserved2            = b'\x00\x00\x00\x00'

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

    # DWORD           dwSize;
    # DWORD           dwFlags;
    # DWORD           dwHeight;
    # DWORD           dwWidth;
    # DWORD           dwPitchOrLinearSize;
    # DWORD           dwDepth;
    # DWORD           dwMipMapCount;
    # DWORD           dwReserved1[11];
    # DDS_PIXELFORMAT ddspf;
    # DWORD           dwCaps;
    # DWORD           dwCaps2;
    # DWORD           dwCaps3;
    # DWORD           dwCaps4;
    # DWORD           dwReserved2;

def rtt2dds(filepath):
    print("Processing " + filepath)
    with open(filepath, 'rb') as f:
        data = bytearray(f.read())

    # Magic
    if data[0x0] != 0x80:
        raise ValueError('Expecting 0x80 at pos 0')

    # Find compression method
    if data[0x4] == 0x05: # No compression
        fourCC = b'\x00\x00\x00\x00'
    elif data[0x4] == 0x06:
        fourCC = b'DXT1'
    elif data[0x4] == 0x07:
        fourCC = b'DXT3'
    elif data[0x4] == 0x08:
        fourCC = b'DXT5'
    else:
        raise ValueError('Unknown image format')

    # Get resolution
    # TODO: width <-> height
    width = (data[0x8] << 8) + data[0x9]
    height = (data[0xa] << 8) + data[0xb]

    DDS_header = create_DDS_header(fourCC, width, height)
    for i in range(0, len(DDS_header)):
        data[i] = DDS_header[i]

    with open(os.path.join(os.path.dirname(filepath), os.path.basename(filepath)[:-3] + 'dds'), 'wb') as f:
        f.write(data)

def main():
    for arg in sys.argv[1:]:
        rtt2dds(arg)

if __name__ == '__main__':
    main()
