from tdt import TdT
import numpy as np
from typing import Union,List
from dna_transcoder import DNATranscoder
from hamming_encoder import HammingEncoder
import pandas as pd
from hamming_decoder import HammingDecoder
from error_counter import ErrorCounter
from rs_encoder import RSEncoder
from rs_decoder import RSDecoder

# define params
file_name = '1k_data'
bytes_per_oligo = 32
address_size = 4
symbol_size = 5
ecc_interval = 4
miss_extension_prob = 0.01
over_extension_prob = 0.0
deletion_prob = 0.0
molcule_num = 10
reaction_cycle = 3



# Test in RS encoding and decoding


# re = RSEncoder(file_name,bytes_per_oligo,address_size,symbol_size)
# encoded_data = re.encode()

# dt = DNATranscoder()
# encoded_data_dna = dt.encode_many(encoded_data)

# tdt = TdT(encoded_data_dna,reaction_cycle,molcule_num,miss_extension_prob,deletion_prob,over_extension_prob)
# ext_simlated_data = tdt.synthesis()
# # print(ext_simlated_data)
# decoded_data_from_dna = dt.decode_with_build_consensus_base(ext_simlated_data)

# # print("here",decoded_data_from_dna)
# rd = RSDecoder(bytes_per_oligo,address_size,symbol_size)
# decoded_data = rd.decode(decoded_data_from_dna)
# # print(decoded_data_from_dna)

# ec = ErrorCounter(re.ref,rd.for_error_check)
# print(ec.count_error())


# Test in Hamming encoding and decoding

he = HammingEncoder(file_name,bytes_per_oligo,address_size,ecc_interval)
encoded_data = he.encode()

dt = DNATranscoder()
encoded_data_dna = dt.encode_many(encoded_data)

tdt = TdT(encoded_data_dna,reaction_cycle,molcule_num,miss_extension_prob,deletion_prob,over_extension_prob)
ext_simlated_data = tdt.synthesis()
# print(ext_simlated_data)
decoded_data_from_dna = dt.decode_with_build_consensus_base(ext_simlated_data)

# print("here",decoded_data_from_dna)
# rd = RSDecoder(bytes_per_oligo,address_size,symbol_size)
hd = HammingDecoder(bytes_per_oligo,address_size,ecc_interval)
decoded_data = hd.decode(decoded_data_from_dna)
# print(decoded_data_from_dna)

ec = ErrorCounter(he.ref,hd.for_error_check)
print(ec.count_error())