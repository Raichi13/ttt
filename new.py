# -*- coding: utf-8 -*-

import itertools
import numpy as np
import pandas as pd
from typing import Union
import hamming_codec
from reedsolo import RSCodec,ReedSolomonError
import random
from multiprocessing import Pool
import ctypes


#バイナリファイルを読み込みintのリストに変換
def read_bin(path: str) -> list:
    with open(path, 'rb') as f:
        data = f.read()
    return list(data)


if __name__ == '__main__':
    print(read_bin('1k_data'))