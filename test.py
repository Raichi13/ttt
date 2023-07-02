# -*- coding: utf-8 -*-

import itertools
import numpy as np
import pandas as pd
from typing import Union
import hamming_codec
from reedsolo import RSCodec,ReedSolomonError
import random
from multiprocessing import Pool

#Trit(e.g. [1,2,0,0,1,2,2,0]) → ['A','T','G','C','G','C','G','C','G','C']
def trits_to_dna_bases(trits = Union[np.uint8,int],origin_base:str = 'A') :
  # print(type(trits[0]))
  # print(trits[0])
  bases:[str] = [origin_base]
  mapper = {
      'A' : {0:'G',1:'C',2:'T'},
      'C' : {0:'T',1:'G',2:'A'},
      'G' : {0:'A',1:'T',2:'C'},
      'T' : {0:'C',1:'A',2:'G'}
  }
  for i,t in enumerate(trits):
    bases.append(mapper[bases[i]][t])
  return bases

#['A','T','G','C','G','C','G','C','G','C'] → Trit(e.g. [1,2,0,0,1,2,2,0])
def dna_bases_to_trits(bases_:[str]) :
  trits = []
  mapper = {
      'A' : {'G':0,'C':1,'T':2},
      'C' : {'T':0,'G':1,'A':2},
      'G' : {'A':0,'T':1,'C':2},
      'T' : {'C':0,'A':1,'G':2}
  }
  for i,b in enumerate(bases_):
    if i == len(bases_) - 1 : break
    if bases_[i + 1] == b : continue
    trits.append(mapper[b][bases_[i + 1]])
  return np.array(trits,dtype=np.uint8)

# int → trits([1,2,0,1,0,2...])
# (byte[1,0,1,0,1,0,1,0]) → int[170] →  trits[0,2,0,0,2,2]
def to_trit_bytes(ns = Union[np.uint8,int]) -> np.array:
  trits = []
  for n in ns :
    trit = np.base_repr(n,3)
    trits.append(np.r_["-1",[0]*(6-len(str(trit))),np.array(list(str(trit)),dtype=np.uint8)])
  return np.array(trits,dtype=np.uint8)

# to_trit_bytesのまとめて版
def bytes_list_to_trit_bytes(ns_list = [Union[np.uint8,int]]):
  trit_bytes = []
  for ns in ns_list:
    trit_bytes.append(to_trit_bytes(ns).flatten())
  return np.array(trit_bytes,dtype=np.uint8)

# trits[0,2,0,0,2,2] → int[170] (byte[1,0,1,0,1,0,1,0])
def trits_bytes_to_ints(trits =Union[np.uint8,int]):
  ints = []
  remainder = len(trits) % 6
  trits = trits[:len(trits) - remainder:]
  split_as_byte = np.split(trits,len(trits)/6)
  for byte in split_as_byte:
    ints.append(int("".join(list(map(str,byte))),3))
  return np.array(ints,dtype=np.uint8)

def trits_list_bytes_to_ints(trit_list:[Union[np.uint8,int]]):
  bytes_ = []
  for ts in trit_list:
    bytes_.append(trits_bytes_to_ints(ts))
  return np.array(bytes_,dtype=np.uint8)


def to_trits(n:np.uint8):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % 3))
        n //= 3
    return digits[::-1]
    
def ints_to_trits_hummig(ints,max:int) : #uint8の配列をtritの配列に
  r = []
  for i in ints : 
    t = to_trits(i)
    t = ([0] * (max - len(t))) + t
    r.append(t)
  return np.array(np.array(r).flatten(),dtype=np.uint8)


def trits_to_binaries_hummig(trits,trit_max,bit_max) :
  r = []
  trits_blocks = [trits[idx:idx + trit_max] for idx in range(0,len(trits), trit_max)]
  for b in trits_blocks :
    maped = map(str, b)
    bin_str = bin(int("".join(maped),3))
    if (len(bin_str) - 2) < bit_max :
      zeros = bit_max - (len(bin_str) - 2)
      bin_str = bin_str[:2] + ('0' * zeros) + bin_str[2:]
    r.append(bin_str)
  return r

#trits([1,2,0,1,0,2...]) → int 
def trits_to_int(trits:[int]):
    s:str = ''
    for t in trits:
        s += str(t)
    return int(s,3)

