from typing import List

class ErrorCounter:
    def __init__(self,ref : List,data : List) -> None:
        self.error_count = 0
        self.lost_address_count = 0
        self.ref = ref
        self.data = data
        

    def __diff_count(ref, data):
        min_len = min(len(ref), len(data))
        max_len = max(len(ref), len(data))

        # 一致しない要素の数を数える
        count = sum(1 for i in range(min_len) if ref[i] != data[i])

        # 残りの要素の数を加算する
        count += max_len - min_len

        return count
    
    def count_error(self):
        self.lost_address_count = 0
        self.error_count = 0
        decoded_dict = {tuple(item[1]): item for item in self.data}

        no_match_length_sum = 0

        for item_ref in self.ref:
            item_decoded = decoded_dict.get(tuple(item_ref[1]))
            if item_decoded is not None:
                self.error_count += ErrorCounter.__diff_count(item_ref[2],item_decoded[2])
            else:
                no_match_length_sum += len(item_ref[2])
                self.lost_address_count += 1        

        self.error_count += no_match_length_sum
        return self.error_count
    
