import ctypes
from typing import Union
import numpy as np

# # Load the shared library
# lib_hamming = ctypes.CDLL('./hamming-codec/libhamming_wrapper.so')

# # Specify the argument types and the return type of the encode function
# lib_hamming.encode_hamming.argtypes = [ctypes.c_uint64, ctypes.c_uint32, ctypes.c_char_p]
# lib_hamming.encode_hamming.restype = ctypes.c_uint64

# # Specify the argument types and the return type of the decode function
# lib_hamming.decode_hamming.argtypes = [ctypes.c_uint64, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32]
# lib_hamming.decode_hamming.restype = ctypes.c_uint64

# Now you can call these functions from Python
# input_data = 81985529216486895
# n_bits = 128
parity_loc_str = "DEFAULT".encode('utf-8')
byte_max = {1:2,2:3,3:4,4:5} #ecc_intervalごとのECC付与後byteのサイズ

# encoded = lib_hamming.encode_hamming(input_data, n_bits, parity_loc_str)
# print(f"Encoded: {bin(encoded)}")
# print(type(encoded))

# decoded = lib_hamming.decode_hamming(encoded, n_bits, parity_loc_str, 0)
# print(f"Decoded: {hex(decoded)}")


def int2bin(data, n_bits):
    return np.binary_repr(data, n_bits)

def n_parity_bits_required(n_bits):
    p = 1
    while True:
        if 2 ** p >= p + n_bits + 1:
            break
        p += 1
    return p

def compute_parity_bit_positions(n_parity_bits):
    return [2**i - 1 for i in range(n_parity_bits)]

def compute_parity_bits(binary_string, parity_bit_positions):
    binary_string = np.array(list(binary_string), dtype=int)
    parity_bits = []
    for pos in parity_bit_positions:
        mask = pos + 1
        parity_bits.append(np.sum(binary_string[pos::mask]) % 2)
    return parity_bits

def encode(data, n_bits):
    binary_string = int2bin(data, n_bits)
    binary_string = binary_string[::-1]
    n_parity_bits = n_parity_bits_required(n_bits)
    parity_bit_positions = compute_parity_bit_positions(n_parity_bits)
    encoded_message = list(binary_string)
    for pos in parity_bit_positions:
        encoded_message.insert(pos, 'x')
    parity_bits = compute_parity_bits(encoded_message, parity_bit_positions)
    for pos, bit in zip(parity_bit_positions, parity_bits):
        encoded_message[pos] = str(bit)
    return ''.join(encoded_message[::-1])

def decode(encoded_data, n_bits):
    n_parity_bits = n_parity_bits_required(n_bits)
    parity_bit_positions = compute_parity_bit_positions(n_parity_bits)
    parity_bits = compute_parity_bits(encoded_data, parity_bit_positions)
    error_position = int(''.join(map(str, parity_bits[::-1])), 2)
    if error_position > 0:
        encoded_data = list(encoded_data)
        encoded_data[error_position - 1] = str(1 - int(encoded_data[error_position - 1]))
    decoded_data = [bit for pos, bit in enumerate(encoded_data) if pos not in parity_bit_positions]
    return ''.join(decoded_data[::-1])



def add_humming_ecc(datas = Union[np.uint8,int],ecc_interval = 4):
  res = []
  parity_loc_str = "DEFAULT".encode('utf-8')
  for d in datas:
    splited = [d[i:i+ecc_interval] for i in range(0, len(d), ecc_interval)]
    added_ecc = []
    for s in splited:
      # added = hamming_codec.encode(int.from_bytes(bytearray(np.array(s,dtype=np.uint8)),'big'),ecc_interval * 8)
      # added = lib_hamming.encode_hamming(int.from_bytes(bytearray(np.array(s,dtype=np.uint8)),'big'),ecc_interval * 8,parity_loc_str)
      added = encode(int.from_bytes(bytearray(np.array(s,dtype=np.uint8)),'big'),ecc_interval * 8)
      added = int(added,2)
      intnized = []
      # added_ecc.append(int(added,2))
      added_ecc.append(added)
    res.append(added_ecc)
  return np.array(res)

def max_uint(n_bytes):
    return 2 ** (8 * n_bytes) - 1

def correct_error_and_decode(datas = Union[np.uint8,int],ecc_interval = 4):
  res = []
  parity_loc_str = "DEFAULT".encode('utf-8')
  # print(datas)
  for d in datas:
    splited = [d[i:i+byte_max[ecc_interval]] for i in range(0, len(d), byte_max[ecc_interval])]
    ibyte = np.array([],dtype=np.uint8)
    for s in splited:
      # print("s",s)
      if int.from_bytes(bytearray(s),'big') > max_uint(byte_max[ecc_interval]):
        continue
      # di = lib_hamming.decode_hamming(int.from_bytes(bytearray(s),'big'),len(s)*8,parity_loc_str,0)
      di = decode(int.from_bytes(bytearray(s),'big'))
      di = int(di,2)
      # print("di",di)
      if di > max_uint(ecc_interval):
        continue
      ibyte = np.r_["-1",ibyte,np.frombuffer(int(di).to_bytes(ecc_interval,'big'),dtype=np.uint8)]
    res.append(ibyte)
  return res

def test():
    for i in range(256):
        encoded = encode(i, 8)
        decoded = decode(encoded, len(encoded))
        assert int(decoded, 2) == i, f"Decoding failed: {i} != {int(decoded, 2)}"

test()

# test_b = np.array([np.array([255,255,255,255,255]),np.array([255,255,255,255,255])])
# # it = int.from_bytes(bytearray(np.array([255,255,255,255,255],dtype=np.uint8)),'big')
# # print(it)
# # bin = bytearray(it.to_bytes(5,'big'))
# # print(np.array(bin,dtype=np.uint8))
# encoded = (add_humming_ecc(test_b,3))
# print(encoded)
# for ei in encoded[0]:
#   print(np.array(bytearray(int(ei).to_bytes(5,'big')),dtype=np.uint8))
