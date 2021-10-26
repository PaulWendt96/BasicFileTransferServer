import math
import struct

def break_stream(stream, size=4096):
    ''' Break an iterable into <size> sized chunks
        When a chunk is requested, yield a 3-tuple representing: 
         
          - the chunk itself (chunk)
          - the size of the chunk
          - the number of chunks remaining
    '''
    stream_length = len(stream)
    if not stream_length:
        raise ValueError("Empty Stream")

    chunks_to_send = math.ceil(stream_length / size)
    i = 0
    while chunks_to_send:
        chunk = stream[i * size: (i + 1) * size]
        chunks_to_send -= 1
        i += 1
        stream_size = size if chunks_to_send else len(chunk)
        yield chunk, stream_size, chunks_to_send
