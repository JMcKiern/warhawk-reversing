import os
import sys
import struct

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

def create_DDS_pixelformat(fourCC, isCompressed, hasAlpha, hasAlphaOnly, isYUV, isLUM):
    '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-pixelformat
    '''
    size        = int32_to_bytes(32)
    flags       = int32_to_bytes(get_DDS_pixelformat_flags(isCompressed, hasAlpha, hasAlphaOnly, isYUV, isLUM))
    # fourCC passed as argument
    RGBBitCount = int32_to_bytes(8) #TODO
    RBitMask    = int32_to_bytes(0) #TODO
    GBitMask    = int32_to_bytes(0) #TODO
    BBitMask    = int32_to_bytes(0) #TODO
    ABitMask    = int32_to_bytes(0xFF) #TODO
    return bytearray(size + flags + fourCC + RGBBitCount + RBitMask + GBitMask + BBitMask + ABitMask)

def int32_to_bytes(number):
    return struct.pack("<I", number)

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

def create_DDS_header(fourCC, res_width, res_height):
    '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
    '''
    isCompressed = fourCC != b'\x00' * 4
    hasAlpha = True#isCompressed # TODO: Change this
    # TODO: why False?
    isPitch = False
    isMipmapped = False
    hasDepth = False
    isComplex = False
    # "Used in some older DDS files..."
    # Let's just ignore for now
    hasAlphaOnly = True
    isYUV = False
    isLUM = False


    dds_magic            = b'DDS '
    header_size          = int32_to_bytes(124) #dwSize
    flags                = int32_to_bytes(get_DDS_header_flags(isCompressed, isPitch, isMipmapped, hasDepth))
    height               = int32_to_bytes(res_height)
    width                = int32_to_bytes(res_width)
    pitch_or_linear_size = int32_to_bytes(0) # TODO
    depth                = int32_to_bytes(0) # TODO
    mipmapcount          = int32_to_bytes(0) # TODO
    reserved             = int32_to_bytes(0) * 11
    ddspf                = create_DDS_pixelformat(fourCC, isCompressed, hasAlpha, hasAlphaOnly, isYUV, isLUM)
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
        fourCC = int32_to_bytes(0)
    elif data[0x4] == 0x06:
        fourCC = b'DXT1'
    elif data[0x4] == 0x07:
        fourCC = b'DXT3'
    elif data[0x4] == 0x08:
        fourCC = b'DXT5'
    else:
        #raise ValueError('Unknown image format')
        fourCC = int32_to_bytes(0)

    if data[0x5] != 0x0:
        raise ValueError('Expecting 0x0 at pos 5')

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