def read_file_and_separate_data_each_oligo(file_path:str,bytes_per_oligo:int):
  with open(file_path,'rb') as f:
      bdata = np.fromfile(f,dtype=np.dtype(np.uint8))
      s_data = [bdata[i:i+bytes_per_oligo] for i in range(0, len(bdata), bytes_per_oligo)]      
  added = []
  for i,s in enumerate(s_data):
      added.append(bytes_per_oligo - len(s))
      s_data[i] = np.array(list(s_data[i]) + list([0]*(bytes_per_oligo - len(s))))
  return s_data,added,bdata #分割&ゼロ埋めされたdata([uint8]),0埋めしたbyte

def assemble_saparated_data(data:[]):
  saparated_with_meta_add_data = []
  for d in data:
    s = (d[:4:],d[4:4+d[0]:],d[4+d[0]::]) if d[2] == 0 else (d[:4:],d[4:4+d[0]:],d[4+d[0]:len(d) - d[2]:])
    saparated_with_meta_add_data.append(s)
    sorted_by_address = sorted(saparated_with_meta_add_data,key= lambda x:tuple(x[1]))
    rawdata = []
    for st in sorted_by_address:
      rawdata.append(list(st[2]))
  return saparated_with_meta_add_data,sum(rawdata,[])

# address_size(byte単位) -> [uint8,uint8,uint8,uint8]
def generate_address(address_size:int,max:int):
    res = []
    for i in range(max):
        a= list(np.binary_repr(i,width=8*address_size)[j:j+8] for j in range(0,8*address_size,8))
        res.append(np.array(list(map(lambda x:int(x,2),a))).astype(np.uint8))
    return np.array(res)

def generate_metadata(address_size:np.uint8,encode_type:np.uint8,free:[],length:int):
  return np.array([[address_size,encode_type,free[0],free[1]]]*length,dtype=np.uint8)

def identify_and_add_metadata(splited_data:np.array,address_size:np.uint8,encode_type:np.int8,free_aria = Union[np.uint8,int]):
    address = generate_address(address_size,len(splited_data))
    metadata = generate_metadata(address_size,encode_type,free_aria,len(splited_data))
    return np.r_["1",metadata,address,splited_data]

def identify_data(splited_data:np.array,address_size:np.uint8):
  return np.r_["1",generate_address(address_size,len(splited_data)),splited_data]

# [uint8(base = 10)] → 
def add_humming_ecc(datas = Union[np.uint8,int],ecc_interval = 4):
  res = []
  for d in datas:
    splited = [d[i:i+ecc_interval] for i in range(0, len(d), ecc_interval)]
    added_ecc = []
    for s in splited:
      added = hamming_codec.encode(int.from_bytes(bytearray(np.array(s,dtype=np.uint8)),'big'),ecc_interval * 8)
      intnized = []
      added_ecc.append(int(added,2))
    res.append(added_ecc)
  return np.array(res)

def add_rs_ecc(datas:[],symbol_size=10):
    rsc = RSCodec(symbol_size)
    res = []
    for d in datas:
      e = rsc.encode(list(d))
      res.append(np.frombuffer(e,dtype=np.uint8))
    return np.array(res)


def trits_to_binaries(trits,trit_max,bit_max) :
  r = []
  trits_blocks = [trits[idx:idx + trit_max] for idx in range(0,len(trits), trit_max)]
  for b in trits_blocks :
    maped = map(str, b)
    bin_str = bin(int("".join(maped),3))
    if (len(bin_str) - 2) < bit_max :
      zeros = bit_max - (len(bin_str) - 2)
      bin_str = bin_str[:2] + ('0' * zeros) + bin_str[2:]
    r.append(int(bin_str,2))
  return np.array(r,dtype=np.uint8)


def encode_humming(data:[],ecc_interval = 4,address_size = 4):
  trit_max = {1:8,2:14,3:19,4:24} #ecc_intervalごとのtritのmax桁数
  bit_max = {1:12,2:21,3:29,4:38} #ecc_intervalごとのECC付与後bitのmax桁数
  added_ecc = add_humming_ecc(data,ecc_interval)
  # for d in data:
  #   print(d)
  # added_ecc.append()
  trits_each_oligo = []
  for d in added_ecc:
    trits_each_oligo.append(ints_to_trits_hummig(d,trit_max[ecc_interval]))
  target_bases = []
  for t in trits_each_oligo:
    target_bases.append(trits_to_dna_bases(t))
  return target_bases

