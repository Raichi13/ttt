from encoder_base import EncoderBase
from tdt import TdT
import numpy as np
from typing import Union,List
from encoder_base import EncoderBase
import pandas as pd
from reedsolo import RSCodec,ReedSolomonError

class RSEncoder(EncoderBase):
    def __init__(self, file_path: str, bytes_per_oligo: int, address_size: int,symbol_size : int) -> None:
        super().__init__(file_path, bytes_per_oligo, address_size,0)
        self.symbol_size = symbol_size
        self.__rs = RSCodec(symbol_size)
    
    def encode(self):
        identified_data = super().get_identified_data(self.symbol_size)
        encoded_data = []
        for d_in_oligo in identified_data:
            e = self.__rs.encode(bytearray(list(d_in_oligo)))
            encoded_data.append(np.frombuffer(e,dtype=np.uint8))
        return encoded_data
