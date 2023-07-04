import numpy as np
from typing import Union,List

class EncoderBase:
    def __init__(self,file_path : str,bytes_per_oligo : int,address_size:int,encode_type:int) -> None:
        self.file_path = file_path
        self.bytes_per_oligo = bytes_per_oligo
        self.address_size = address_size
        self.encode_type = encode_type
        self.ref = []

    def __read_file_and_separate_data_each_oligo(self):
        with open(self.file_path,'rb') as f:
            bdata = np.fromfile(f,dtype=np.dtype(np.uint8))
            s_data = [bdata[i:i+self.bytes_per_oligo] for i in range(0, len(bdata), self.bytes_per_oligo)]
        added = []
        for i,s in enumerate(s_data):
            added.append(self.bytes_per_oligo - len(s))
            s_data[i] = np.array(list(s_data[i]) + list([0]*(self.bytes_per_oligo - len(s))))
        return s_data,added,bdata #分割&ゼロ埋めされたdata([uint8]),0埋めしたbyte
    
    def __generate_address(self,max:int):
        res = []
        for i in range(max):
            a= list(np.binary_repr(i,width=8*self.address_size)[j:j+8] for j in range(0,8*self.address_size,8))
            res.append(np.array(list(map(lambda x:int(x,2),a))).astype(np.uint8))
        return np.array(res)
    
    def __generate_metadata(self,added:List[np.uint8],free:np.uint8,length:int):
        meta_data = np.stack([np.array([self.address_size]*length,dtype=np.uint8),
                np.array([self.encode_type]*length,dtype=np.uint8),
                np.array(added,dtype=np.uint8),
                np.array(([free]*length),dtype=np.uint8)],1)
        return meta_data
    
    def __identified_and_added_meta_data(self,data,added,free):
        address = self.__generate_address(len(data))
        address_and_data = np.r_["1",address,data]
        meta_data = self.__generate_metadata(added,free,len(data))
        return np.r_["1",meta_data,address_and_data]
    
    def __assemble_saparated_data(self,data:List):
      saparated_with_meta_add_data = []
      for d in data:
        s = (d[:4:],d[4:4+d[0]:],d[4+d[0]::]) if d[2] == 0 else (d[:4:],d[4:4+d[0]:],d[4+d[0]:len(d) - d[2]:])
        saparated_with_meta_add_data.append(s)
        sorted_by_address = sorted(saparated_with_meta_add_data,key= lambda x:tuple(x[1]))
        rawdata = []
        for st in sorted_by_address:
          rawdata.append(list(st[2]))
      return saparated_with_meta_add_data,sum(rawdata,[])
    

    def get_identified_data(self,free:np.uint8):
        data,added,bdata = self.__read_file_and_separate_data_each_oligo()
        d = self.__identified_and_added_meta_data(data,added,free)
        self.ref = self.__assemble_saparated_data(d)[0]
        return d
    
