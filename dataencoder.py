import numpy as np

class DataEncoder:
    def __init__(self, file_path,encode_algorithm,encode_param,data_par_oligo = 16):
        self.file_path = file_path
        self.data_par_oligo = data_par_oligo
        self.encode_algorithm = encode_algorithm
        self.encode_param = encode_param
    
    def read_file_and_separate_data_each_oligo(self):
        with open(self.file_path,'rb') as f:
            bdata = np.fromfile(f,dtype=np.dtype(np.uint8))
            s_data = [bdata[i:i+self.data_par_oligo] for i in range(0, len(bdata), self.data_par_oligo)]      
        added = []
        for i,s in enumerate(s_data):
            added.append(self.data_par_oligo - len(s))
            s_data[i] = np.array(list(s_data[i]) + list([0]*(self.data_par_oligo - len(s))))
        return s_data,added,bdata
    
    def encode(self):
        s_data,added,bdata = self.read_file_and_separate_data_each_oligo()
        encoded_data = []
        for i,s in enumerate(s_data):
            if self.encode_algorithm == 'hamming':
                pass
            elif self.encode_algorithm == 'rs':
                pass
            else:
                print('encode_algorithm is invalid')
                exit()
        return encoded_data,added,bdata