import numpy as np

def hamming_decode(encoded_data):
    encoded_data = np.array(list(encoded_data), dtype=int)
    r = int(np.log2(encoded_data.size))
    parity_bits = [np.sum(encoded_data[np.arange(2**i, encoded_data.size, 2**(i+1))]) % 2 for i in range(r)]
    error_bit = np.sum([2**i if parity_bits[i] != encoded_data[2**i] else 0 for i in range(r)])
    if error_bit != 0:
        encoded_data[error_bit - 1] ^= 1
    decoded_data = np.delete(encoded_data, [2**i for i in range(r)])
    return ''.join(map(str, decoded_data))

encoded_data = '01001001'
print('Decoded Data is:', hamming_decode(encoded_data))