#!/usr/bin/env python3

import struct
import argparse

def indent(level: int):
    for i in range(0, level):
        print("\t", end="")

def printLinksTo(data: int, toOffset: int, level: int):
    isRootPrinted = False
    for currOffset in range(0, len(data), 4):
        if len(data[currOffset:currOffset+4]) != 4:
            continue

        # Deal with relative pointers
        current_val, = struct.unpack(">i", data[currOffset:currOffset+4])
        if current_val + currOffset == toOffset and current_val != 0:
            if level == 1 and not isRootPrinted:
                print(hex(toOffset))
                isRootPrinted = True
            indent(level)
            print(hex(currOffset) + " (R)")
            printLinksTo(data, currOffset, level+1)

        # Deal with absolute pointers
        current_val, = struct.unpack(">I", data[currOffset:currOffset+4])
        if current_val == toOffset:
            if level == 1 and not isRootPrinted:
                print(hex(toOffset))
                isRootPrinted = True
            indent(level)
            print(hex(currOffset) + " (A)")
            printLinksTo(data, currOffset, level+1)

def main():
    parser = argparse.ArgumentParser(
            description="Find pointers that might point to the given address(es)")
    parser.add_argument("filepath", help="path to the file")
    parser.add_argument("--range", action="store_true", help="use a range - must be accompanied by exactly two offsets (start and end)")
    parser.add_argument("offset", nargs="+", help="hex offset(s) to the addresses")
    args = parser.parse_args()
    if args.range:
        if len(args.offset) != 2:
            parser.error("There must be exactly two offsets when using --range")
        start = int(args.offset[0], 16)
        end = int(args.offset[1], 16)
        offsets = [*range(start, end, 4)]
    else:
        offsets = [int(i, 16) for i in args.offset]

    with open(args.filepath, "rb") as f:
        data = bytearray(f.read())
    for offset in offsets:
        printLinksTo(data, offset, 1)

if __name__ == "__main__":
    main()
