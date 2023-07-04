from tdt import TdT
import numpy as np
import hamming
from typing import Union,List
from dna_transcoder import DNATranscoder
from encoder_base import EncoderBase
from hamming_encoder import HammingEncoder
import pandas as pd
from hamming_decoder import HammingDecoder
from error_counter import ErrorCounter
from rs_encoder import RSEncoder
from rs_decoder import RSDecoder

# tb = ['A','G','C','T']
# tdt = TdT(tb,3,0,0.2,0)
# print(tdt.synthesis())

def read_file_and_separate_data_each_oligo(file_path:str,bytes_per_oligo:int):
  with open(file_path,'rb') as f:
      bdata = np.fromfile(f,dtype=np.dtype(np.uint8))
      s_data = [bdata[i:i+bytes_per_oligo] for i in range(0, len(bdata), bytes_per_oligo)]      
  added = []
  for i,s in enumerate(s_data):
      added.append(bytes_per_oligo - len(s))
      s_data[i] = np.array(list(s_data[i]) + list([0]*(bytes_per_oligo - len(s))))
  return s_data,added,bdata #分割&ゼロ埋めされたdata([uint8]),0埋めしたbyte


def assemble_saparated_data(data:List):
  saparated_with_meta_add_data = []
  for d in data:
    s = (d[:4:],d[4:4+d[0]:],d[4+d[0]::]) if d[2] == 0 else (d[:4:],d[4:4+d[0]:],d[4+d[0]:len(d) - d[2]:])
    saparated_with_meta_add_data.append(s)
    sorted_by_address = sorted(saparated_with_meta_add_data,key= lambda x:tuple(x[1]))
    rawdata = []
    for st in sorted_by_address:
      rawdata.append(list(st[2]))
  return saparated_with_meta_add_data,sum(rawdata,[])

# def to_trit_bytes(ns = Union[np.uint8,int]) -> np.array:
#   trits = []
#   for n in ns :
#     trit = np.base_repr(n,3)
#     trits.append(np.r_["-1",[0]*(6-len(str(trit))),np.array(list(str(trit)),dtype=np.uint8)])
#   return np.array(trits,dtype=np.uint8)

# def trits_bytes_to_ints(trits =Union[np.uint8,int]):
#   ints = []
#   remainder = len(trits) % 6
#   trits = trits[:len(trits) - remainder:]
#   split_as_byte = np.split(trits,len(trits)/6)
#   for byte in split_as_byte:
#     ints.append(int("".join(list(map(str,byte))),3))
#   return np.array(ints,dtype=np.uint8)

# def trits_list_bytes_to_ints(trit_list:[Union[np.uint8,int]]):
#   bytes_ = []
#   for ts in trit_list:
#     bytes_.append(trits_bytes_to_ints(ts))
#   return np.array(bytes_,dtype=np.uint8)

def build_consensus_base(bases:List,trim_margin:int = 0):
  avg = np.round(np.average(list(map(lambda x:len(x),bases))))
  df = pd.DataFrame(bases)
  mode = df.mode().iloc[0].tolist()
  return mode[:int(avg+trim_margin):],avg


byte_max = {1:2,2:3,3:4,4:5}
ecc_int = 4
s_data,added,bdata = read_file_and_separate_data_each_oligo('1k_data',15)
encoded = hamming.add_humming_ecc(s_data,ecc_int)
byted = bytearray()
for ed in encoded:
  for e in ed:
    byted = byted + bytearray(int(e).to_bytes(byte_max[ecc_int],'big'))

byte_int = np.array(byted,dtype=np.uint8) #ECC付与後の生のバイナリ(int)

transcoder = DNATranscoder()

# encoded_base = transcoder.encode(byte_int)

# print(encoded_base)

encoded_base = ['A','A','A','A','T','T','T','T','G','G','G','G','T','A','C','A','G','A','A','A','T','T','T','T','G','G','G','G','T','A','C','A']

decoded_byte_ints = transcoder.decode(encoded_base)

# print(decoded_byte_ints)



# trit_bytes = to_trit_bytes(byte_int).flatten()
# print(np.array(list(trit_bytes)+[9]))
# r_byte_int = trits_bytes_to_ints(np.array(list(trit_bytes)+[0,2,1,1,1,2],dtype=np.uint8))

# #print(trit_bytes.flatten()[3])
# print(byte_int)
# print(r_byte_int)

# cb = EncoderBase('1k_data',15,4,4)
# idd = cb.get_identified_data(9)
# spd,sumd = assemble_saparated_data(idd)
# print(idd)

# hc = HammingEncoder('1k_data',15,4,1)
rc = RSEncoder('1k_data',15,4,5)
ecced = rc.encode()


dt = DNATranscoder()
bases = []
for e in ecced:
  bases.append(dt.encode(e))

dcs = []
for b in bases:
  dcs.append(dt.decode(b))



# hd = HammingDecoder(15,4,1)
rd = RSDecoder(15,4,5)
decoded = rd.decode(dcs)
# print(decoded)
ec = ErrorCounter(rc.ref,rd.for_error_check)
print(ec.count_error())
# print(decoded)




# dc = dt.decode(bases[0])
# print(dc)
# afterd = hamming.correct_error_and_decode([dc])
# print(afterd)

# print(int(34421704871).to_bytes(5,'big'))



# d = [0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# splited = [d[i:i+4] for i in range(0, len(d), 4)]
# # print(splited)

# print(int.from_bytes(bytearray([255,255,255,255]),'big'))
# bt = int(4294967295).to_bytes(4,'big')
# npis = np.frombuffer(bt,dtype=np.uint8)
# npis2 = np.array([0,0,0,0,0],dtype=np.uint8)
# print(np.r_["-1",npis,npis2])

ba = ['A','T','G','C','A','T','G','C','A','T','G','C']
bb = ['A','T','G','C','A','T','G','C','A','T','G','C']
bc = ['T','T','G','C','A','T','G','C','A','T','G','C','G']
bd = ['T','T','G','C','A','T','G','C','A','T','G','C']
be = ['T','T','G','C','A','T','G','C','A','T','G','C']

# print(build_consensus_base([ba,bb,bc,bd,be],0))

