#include <std/ptr>
#include <std/io>
#include <std/core>
std::core::set_endian(std::mem::Endian::Big); // the pragma not working for some reason


struct RelPtr<T> {
    T* p : s32 [[pointer_base("std::ptr::relative_to_pointer")]];
};

struct NgpRttHeader {
    u8 compression_method;
    u8 data_location_flag;
    u16 image_format;
    u16 width;
    u16 height;
    u8 data_in_ngp;
    u8 unknown1;
    u8 number_of_mipmaps;
    u8 unknown2;
    s32 pointer;
};

struct PointerTable<T> {
    u32 num_ptrs;
    RelPtr<T> ptrs[num_ptrs];
};

struct Face {
    u16 vertex_indices[3];
};

struct Vertex {
    u16 x,y,z;
};


struct ModelLevel0 {
    u32 magic_number;
    if (magic_number != 1) break;
    u32 ptr;
    u32 unknown0;
    u32 unknown1;
    u32 unknown2;
    u32 unknown3;
    u32 unknown4;
    u32 number_of_face_indices;
    u32 unknown5;
    u16 number_of_vertices;
    u8 number_of_linkers;
    u8 unknown6;
    Face* faces[number_of_face_indices / 3] : s32;
    u32 unknown7;
    u32 unknown8;
    Vertex* vertices[number_of_vertices] : s32;
    u96 unknown_structure0;
    u96 unknown_structure1;
};

struct ModelLevel0A {
    u128 unknown0;
    u128 unknown1;
    u128 unknown2;
    u128 unknown3;
};

struct ModelLevel1 {
    u128 unknown4;
    u128 unknown5;
    RelPtr<ModelLevel0A> unknown6;
    std::print("{:x}", addressof(this));
    std::print("{:x}", addressof(parent));
    //RelPtr<ModelLevel0> m;
    u32 unknown7;
    u32 unknown8;
};

struct ModelLevel2 {
    u32 unknown0;
    u32 unknown1;
    u32 unknown2;
    RelPtr<ModelLevel1> m1[1]; // idk what specifies this length
};

struct ModelLevel3 {
    u32 unknown0;
    u32 unknown1;
    u32 unknown2;
    u32 unknown3;
    RelPtr<ModelLevel2> m2; // idk what specifies this length
};

struct ModelLevel4 {
    u8 unknown0;
    u8 num_entries0;
    u8 unknown1;
    u8 unknown2;
    u32 unknown3;
    u32 unknown4;
    RelPtr<u32> unknown5[num_entries0];
    u8 unknown6;
    u8 num_entries1;
    u8 unknown7;
    u8 unknown8;
    u32 unknown9;
    RelPtr<ModelLevel3> m3[num_entries1];
};

struct ModelLevel5 {
    u32 unknown0;
    u32 unknown1;
    RelPtr<ModelLevel4> m4;
};

struct ModelLevel6 {
    u32 unknown0;
    u32 unknown1;
    u32 unknown2;
    RelPtr<ModelLevel5> m5;
};

struct Ngp {
    u32 id;
    u32 unk0;
    u32 unk1;
    
    RelPtr<PointerTable<ModelLevel6>> t1_ptr;
    RelPtr<PointerTable<NgpRttHeader>> texture_table_ptr;
    RelPtr<u32> t3_ptr;
    RelPtr<u32> t4_ptr;
    RelPtr<u32> t5_ptr;
};


Ngp ngp @ 0x0;

RelPtr<ModelLevel1> m0 @ 0x914;
//RelPtr<ModelLevel1> m1 @ 0x918;
//ModelLevel4 m4 @ 0xc50;
//ModelLevel6 m @ 0xc90;
//RelPtr<u32> mp0 @ 0x978;
//RelPtr<ModelLevel3> mp1 @ 0xc68;

//RelPtr<u32> p0 @ 0xc9c;