def encode_rs(data:[],symbol_size = 10):
  ecc_added = add_rs_ecc(data,symbol_size)
  trits_each_oligo = []
  # for e in ecc_added:
  #   trits_each_oligo.append(bytes_list_to_trit_bytes(e))
  trits_each_oligo = bytes_list_to_trit_bytes(ecc_added)
  # print(trits_each_oligo)
  target_bases = []
  for t in trits_each_oligo:
    target_bases.append(trits_to_dna_bases(t))
  return target_bases

def decode_humming(bases:[],ecc_interval = 4,address_size = 4):
  trit_max = {1:8,2:14,3:19,4:24} #ecc_intervalごとのtritのmax桁数
  bit_max = {1:12,2:21,3:29,4:38} #ecc_intervalごとのECC付与後bitのmax桁数
  trits = []
  for base in bases:
    trits.append(dna_bases_to_trits(base))
  decoded = []
  for t in trits:
    # print("trits")
    # print(t)
    decoded_bin = trits_to_binaries_hummig(t,trit_max[ecc_interval],bit_max[ecc_interval])
    # print(decoded_bin)
    humming_decoded = []
    for d in decoded_bin:
        print("before decode")
        print(d)
        id_ = int(d,2)
        print("id")
        dec = hamming_codec.decode(id_,len(d))
        print("dec")
        decoded_i = int(dec,2)
        print(decoded_i)
        print("after decode")
        if decoded_i > 4294967295: # try catchでやるとnumpyで二重メモリ解放が起きてカーネルが落ちるためベタ書きで例外処理
            print("exception")
            humming_decoded.append([255,255,255,255])
        else :
            bi = decoded_i.to_bytes(ecc_interval,"big")
            humming_decoded.append(list(np.frombuffer(bi,dtype=np.uint8)))
    #   try:
    #     humming_decoded.append(list(np.frombuffer(int(hamming_codec.decode(int(d,2),len(d)),2).to_bytes(ecc_interval,"big"),dtype=np.uint8)))
    #   except OverflowError as e:
    #     print("exception")
    #     humming_decoded.append([255,255,255,255])
    # print(humming_decoded[0][3])
    small_byte_size = humming_decoded[0][3] % ecc_interval
    # # print(humming_decoded[len(humming_decoded) - 1])
    if small_byte_size != 0:
      humming_decoded[len(humming_decoded) - 1] = humming_decoded[len(humming_decoded) - 1][4 - small_byte_size::]
    # print(humming_decoded)#flattenする
    decoded.append(sum(list(humming_decoded),[]))
  print("koko")
#   print(decoded)
  return np.array(decoded,dtype=np.uint8)
  # return decoded

def decode_rs(bases:[],symbol_size = 10):
  trits = []
  decode_error_count = 0
  for base in bases:
    trits.append(dna_bases_to_trits(base))
  decoded_ints = trits_list_bytes_to_ints(trits)
  decoded = []
  # print(np.shape(decoded))
  rsc = RSCodec(symbol_size)
  for di in decoded_ints:
    try:
      rscd = rsc.decode(bytearray(di))[0]
      decoded.append(np.frombuffer(rsc.decode(bytearray(di))[0],dtype=np.uint8))
    except ReedSolomonError as e:
      decode_error_count += 1
  return decoded,decode_error_count


# 重み付けされた排反な2つの事象の抽選関数(高速化のために2つの事象に限定して実装(listで渡すと遅い))
def weighted_random_exclusive(probability0:int,probability1:int):
#   r = np.random.rand()
  r = random.random()
  if r < probability0 :
    return 0
  elif r < probability0 + probability1 :
    return 1
  else:
    return -1

# 重み付けされた抽選関数
def weighted_random(probability:int):
#   return (np.random.rand() < probability)
    return (random.random() < probability)

def extension(base : str, cycle : int,miss_extension_probability : int,deletion_probability : int,over_extension_probability : int) :
  bases_list = ['A','G','C','T']
  r = []
  miss_extension_count = 0
  deletion_count = 0
  over_extension_count = 0
  for i in range(cycle):
    ext_base = base
    if weighted_random(miss_extension_probability):# 塩基ミス
      other_bases = [s for s in bases_list if base not in s]
      ext_base = other_bases[random.randint(0,2)]
      miss_extension_count += 1
    deletion_or_over = weighted_random_exclusive(over_extension_probability,deletion_probability)# 伸長失敗と過剰に伸長
    if deletion_or_over == -1 :# 正常に伸長
      r.append(ext_base)      
      continue
    if deletion_or_over == 0 : #過剰に伸長
      r.append(ext_base)
      r.append(ext_base)
      over_extension_count += 1
      continue
    if deletion_or_over == 1 : #欠損
      deletion_count += 1
      continue
  return r,miss_extension_count,deletion_count,over_extension_count

