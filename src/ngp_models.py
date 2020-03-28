#!/usr/bin/env python3

import sys
import struct
import rtt2dds
import ngp_textures

def dereferenceRelativePointer(data, locOfPointer):
    relativeOffset, = struct.unpack(">i", data[locOfPointer:locOfPointer+4])
    offset = locOfPointer + relativeOffset
    return offset

def getUVs(filename: str, header: bytearray, count: int):
    uvs = []
    startOfLinkers = 0x38
    for i in range(startOfLinkers, len(header), 0x0C):
        linker = header[i:i+0x0C]
        if linker[0:4] == struct.pack(">I", 0x00080003): # I think this identifies the UV coords
            repeatLength = linker[0x4]
            isDataInNGP = linker[0x6] == 0x01
            offset, = struct.unpack(">I", linker[0x08:0x08+0x04])
            break
    else:
        return uvs

    def translate(val):
        return (((val / 0x3800) ** 10) / 2)

    if isDataInNGP:
        extension = ".ngp"
    else:
        extension = ".vram"

    with open(filename + extension, "rb") as f:
        data = bytearray(f.read())
    for i in range(offset, offset + (count * repeatLength), repeatLength):
        uvCoords = []
        curr_x, = struct.unpack(">H", data[i:i+2])
        curr_y, = struct.unpack(">H", data[i+2:i+4])
        uvCoords.append(translate(curr_x))
        uvCoords.append(1-translate(curr_y)) # Flip Y because textures are flipped
        uvs.append(uvCoords)
    return uvs

def getFaces(filenameStem: str, facesOffset: int, numberOfIndicesUsedInFaces: int):
    with open(filenameStem + ".ngp", 'rb') as f:
        ngp_data = bytearray(f.read())
    numberOfFaces = int(numberOfIndicesUsedInFaces / 3) # 3 vertices per face
    facesRaw = ngp_data[facesOffset:facesOffset+(numberOfFaces*6)]
    faces = []
    for i in range(0, len(facesRaw), 6):
        faceVertices = []
        for j in range(0, 6, 2):
            val, = struct.unpack(">H", facesRaw[i+j:i+j+2])
            faceVertices.append(val + 1) # Index from 1
        faces.append(faceVertices)
    return faces

def getVertices(filenameStem: str, vertexOffset: int, numberOfVertices: int):
    with open(filenameStem + ".ngp", 'rb') as f:
        ngp_data = bytearray(f.read())

    verticesRaw = ngp_data[vertexOffset:vertexOffset+(numberOfVertices*6)]
    vertices = []
    for i in range(0, len(verticesRaw), 6):
        vertexCoords = []
        for j in range(0, 6, 2):
            val, = struct.unpack(">h", verticesRaw[i+j:i+j+2])
            vertexCoords.append((val + 0x8000) / 0x8000)
        vertices.append(vertexCoords)
    return vertices

def extractNGPTexture(filenameStem: str, headerLoc: int):
    with open(filenameStem + ".ngp", "rb") as f:
        ngp_data = bytearray(f.read())
    with open(filenameStem + ".vram", "rb") as f:
        vram_data = bytearray(f.read())
    rttmod_header = ngp_data[headerLoc:headerLoc+0x10]
    return ngp_textures.parseNGPTextureHeader(rttmod_header, ngp_data, vram_data)

def extractModel(filenameStem: str, headerOffset: int):
    with open(filenameStem + ".ngp", 'rb') as f:
        ngp_data = bytearray(f.read())

    numLinkers = ngp_data[headerOffset+0x26]
    headerSize = 0x2C + (numLinkers * 0x0C)

    header = ngp_data[headerOffset:headerOffset+headerSize]
    if (header[0x0:0x4] != struct.pack(">I", 1)):
        raise ValueError("Wrong magic")
    numberOfVertices, = struct.unpack(">H", header[0x24:0x24+2])
    numberOfIndicesUsedInFaces, = struct.unpack(">I", header[0x1c:0x1c+4])
    facesOffset, = struct.unpack(">I", header[0x28:0x28+4])
    vertexOffset, = struct.unpack(">I", header[0x34:0x34+4])

    faces = getFaces(filenameStem, facesOffset, numberOfIndicesUsedInFaces)
    vertices = getVertices(filenameStem, vertexOffset, numberOfVertices)
    uvs = getUVs(filenameStem, header, numberOfVertices)


    ptr = dereferenceRelativePointer(ngp_data, headerOffset+0x04)
    dataptr = dereferenceRelativePointer(ngp_data, ptr+0x10)
    textureHeaderOffset = -1
    for i in range(0, ptr - dataptr, 4):
        if (ngp_data[dataptr+i:dataptr+i+4] == struct.pack(">I", 0x00111122) and
                ngp_data[dataptr+i+4:dataptr+i+8] != struct.pack(">I", 0x00)):
            textureHeaderOffset = dereferenceRelativePointer(ngp_data, dataptr+i+4)

    modelName = filenameStem + "_" + hex(headerOffset)

    with open(modelName + ".obj", "w") as f:
        if textureHeaderOffset != -1:
            f.write("mtllib " + modelName + ".mtl\n")
            f.write("usemtl Textured\n")
        f.write("o " + modelName + "\n")
        for i in range(0, len(vertices)):
            f.write("v ")
            f.write(" ".join([str(c) for c in vertices[i]]))
            f.write("\n")
        for i in range(0, len(uvs)):
            f.write("vt ")
            f.write(" ".join([str(c) for c in uvs[i]]))
            f.write("\n")
        for i in range(0, len(faces)):
            f.write("f ")
            f.write(" ".join([(str(v) + "/" + str(v)) for v in faces[i]]))
            f.write("\n")

    textureFilename = modelName + ".dds"
    if textureHeaderOffset != -1:
        rttdata = extractNGPTexture(filenameStem, textureHeaderOffset)
        ddsdata = rtt2dds.rtt2dds(rttdata)
        with open(textureFilename, "wb") as f:
            f.write(ddsdata)

        with open(modelName + ".mtl", "w") as f:
            f.write("newmtl Textured\n")
            f.write("Kd 1.0 1.0 1.0\n")
            f.write("map_Kd " + textureFilename + "\n")

def findNextModel(data: bytearray, start: int):
    for i in range(start, len(data), 4):
        if (data[i:i+0x4] != struct.pack(">I", 1)):
            continue
        if (data[i+0x14:i+0x18] != struct.pack(">I", 0x3C000000)):
            continue
        numLinkers, = struct.unpack(">B", data[i+0x26:i+0x27])
        length = 0x2C + (numLinkers * 0x0C)
        return i, length
    return -1, 0

def extractModels(filename: str):
    with open(filename + ".ngp", 'rb') as f:
        data = bytearray(f.read())

    loc = 0x0
    while True:
        loc, length = findNextModel(data, loc)
        if loc == -1:
            break
        print("Extracting model located at " + hex(loc))
        extractModel(filename, loc)
        loc += length

def main():
    filename = sys.argv[1]
    extractModels(filename)

if __name__ == "__main__":
    main()
