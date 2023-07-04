from encoder_base import EncoderBase
from tdt import TdT
import numpy as np
import hamming
from typing import Union,List
from encoder_base import EncoderBase
import pandas as pd
import ctypes

class HammingEncoder(EncoderBase):
    def __init__(self, file_path: str, bytes_per_oligo: int, address_size: int,ecc_interval:int) -> None:
        if ecc_interval > 4 or ecc_interval < 1:
            raise ValueError('ecc_interval must be less than 4 and more than 1')
        self.ecc_interval = ecc_interval
        self.byte_max = {1:2,2:3,3:4,4:5}
        super().__init__(file_path, bytes_per_oligo, address_size, ecc_interval)

    def encode(self):
        #複数オリゴに対応した配列で返ってくる
        identified_data = super().get_identified_data(self.ecc_interval)
        ecced_data = hamming.add_humming_ecc(identified_data,self.ecc_interval)
        ecced_data_uint8 = []
        for d_in_oligo in ecced_data:
            b_in_oligo = []
            for d in d_in_oligo:
                b_in_oligo.append(np.array(bytearray(int(d).to_bytes(self.byte_max[self.ecc_interval],'big')),dtype=np.uint8))
            ecced_data_uint8.append(np.array(b_in_oligo).flatten())
        return ecced_data_uint8
        

    