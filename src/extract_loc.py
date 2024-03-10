import argparse
import struct

def dereferenceRelativePointer(data, locOfPointer):
    relativeOffset, = struct.unpack(">i", data[locOfPointer:locOfPointer+4])
    offset = locOfPointer + relativeOffset
    return offset

def readCStr(data, offset):
    s = ""
    cp = 0
    c = struct.unpack(">B", data[offset+cp:offset+cp+0x1])[0]
    while c != 0:
        s += chr(c)
        cp += 0x1
        c = struct.unpack(">B", data[offset+cp:offset+cp+0x1])[0]
    return s

def readU16CStr(data, offset):
    s = ""
    cp = 0
    c = struct.unpack(">H", data[offset+cp:offset+cp+0x2])[0]
    while c != 0:
        s += chr(c)
        cp += 0x2
        c = struct.unpack(">H", data[offset+cp:offset+cp+0x2])[0]
    return s

def extract_loc(data: bytearray):
    num_categories = struct.unpack(">I", data[0x0:0x4])[0]
    categories = {}
    for i in range(num_categories):
        LEN_CATEGORY_BYTES = 3 * 0x4
        c = 0x4 + LEN_CATEGORY_BYTES * i
        category_name = readCStr(data, c)
        categories[category_name] = {}
        category_ptr = dereferenceRelativePointer(data, c + 0x8)
        num_entries = struct.unpack(">I", data[category_ptr:category_ptr+0x4])[0]
        for j in range(num_entries):
            LEN_ENTRY_BYTES = 2 * 0x4
            e = category_ptr + 0x4 + LEN_ENTRY_BYTES * j
            entry_id = struct.unpack(">I", data[e:e+0x4])[0]
            ep = dereferenceRelativePointer(data, e+0x4)
            entry_str = readU16CStr(data, ep)
            categories[category_name][entry_id] = entry_str
    return categories


def main():
    parser = argparse.ArgumentParser(
            description="Extract .loc")
    parser.add_argument("filepath", nargs="+", help="path to file")
    args = parser.parse_args()

    for filepath in args.filepath:
        print("Processing " + filepath)
        with open(filepath, 'rb') as f:
            data = bytearray(f.read())
        outdata = extract_loc(data)

        with open('{}.txt'.format(filepath), 'w') as f:
            for category, c_dict in outdata.items():
                for entry_id, entry_str in c_dict.items():
                    f.write("{}\t{}\t{}".format(category, entry_id, repr(entry_str)))
                    f.write("\n")


if __name__ == '__main__':
    main()
