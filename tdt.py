import random

class TdT:
    def __init__(self,target_bases,reaction_cycle,molecule_number,miss_extension_probability,deletion_probability,over_extension_probability):
        self.target_bases = target_bases
        self.reaction_cycle = reaction_cycle
        self.molecule_number = molecule_number
        self.miss_extension_probability = miss_extension_probability
        self.deletion_probability = deletion_probability
        self.over_extension_probability = over_extension_probability
        self.miss_extension_count = 0
        self.deletion_count = 0
        self.over_extension_count = 0
        self.synthesis_products = []


    # 重み付けされた排反な2つの事象の抽選関数(高速化のために2つの事象に限定して実装(listで渡すと遅い))
    def weighted_random_exclusive(self,probability0:int,probability1:int):
        r = random.random()
        if r < probability0 :
            return 0
        elif r < probability0 + probability1 :
            return 1
        else:
            return -1
    
    # 重み付けされた抽選関数
    def weighted_random(self,probability:int):
        return (random.random() < probability)
        
    def extension(self,base):
        bases_list = ['A','G','C','T']
        r = []
        for i in range(self.reaction_cycle):
            ext_base = base
            if self.weighted_random(self.miss_extension_probability):# 塩基ミス
                other_bases = [s for s in bases_list if base not in s]
                ext_base = other_bases[random.randint(0,2)]
                self.miss_extension_count += 1
            # 伸長失敗と過剰に伸長
            deletion_or_over = self.weighted_random_exclusive(self.over_extension_probability,self.deletion_probability)
            if deletion_or_over == -1 :# 正常に伸長
                r.append(ext_base)      
                continue
            if deletion_or_over == 0 : #過剰に伸長
                r.append(ext_base)
                r.append(ext_base)
                self.over_extension_count += 1
                continue
            if deletion_or_over == 1 : #欠損
                self.deletion_count += 1
                continue
        return r       


    def __synthesis(self,target_base):
        synthesis_product = []
        for base in target_base:
            synthesis_product = synthesis_product + self.extension(base)
        return synthesis_product
    
    def synthesis(self):
        self.synthesis_products = []
        for tb in self.target_bases:
            products = []
            for i in range(self.molecule_number):
                products.append(self.__synthesis(tb))
            self.synthesis_products.append(products)
        return self.synthesis_products



# tb = ['A','G','C','T']
# tdt = TdT(tb,3,0,0.2,0)
# print(tdt.synthesis())