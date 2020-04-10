# Table 2 (Texture Table)

Table 2 is a Standard Table

Table entries are relative pointers to NGP Texture Headers

## NGP Texture Header

- Length of 0x10
- These are .rtt headers but are missing the first 4 bytes
- The last 4 bytes gives the offset of the texture data
- Byte 0x8 (or 0xc after adding the first 4 bytes) indicates where the texture data is
  located
    - 0x00 means in the .vram file
    - 0x01 means in the .ngp file
