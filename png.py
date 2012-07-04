import array
import struct
import zlib


def output_chunk(out, chunk_type, data):
    out.write(struct.pack("!I", len(data)))
    out.write(chunk_type)
    out.write(data)
    checksum = zlib.crc32(data, zlib.crc32(chunk_type))
    out.write(struct.pack("!i", checksum))


def get_data(width, height, pixels):
    compressor = zlib.compressobj()
    data = array.array("B")
    for y in range(height):
        data.append(0)
        for x in range(width):
            r, g, b = pixels.get((x, y), (0, 0, 0))
            data.extend([r, g, b])
    compressed = compressor.compress(data.tostring())
    flushed = compressor.flush()
    return compressed + flushed


def output_png(filename, width, height, pixels):
    out = open(filename, "wb")
    out.write(struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10))
    output_chunk(out, b"IHDR", struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0))
    output_chunk(out, b"IDAT", get_data(width, height, pixels))
    output_chunk(out, b"IEND", b"")
    out.close()
