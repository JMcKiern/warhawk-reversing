import struct

def int32_to_bytes(number):
    return struct.pack("<I", number)

def get_img_data_size(width, height, num_mipmaps, bytes_per_pixel, bytes_per_group):
    return int(sum([max(bytes_per_pixel * width * height * ((1/(2.0 ** i)) ** 2), bytes_per_group) for i in range(0, num_mipmaps)]))
