import struct

class DdsFlags:
    # Pixelformat Flags
    DDPF_ALPHAPIXELS = 0x1
    DDPF_ALPHA       = 0x2
    DDPF_FOURCC      = 0x4
    DDPF_RGB         = 0x40
    DDPF_YUV         = 0x200
    DDPF_LUMINANCE   = 0x20000

    # DDS Header Flags
    DDSD_CAPS        = 0x1
    DDSD_HEIGHT      = 0x2
    DDSD_WIDTH       = 0x4
    DDSD_PITCH       = 0x8
    DDSD_PIXELFORMAT = 0x1000
    DDSD_MIPMAPCOUNT = 0x20000
    DDSD_LINEARSIZE  = 0x80000
    DDSD_DEPTH       = 0x800000

    # DDS CAPS Flags
    DDSCAPS_COMPLEX = 0x8
    DDSCAPS_MIPMAP  = 0x400000
    DDSCAPS_TEXTURE = 0x1000

class DdsHeader:
    __ddsMagic: bytes = b'DDS '
    __headerSize: int = 124

    __isMipmapped: bool
    __isCompressed: bool

    fourCC: str
    width: int
    height: int
    num_mipmaps: int
    hasAlpha: bool
    isPitch: bool
    hasDepth: bool
    isComplex: bool
    hasAlphaOnly: bool
    isYUV: bool
    isLUM: bool
    RGBBitCount: int
    RBitMask: int
    GBitMask: int
    BBitMask: int
    ABitMask: int

    def __get_pixelformat_flags(self):
        flags = 0 # No mandatory flags
        if self.hasAlpha:
            flags |= DdsFlags.DDPF_ALPHAPIXELS
        if self.hasAlphaOnly:
            flags |= DdsFlags.DDPF_ALPHA
        if self.__isCompressed:
            flags |= DdsFlags.DDPF_FOURCC
        else:
            flags |= DdsFlags.DDPF_RGB # TODO: Should this flag be added when hasAlpha?
        if self.isYUV:
            flags |= DdsFlags.DDPF_YUV
        if self.isLUM:
            flags |= DdsFlags.DDPF_LUMINANCE
        return flags

    def __create_pixelformat(self):
        '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-pixelformat
        '''
        size        = struct.pack("<I", 32)
        flags       = struct.pack("<I", self.__get_pixelformat_flags())
        # fourCC passed straight from class variable
        RGBBitCount = struct.pack("<I", self.RGBBitCount)
        RBitMask    = struct.pack("<I", self.RBitMask)
        GBitMask    = struct.pack("<I", self.GBitMask)
        BBitMask    = struct.pack("<I", self.BBitMask)
        ABitMask    = struct.pack("<I", self.ABitMask)
        return bytearray(size + flags + self.fourCC + RGBBitCount + RBitMask +
                GBitMask + BBitMask + ABitMask)

    def __get_header_flags(self):
        flags = 0

        # Add mandatory flags
        flags |= DdsFlags.DDSD_CAPS
        flags |= DdsFlags.DDSD_HEIGHT
        flags |= DdsFlags.DDSD_WIDTH
        flags |= DdsFlags.DDSD_PIXELFORMAT

        if self.isPitch:
            if self.__isCompressed:
                flags |= DdsFlags.DDSD_LINEARSIZE
            else:
                flags |= DdsFlags.DDSD_PITCH
        if self.__isMipmapped:
            flags |= DdsFlags.DDSD_MIPMAPCOUNT
        if self.hasDepth:
            flags |= DdsFlags.DDSD_DEPTH
        return flags

    def __get_caps_flags(self):
        flags = 0

        # Add mandatory flags
        flags |= DdsFlags.DDSCAPS_TEXTURE
        flags |= DdsFlags.DDSD_HEIGHT
        flags |= DdsFlags.DDSD_WIDTH
        flags |= DdsFlags.DDSD_PIXELFORMAT

        if self.isComplex:
            flags |= DdsFlags.DDSCAPS_COMPLEX
        if self.__isMipmapped:
            flags |= DdsFlags.DDSCAPS_MIPMAP
        return flags

    def create(self):
        '''https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
        '''
        self.__isCompressed = (self.fourCC != (b'\x00' * 4))
        self.__isMipmapped = self.num_mipmaps != 0x01

        header = bytearray()
        header += self.__ddsMagic
        header += struct.pack("<I", self.__headerSize)
        header += struct.pack("<I", self.__get_header_flags())
        header += struct.pack("<I", self.height)
        header += struct.pack("<I", self.width)
        header += struct.pack("<I", 0) # TODO: pitch or linear size
        header += struct.pack("<I", 0) # TODO: depth
        header += struct.pack("<I", self.num_mipmaps)
        header += struct.pack("<I", 0) * 11 # Reserved
        header += self.__create_pixelformat()
        header += struct.pack("<I", self.__get_caps_flags())
        header += struct.pack("<I", 0) # TODO: caps2 - this deals with cubemaps/volume textures
        header += struct.pack("<I", 0) # caps3
        header += struct.pack("<I", 0) # caps4
        header += struct.pack("<I", 0) # reserved2

        return header
