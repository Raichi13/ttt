import ctypes
from typing import Union
import numpy as np

# Load the shared library
lib_hamming = ctypes.CDLL('./hamming-codec/libhamming_wrapper.so')

# Specify the argument types and the return type of the encode function
lib_hamming.encode_hamming.argtypes = [ctypes.c_uint64, ctypes.c_uint32, ctypes.c_char_p]
lib_hamming.encode_hamming.restype = ctypes.c_uint64

# Specify the argument types and the return type of the decode function
lib_hamming.decode_hamming.argtypes = [ctypes.c_uint64, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32]
lib_hamming.decode_hamming.restype = ctypes.c_uint64

# Now you can call these functions from Python
# input_data = 81985529216486895
n_bits = 128
parity_loc_str = "DEFAULT".encode('utf-8')
byte_max = {1:2,2:3,3:4,4:5} #ecc_intervalごとのECC付与後byteのサイズ

# encoded = lib_hamming.encode_hamming(input_data, n_bits, parity_loc_str)
# print(f"Encoded: {bin(encoded)}")
# print(type(encoded))

# decoded = lib_hamming.decode_hamming(encoded, n_bits, parity_loc_str, 0)
# print(f"Decoded: {hex(decoded)}")


def add_humming_ecc(datas = Union[np.uint8,int],ecc_interval = 4):
  res = []
  parity_loc_str = "DEFAULT".encode('utf-8')
  for d in datas:
    splited = [d[i:i+ecc_interval] for i in range(0, len(d), ecc_interval)]
    added_ecc = []
    for s in splited:
      # added = hamming_codec.encode(int.from_bytes(bytearray(np.array(s,dtype=np.uint8)),'big'),ecc_interval * 8)
      added = lib_hamming.encode_hamming(int.from_bytes(bytearray(np.array(s,dtype=np.uint8)),'big'),ecc_interval * 8,parity_loc_str)
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
  print(datas)
  for d in datas:
    splited = [d[i:i+byte_max[ecc_interval]] for i in range(0, len(d), byte_max[ecc_interval])]
    ibyte = np.array([],dtype=np.uint8)
    for s in splited:
      # print("s",s)
      di = lib_hamming.decode_hamming(int.from_bytes(bytearray(s),'big'),len(s)*8,parity_loc_str,0)
      if di > max_uint(ecc_interval):
        continue
      ibyte = np.r_["-1",ibyte,np.frombuffer(int(di).to_bytes(ecc_interval,'big'),dtype=np.uint8)]
    res.append(ibyte)
  return res



# test_b = np.array([np.array([255,255,255,255,255]),np.array([255,255,255,255,255])])
# # it = int.from_bytes(bytearray(np.array([255,255,255,255,255],dtype=np.uint8)),'big')
# # print(it)
# # bin = bytearray(it.to_bytes(5,'big'))
# # print(np.array(bin,dtype=np.uint8))
# encoded = (add_humming_ecc(test_b,3))
# print(encoded)
# for ei in encoded[0]:
#   print(np.array(bytearray(int(ei).to_bytes(5,'big')),dtype=np.uint8))
