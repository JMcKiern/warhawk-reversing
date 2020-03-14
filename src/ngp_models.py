import sys
import struct

def extractModel(filename: str, headerOffset: int):
    with open(filename, 'rb') as f:
        data = bytearray(f.read())

    header = data[headerOffset:headerOffset+0x5c]
    if (header[0x0:0x4] != struct.pack(">I", 1)):
        raise ValueError("Wrong magic")
    numberOfVertices, = struct.unpack(">H", header[0x24:0x24+2])
    numberOfIndicesUsedInFaces, = struct.unpack(">I", header[0x1c:0x1c+4])
    facesOffset, = struct.unpack(">I", header[0x28:0x28+4])
    vertexOffset, = struct.unpack(">I", header[0x34:0x34+4])

    numberOfFaces = int(numberOfIndicesUsedInFaces / 3)

    faces = data[facesOffset:facesOffset+(numberOfFaces*6)]
    vertices = data[vertexOffset:vertexOffset+(numberOfVertices*6)]

    with open(filename + "_" + hex(headerOffset) + ".obj", "w") as f:
        for i in range(0, len(vertices), 6):
            f.write("v ")
            for j in range(0, 6, 2):
                val, = struct.unpack(">h", vertices[i+j:i+j+2])
                f.write(str((val + 0x8000) / 0x8000) + " ")
            f.write("\n")
        for i in range(0, len(faces), 6):
            f.write("f ")
            for j in range(0, 6, 2):
                val, = struct.unpack(">H", faces[i+j:i+j+2])
                f.write(str(int(val + 1)) + " ")
            f.write("\n")

def extractModels(filename: str, start: int, end: int):
    with open(filename, 'rb') as f:
        data = bytearray(f.read())

    for i in range(start, end, 0x4):
        if (data[i:i+0x4] == struct.pack(">I", 1)):
            extractModel(filename, i)

def main():
    start_header = int(sys.argv[1], 16)
    end_header = int(sys.argv[2], 16)
    filename = sys.argv[3]
    print(hex(start_header) + " " + hex(end_header) + " " + filename)
    extractModels(filename + ".ngp", start_header, end_header)

if __name__ == "__main__":
    main()
