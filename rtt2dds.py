import math
import os
import sys

def get_DXTn_CC(DXTn):
    if DXTn in range(1,6):
        return bytearray.fromhex(hex(0x30 + DXTn)[2:])
    # elif DXTn == 10:
    else:
        raise ValueError('Unknown image format')

def create_DDS_pixelformat(DXTn):
    '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-pixelformat
    '''
    size = bytearray(b'\x20\x00\x00\x00')
    flags = bytearray(b'\x04\x00\x00\x00') # TODO: dwFlags
    fourCC = bytearray(b'\x44\x58\x54') + get_DXTn_CC(DXTn)
    RGBBitCount = bytearray(b'\x00\x00\x00\x00')
    RBitMask = bytearray(b'\x00\x00\x00\x00')
    GBitMask = bytearray(b'\x00\x00\x00\x00')
    BBitMask = bytearray(b'\x00\x00\x00\x00')
    ABitMask = bytearray(b'\x00\x00\x00\x00')
    return (size + flags + fourCC + RGBBitCount + RBitMask + GBitMask + BBitMask + ABitMask)

def int_to_32ba_BE(number):
    output = bytearray()
    while number > 0:
        byte = number & 0xFF
        output += bytearray.fromhex('{0:02x}'.format(byte))
        number >>= 8
    return output.ljust(4, b'\x00')

def create_DDS_header(DXTn, res_width, res_height):
    '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
    '''
    dds_magic = bytearray(b'\x44\x44\x53\x20')
    header_size = bytearray(b'\x7C\x00\x00\x00') # dwSize
    flags = bytearray(b'\x07\x10\x00\x00') # TODO: dwFlags
    height = int_to_32ba_BE(res_height)
    width = int_to_32ba_BE(res_width)
    pitch_or_linear_size = bytearray(b'\x00\x00\x00\x00') # TODO
    depth = bytearray(b'\x00\x00\x00\x00') # TODO
    mipmapcount = bytearray(b'\x00\x00\x00\x00') # TODO
    reserved = bytearray(b'\x00\x00\x00\x00') * 11 # TODO
    ddspf = create_DDS_pixelformat(DXTn)
    caps = bytearray(b'\x08\x10\x40\x00') # TODO
    caps2 = bytearray(b'\x00\x00\x00\x00') # TODO
    caps3 = bytearray(b'\x00\x00\x00\x00')
    caps4 = bytearray(b'\x00\x00\x00\x00')
    reserved2 = bytearray(b'\x00\x00\x00\x00')

    return (dds_magic +
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

    # Find DXTn format
    if data[0x4] == 0x06:
        DXTn = 1
    elif data[0x4] == 0x07:
        DXTn = 3
    elif data[0x4] == 0x08:
        DXTn = 5
    else:
        raise ValueError('Unknown image format')

    # Get resolution
    # TODO: width <-> height
    width = (data[0x8] << 8) + data[0x9]
    height = (data[0xa] << 8) + data[0xb]

    DDS_header = create_DDS_header(DXTn, width, height)
    for i in range(0, len(DDS_header)):
        data[i] = DDS_header[i]

    with open(os.path.join(os.path.dirname(filepath), os.path.basename(filepath)[:-3] + 'dds'), 'wb') as f:
        f.write(data)

def main():
    for arg in sys.argv[1:]:
        rtt2dds(arg)

if __name__ == '__main__':
    main()
