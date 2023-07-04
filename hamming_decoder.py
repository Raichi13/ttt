from decoder_base import DecoderBase
import hamming

class HammingDecoder(DecoderBase):
    def __init__(self,bytes_per_oligo : int,address_size:int,ecc_interval:int) -> None:
        super().__init__(bytes_per_oligo,address_size)
        self.lost_bytes = 0
        self.ecc_interval = ecc_interval

    # データには複数オリゴ一緒に配列で入っている
    def decode(self,data):
        decoded_data = hamming.correct_error_and_decode(data,self.ecc_interval)
        sp,raw_data = super().assemble_saparated_data(decoded_data)
        self.for_error_check = sp
        return raw_data

