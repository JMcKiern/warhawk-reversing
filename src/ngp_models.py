import sys
import struct

def getUVs(filename: str, header: bytearray, count: int):
    startOfLinkers = 0x38
    for i in range(startOfLinkers, len(header), 0x0C):
        linker = header[i:i+0x0C]
        if linker[0:4] == struct.pack(">I", 0x00080003): # I think this identifies the UV coords
            repeatLength = linker[0x4]
            isDataInNGP = linker[0x6] == 0x01
            offset, = struct.unpack(">I", linker[0x08:0x08+0x04])
            break
    else:
        return False

    def translate(val):
        return (((val / 0x3800) ** 10) / 2)

    if isDataInNGP:
        extension = ".ngp"
    else:
        extension = ".vram"

    with open(filename + extension, "rb") as f:
        data = bytearray(f.read())
    uvs = []
    for i in range(offset, offset + (count * repeatLength), repeatLength):
        # print(hex(i))
        # print("data " + hex(*struct.unpack(">I", data[i:i+4])))
        curr_x, = struct.unpack(">H", data[i:i+2])
        curr_y, = struct.unpack(">H", data[i+2:i+4])
        uvs.append(translate(curr_x))
        uvs.append(translate(curr_y))

    return uvs

def extractModel(filename: str, headerOffset: int):
    with open(filename + ".ngp", 'rb') as f:
        ngp_data = bytearray(f.read())

    header = ngp_data[headerOffset:headerOffset+0x5c]
    if (header[0x0:0x4] != struct.pack(">I", 1)):
        raise ValueError("Wrong magic")
    numberOfVertices, = struct.unpack(">H", header[0x24:0x24+2])
    numberOfIndicesUsedInFaces, = struct.unpack(">I", header[0x1c:0x1c+4])
    facesOffset, = struct.unpack(">I", header[0x28:0x28+4])
    vertexOffset, = struct.unpack(">I", header[0x34:0x34+4])

    numberOfFaces = int(numberOfIndicesUsedInFaces / 3)

    faces = ngp_data[facesOffset:facesOffset+(numberOfFaces*6)]
    vertices = ngp_data[vertexOffset:vertexOffset+(numberOfVertices*6)]
    uvs = getUVs(filename, header, numberOfVertices)

    with open(filename + "_" + hex(headerOffset) + ".obj", "w") as f:
        for i in range(0, len(vertices), 6):
            f.write("v ")
            for j in range(0, 6, 2):
                val, = struct.unpack(">h", vertices[i+j:i+j+2])
                f.write(str((val + 0x8000) / 0x8000) + " ")
            f.write("\n")
        for i in range(1, len(uvs), 2):
            f.write("vt ")
            f.write(str(uvs[i-1]))
            f.write(" ")
            f.write(str(uvs[i]))
            f.write("\n")
        for i in range(0, len(faces), 6):
            f.write("f ")
            for j in range(0, 6, 2):
                val, = struct.unpack(">H", faces[i+j:i+j+2])
                f.write(str(int(val + 1)) + "/" + str(int(val + 1)) + " ")
            f.write("\n")

def extractModels(filename: str, start: int, end: int):
    with open(filename + ".ngp", 'rb') as f:
        data = bytearray(f.read())

    for i in range(start, end, 0x4):
        if (data[i:i+0x4] == struct.pack(">I", 1)):
            extractModel(filename, i)

def main():
    start_header = int(sys.argv[1], 16)
    end_header = int(sys.argv[2], 16)
    filename = sys.argv[3]
    print(hex(start_header) + " " + hex(end_header) + " " + filename)
    extractModels(filename, start_header, end_header)

if __name__ == "__main__":
    main()
