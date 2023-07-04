from encoder_base import EncoderBase
from tdt import TdT
import numpy as np
from typing import Union,List
from decoder_base import DecoderBase
import pandas as pd
from reedsolo import RSCodec,ReedSolomonError

class RSDecoder(DecoderBase):
    def __init__(self, bytes_per_oligo: int, address_size: int,symbol_size : int) -> None:
        super().__init__(bytes_per_oligo, address_size)
        self.symbol_size = symbol_size
        self.__rs = RSCodec(symbol_size)
    
    def decode(self,data):
        decoded_data = []
        for d_in_oligo in data:
            try:
                d = np.frombuffer(self.__rs.decode(bytearray(d_in_oligo))[0],dtype=np.uint8)
            except ReedSolomonError:
                # print('fire ReedSolomonError')
                d = np.array([],dtype=np.uint8)
            decoded_data.append(d)
        sp,raw_data = super().assemble_saparated_data(decoded_data)
        self.for_error_check = sp
        return raw_data
    