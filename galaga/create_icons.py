import zlib
import struct
import os

def write_png(width, height):
    # PNG signature
    png = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    # width(4), height(4), bit depth(1), color type(1, 2=RGB), compression(1), filter(1), interlace(1)
    ihdr_data = struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0)
    png += struct.pack('!I', len(ihdr_data)) + b'IHDR' + ihdr_data + struct.pack('!I', zlib.crc32(b'IHDR' + ihdr_data))
    
    # IDAT chunk
    raw_data = b""
    for y in range(height):
        raw_data += b'\x00' # filter type 0
        for x in range(width):
            # Coordinates relative to center (-1.0 to 1.0)
            nx = (x - width / 2) / (width / 2)
            ny = (y - height / 2) / (height / 2)
            
            is_ship_yellow = False
            is_ship_red = False
            is_ship_white = False
            
            # Simple arcade ship pixel calculation
            if abs(nx) < 0.6 and 0.1 < ny < 0.4 and abs(nx) > 0.3:
                is_ship_white = True
            elif abs(nx) < 0.25 and abs(ny) < 0.5:
                is_ship_yellow = True
            elif abs(nx) < 0.12 and -0.7 < ny <= -0.5:
                is_ship_red = True
            elif abs(nx) < 0.5 and abs(nx) > 0.4 and 0.0 < ny < 0.2:
                is_ship_red = True
                
            if is_ship_red:
                raw_data += b'\xff\x00\x00' # Red
            elif is_ship_yellow:
                raw_data += b'\xff\xcc\x00' # Retro Yellow
            elif is_ship_white:
                raw_data += b'\xff\xff\xff' # White
            else:
                raw_data += b'\x00\x00\x00' # Transparent/Black
                
    compressor = zlib.compressobj()
    compressed = compressor.compress(raw_data) + compressor.flush()
    png += struct.pack('!I', len(compressed)) + b'IDAT' + compressed + struct.pack('!I', zlib.crc32(b'IDAT' + compressed))
    
    # IEND chunk
    png += struct.pack('!I', 0) + b'IEND' + struct.pack('!I', zlib.crc32(b'IEND'))
    return png

dest_dir = '/home/yjlee/dev/games/galaga/'
os.makedirs(dest_dir, exist_ok=True)

with open(os.path.join(dest_dir, 'icon-192.png'), 'wb') as f:
    f.write(write_png(192, 192))
    
with open(os.path.join(dest_dir, 'icon-512.png'), 'wb') as f:
    f.write(write_png(512, 512))

print("PWA icon-192.png and icon-512.png created successfully in /home/yjlee/dev/games/galaga/")
