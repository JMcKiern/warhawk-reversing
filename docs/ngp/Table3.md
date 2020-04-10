# Table 3 (T3)

Offset | Length | Example | Name | Notes
-- | -- | -- | -- | --
0x00 | 0x02 | 0x0006 | Number of entries in T3.0 table |
0x02 | 0x02 | 0x000d | Number of entries in table | 
0x04 | 0x04 | 0xFFFFFFE4 | Pointer to T3.0 Table | Relative pointer
0x08 + (n * 0x04) | 0x04 | 0xFFFFF87C | Entry in table | Relative pointer to T3.1 data

## Table 3.1 Data (T3.1.D)
