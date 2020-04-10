#!/usr/bin/env python3

import argparse
import struct

def dereferenceRelativePointer(data: bytearray, locOfPointer: int):
    relativeOffset = struct.unpack(">i", data[locOfPointer:locOfPointer+4])[0]
    offset = locOfPointer + relativeOffset
    return offset

def main():
    parser = argparse.ArgumentParser(
            description="Find the address that a relative pointer points to")
    parser.add_argument("filepath", help="path to the file")
    parser.add_argument("offset", help="offset of the pointer in hex (eg 0x1c)")
    args = parser.parse_args()
    with open(args.filepath, 'rb') as f:
        data = bytearray(f.read())
    print(hex(dereferenceRelativePointer(data, int(args.offset, 16))))

if __name__ == "__main__":
    main()
