import base64
import struct
import zlib

def decode_base64_to_image(encoding: str):
    content = encoding.split(";")[1]
    image_encoded = content.split(",")[1]

    return base64.b64decode(image_encoded)

def decompress_png(f):
    PngSignature = b'\x89PNG\r\n\x1a\n'
    if f.read(len(PngSignature)) != PngSignature:
        raise Exception('Invalid PNG Signature')

    def read_chunk(f):
        # Returns (chunk_type, chunk_data)
        chunk_length, chunk_type = struct.unpack('>I4s', f.read(8))
        chunk_data = f.read(chunk_length)
        checksum = zlib.crc32(chunk_data, zlib.crc32(struct.pack('>4s', chunk_type)))
        chunk_crc, = struct.unpack('>I', f.read(4))
        if chunk_crc != checksum:
            raise Exception('chunk checksum failed {} != {}'.format(chunk_crc,
                checksum))
        return chunk_type, chunk_data

    chunks = []
    while True:
        chunk_type, chunk_data = read_chunk(f)
        chunks.append((chunk_type, chunk_data))
        if chunk_type == b'IEND':
            break

    #print([chunk_type for chunk_type, chunk_data in chunks])

    _, IHDR_data = chunks[0] # IHDR is always first chunk
    width, height, bitd, colort, compm, filterm, interlacem = struct.unpack('>IIBBBBB', IHDR_data)

    if compm != 0:
        raise Exception('invalid compression method')
    if filterm != 0:
        raise Exception('invalid filter method')

    if colort != 6:
        raise Exception('we only support truecolor with alpha')
    if bitd != 8:
        raise Exception('we only support a bit depth of 8')
    if interlacem != 0:
        raise Exception('we only support no interlacing')

    #print(width, height)

    IDAT_data = b''.join(chunk_data for chunk_type, chunk_data in chunks if chunk_type == b'IDAT')

    IDAT_data = zlib.decompress(IDAT_data)
    #print(len(IDAT_data))

    def PaethPredictor(a, b, c):
        p = a + b - c
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        if pa <= pb and pa <= pc:
            Pr = a
        elif pb <= pc:
            Pr = b
        else:
            Pr = c
        return Pr

    Recon = []

    bytesPerPixel = 4
    stride = width * bytesPerPixel

    def Recon_a(r, c):
        return Recon[r * stride + c - bytesPerPixel] if c >= bytesPerPixel else 0

    def Recon_b(r, c):
        return Recon[(r-1) * stride + c] if r > 0 else 0

    def Recon_c(r, c):
        return Recon[(r-1) * stride + c - bytesPerPixel] if r > 0 and c >= bytesPerPixel else 0

    i = 0
    for r in range(height): # for each scanline
        filter_type = IDAT_data[i] # first byte of scanline is filter type
        i += 1
        for c in range(stride): # for each byte in scanline
            Filt_x = IDAT_data[i]
            i += 1
            if filter_type == 0: # None
                Recon_x = Filt_x
            elif filter_type == 1: # Sub
                Recon_x = Filt_x + Recon_a(r, c)
            elif filter_type == 2: # Up
                Recon_x = Filt_x + Recon_b(r, c)
            elif filter_type == 3: # Average
                Recon_x = Filt_x + (Recon_a(r, c) + Recon_b(r, c)) // 2
            elif filter_type == 4: # Paeth
                Recon_x = Filt_x + PaethPredictor(Recon_a(r, c), Recon_b(r, c), Recon_c(r, c))
            else:
                raise Exception('unknown filter type: ' + str(filter_type))
            Recon.append(Recon_x & 0xff) # truncation to byte

    return bytes(Recon)