# NGP

.ngp files store models, texture data, the model data, UV coordinates and
presumably some other data (animation, normal maps etc.)

## Header

The header is 0x20 bytes long.

|Offset|Length|Example|Name|Notes|
|---|---|---|---|---|
|0x00|0x08|0x696570334616A42B|Magic Number|NGPs always start with this|
|0x08|0x04|0x466F37AB|Object Identifier|Present in PTR and VRAM file headers for same object|
|0x0C|0x04|0x0000001C|[Table 1](ngp/Table1.md) Pointer|Relative pointer|
|0x10|0x04|0x00000070|[Texture Table (Table 2)](ngp/Table2.md) Pointer|Relative pointer|
|0x14|0x04|0x00095FB4|[Table 3](ngp/Table3.md) Pointer|Relative pointer|
|0x18|0x04|0x00002F68|[Data 4](ngp/Data4.md) Pointer|Relative pointer|
|0x1C|0x04|0x000022E0|[Data 5](ngp/Data5.md) Pointer|Relative pointer|

## Overall File Structure

- Header
- Table 1
- Texture Table (Table 2)
- Unknown
- Model headers (maybe includes pointer to texture headers?)
- Unknown
- Model data
    1. Face data - Each face is 3 vertex indices which are shorts
    2. Vertex data - short_signed
- Unknown
- Snippets of stuff with a header (at the bottom of the data?) that includes
  strings like "hud" and "vehicle"
- Unknown
- NGP Texture Headers
- Unknown
- Texture data (pointed to by the NGP Texture Headers)
- Unknown

## Subparts

- [Table 1](ngp/Table1.md)
- [Texture Table (Table 2)](ngp/Table2.md)
- [Table 3](ngp/Table3.md)
- [Data 4](ngp/Data4.md)
- [Data 5](ngp/Data5.md)
- [Model Headers](ngp/ModelHeader.md)

## Notes

In addition to the terminology outlined in the docs [README.md](README.md),
there is some terminology specific to NGP:

### Standard Table

Offset | Length | Example | Name | Notes
-- | -- | -- | -- | --
0x00 | 0x04 | 0x00000001 | Number of entries in table |  
0x04 + (n * 0x04) | 0x04 | 0x00000804 | Entry in table | Relative pointer
