# WarHawk Reversing

Some scripts to reverse the file formats used in [WarHawk](https://en.wikipedia.org/wiki/Warhawk_(2007_video_game)).

The ultimate goal of this project is to end up with a collection of scripts that can convert the custom file formats into common formats (eg .obj, .dds). The emphasis is on the texture and model formats (.rtt and .ngp).

## File Formats

Within the psarc, the file formats used are as follows:
- [.rtt](docs/RTT.md) - Basically a DDS with a custom header
- .vram - Multiple textures
- .ngp - Stores some texture data, the model data and presumably some others (animation, normal maps, uv maps etc.)
- .ptr - Has list of location for various model header and textures
- .dat - content.dat or external_paths.dat
- .loc - Localisation files (these seem to be in UTF-16 Big Endian)
- .fbin - Compiled fragment shaders
- .vbin - Compiled vertex shaders
- .twk - Config (tweak) files (eg reload time for jeep machine gun)
- .tvm3 - Seems to define the game modes on a specific map

## How To Use

### rtt2dds

.rtt files can be converted to .dds files with rtt2dds.py. Simply pass the path of the .rtt file to the script:
```
./rtt2dds.py /path/to/sample_texture.rtt
```
This will create a sample_texture.dds file in the same path as the .rtt file. The .rtt files can also be dragged and dropped on to the rtt2dds.py script.

There is a `--permissive` mode that can be used to bypass the checks that validate the .rtt file.

```
./rtt2dds.py --permissive /path/to/sample_texture1.rtt
```

## Contributing

Any help would be much appreciated.  
Feel free to open an issue or pr.