def synthesis_dna(bases : list,
                  reaction_cycle : int,
                  miss_extension_probability : int,
                  deletion_probability : int,
                  over_extension_probability : int) :
  synthesis_result = []
  miss_extension_count = 0
  deletion_count = 0
  over_extension_count = 0
  for b in bases :
    r,miss_extension_count_,deletion_count_,over_extension_count_ = extension(b,reaction_cycle,miss_extension_probability,deletion_probability,over_extension_probability)
    synthesis_result = synthesis_result + r
    miss_extension_count += miss_extension_count_
    deletion_count += deletion_count_
    over_extension_count += over_extension_count_
  return synthesis_result,miss_extension_count,deletion_count,over_extension_count

def build_consensus_base(bases:[],trim_margin:int = 0):
  avg = np.round(np.average(list(map(lambda x:len(x),bases))))
  df = pd.DataFrame(bases)
  mode = df.mode().iloc[0].tolist()
  return mode[:int(avg+trim_margin):],avg

def simulate(input_data_path_:str,
        address_size_:int,
        encode_type_:int,
        oligo_count_:int,
        reaction_cycle_ :int,
        miss_extension_probability_ : int,
        deletion_probability_ : int,
        over_extension_probability_ : int,
        ecc_param:int,
        trim_margin_:int = 0,
        bytes_per_oligo_ :int = 16):
        miss_extension_count_in_sim = deletion_count_in_sim = over_extension_count_in_sim = 0
        s_data,added,raw = read_file_and_separate_data_each_oligo(input_data_path_,bytes_per_oligo_) #ファイルを読み込みオリゴサイズごとに分割
        identified_data = identify_data(s_data,address_size_)#アドレス付与
        meta_data = np.stack([np.array([address_size_]*len(s_data),dtype=np.uint8),
                np.array([encode_type_]*len(s_data),dtype=np.uint8),
                np.array(added,dtype=np.uint8),
                np.array(([bytes_per_oligo_]*len(s_data)) if encode_type_ in [1,2,3,4] else ([ecc_param]*len(s_data)),dtype=np.uint8)],1)
        identified_and_added_meta_data = np.r_["1",meta_data,identified_data]
        max_address = identified_and_added_meta_data[len(identified_and_added_meta_data) - 1][4:4+address_size_:]
        
        target_bases = encode_humming(identified_and_added_meta_data,ecc_param) if encode_type_ in [1,2,3,4] else encode_rs(identified_and_added_meta_data,ecc_param)
        synthesis_res = []
        for tb in target_bases:
                sysnthesis_result_each_address = []
                for i in range(oligo_count_):        
                        results,mc,dc,oc = synthesis_dna(tb,reaction_cycle_,miss_extension_probability_,deletion_probability_,over_extension_probability_)
                        sysnthesis_result_each_address.append(results)
                        miss_extension_count_in_sim += mc
                        deletion_count_in_sim += dc
                        over_extension_count_in_sim += oc
                synthesis_res.append(sysnthesis_result_each_address)
        
        consensus_bases = []
        err_oligo_count = 0
        err_byte_count = 0
        for sr in synthesis_res:
                consensus_bases.append(build_consensus_base(sr,trim_margin_)[0])
        
        # print(len(consensus_bases))
        if encode_type_ in [1,2,3,4]:
                decoded_ = decode_humming(consensus_bases,ecc_param,address_size_)
        else :
                decoded_,rs_error = decode_rs(consensus_bases,ecc_param)
                err_oligo_count += rs_error
        print('decode complete')
        assembled_ref_data = assemble_saparated_data(identified_and_added_meta_data)[0]
        assembled_decoded_data = assemble_saparated_data(decoded_)[0]
        assembled_decoded_data = list(filter(lambda x:list(x[1]) <= list(max_address),assembled_decoded_data))
        for ad in assembled_ref_data:
                # print(assembled_decoded_data[0][1])
                # print(assembled_ref_data[0][1])
                read = list(filter(lambda x:list(x[1]) == list(ad[1]),assembled_decoded_data))
                if read == []:
                        err_byte_count += len(ad[2])
                else:
                        # print(ad[2])
                        # print(read[0][2])
                        err_byte_count += np.count_nonzero((ad[2] - read[0][2]) != 0)
        
        return err_byte_count


results = simulate('1k_data',4,4,2,2,0,0,0.01,4)
print(results)