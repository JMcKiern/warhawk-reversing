from ffutils import int32_to_bytes

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
    header_size          = int32_to_bytes(124)
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
