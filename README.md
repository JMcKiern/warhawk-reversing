# WarHawk Reversing

Some scripts to reverse the file formats used in [WarHawk](https://en.wikipedia.org/wiki/Warhawk_(2007_video_game)).

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

## Contributing

Any help would be much appreciated.
