# Model Header

Model Headers contain the pointers to the faces, vertices, UV coordinates and a data structure that leads to the textures.

### Model Header Type 1 - Static Mesh

|Offset|Length|Example|Name|Notes|
|---|---|---|---|---|
|0x00|0x04|0x00000001|Magic Number||
|0x04|0x04|0x0000B114|Relative pointer to unknown data structure|The data structure has links to the texture headers|
|0x08|0x04|0x43780000|*Unknown*|This is likely a float|
|0x0C|0x04|0x437E0000|*Unknown*|This is likely a float|
|0x10|0x04|0x439A0000|*Unknown*|This is likely a float|
|0x14|0x04|0x3C000000|*Unknown*|This is likely a float|
|0x18|0x04|0x00000004|*Unknown*||
|0x1C|0x04|0x00000366|Indices Used in Faces|Number of Faces * 3|
|0x20|0x04|0x000001B9|*Unknown*|Is generally Number of Vertices. However, does not always match. Need to investigate.|
|0x24|0x02|0x01B9|Number of Vertices||
|0x26|0x01|0x05|Number of Linkers|headerSize = 0x2C + (numLinkers * 0x0C)|
|0x27|0x01|0x01|*Unknown*||
|0x28|0x04|0x00001F00|Face Offset||
|0x2C|0x04|0x00000005|*Unknown*||
|0x30|0x04|0x06030100|*Unknown*||
|0x34|0x04|0x000025D0|Vertex Offset||
|0x38|0x0C|0x000200041003000000114980|*Unknown Structure*|See below|
|0x44|0x0C|0x000A00041004000000114983|*Unknown Structure*|See below|
|0x50|0x0C|0x000800031002000000114988|*Unknown Structure*|See below|
|0x5C|0x0C|0x00090003100200000011498C|*Unknown Structure*|See below|

These *Unknown Structures* are 96 bit long data structures that link currently unknown data to the model header. They are structured as follows:

|Offset|Length|Example|Name|Notes|
|---|---|---|---|---|
|0x00|0x04|0x00020004|Identifier?|0x00080003 - UV Coordinates (see UV below)<br>0x00090003 - Bump Texture UV Coordinates?|
|0x04|0x01|0x10|Inter-value Distance|The distance between two consecutive values|
|0x05|0x01|0x03|*Unknown*||
|0x06|0x01|0x00|Data Location Flag|- 0x00 - Data in VRAM<br>- 0x01 - Data in NGP|
|0x07|0x01|0x00|*Unknown*||
|0x08|0x04|0x00114980|Data Offset|Absolute address of the data|

### Model Header Type 2 - Rigged Mesh

|Offset|Length|Example|Name|Notes|
|---|---|---|---|---|
|0x00|0x04|0x00000002|Magic Number||
|0x24|0x04|0x00023B1C|Vertex Relative Pointer||
|0x44|0x04|0x00028100|Face Offset||

### UV Coordinates

The UV coordinates seem to be centred around 0x3800 (ie (0x3800, 0x3800) is
(0.5, 0.5)). However, they're not linear, with the following transformation
happening:

|Raw Coordinate Data|Texture Space Coordinate|
|---|---|
|0x17DD|Approaching 0|
|0x3800|0.5|
|0x3C1A|Approaching 1|

The following function seems to work well enough for what I've tested...

```python
def translate(val):
        return (((val / 0x3800) ** 10) / 2)
```
