import numpy as np
from typing import Union,List

class DecoderBase:
    def __init__(self,bytes_per_oligo : int,address_size:int) -> None:
            self.bytes_per_oligo = bytes_per_oligo
            self.address_size = address_size
            self.lost_bytes = 0
            self.for_error_check = []
    
    def assemble_saparated_data(self,data:List):
      saparated_with_meta_add_data = []
      # print(data)
      rawdata = []
      for d in data:
        if len(d) < 4:
          continue
        s = (d[:4:],d[4:4+d[0]:],d[4+d[0]::]) if d[2] == 0 else (d[:4:],d[4:4+d[0]:],d[4+d[0]:len(d) - d[2]:])
        saparated_with_meta_add_data.append(s)
        sorted_by_address = sorted(saparated_with_meta_add_data,key= lambda x:tuple(x[1]))
        for st in sorted_by_address:
          rawdata.append(list(st[2]))
      return saparated_with_meta_add_data,sum(rawdata,[])
    

