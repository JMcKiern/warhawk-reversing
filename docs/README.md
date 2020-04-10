# Documentation

These files contain what has been reversed so far for the various formats.

## Notes

There are some important points that should be made regarding all of the files.

### Endianness

The files are all big endian.

### Relative pointer

The term relative pointer is used extensively in this documentation. It refers
to a pointer that describes the relative offset from that pointer to the
destination. For example, a relative pointer with value 0x10 at location 0x4
would point to 0x14.
