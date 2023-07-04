#include <iostream>
#include <map>
#include "hamming_codec.h"

extern "C" {

uint64_t encode_hamming(uint64_t input_data, uint32_t n_bits, const char* parity_loc_str) {
    std::map<std::string, hamming_codec::ParityLocation> parity_loc_map{
        {"DEFAULT", hamming_codec::ParityLocation::DEFAULT},
        {"MSB", hamming_codec::ParityLocation::MSB},
        {"LSB", hamming_codec::ParityLocation::LSB}
    };
    auto encoded_binary_string = hamming_codec::encode(input_data, n_bits, parity_loc_map.at(parity_loc_str));
    uint64_t encoded_int = std::stoul(encoded_binary_string, nullptr, 2);
    return encoded_int;
}

uint64_t decode_hamming(uint64_t input_data, uint32_t n_bits, const char* parity_loc_str, uint32_t n_parity_bits) {
    std::map<std::string, hamming_codec::ParityLocation> parity_loc_map{
        {"DEFAULT", hamming_codec::ParityLocation::DEFAULT},
        {"MSB", hamming_codec::ParityLocation::MSB},
        {"LSB", hamming_codec::ParityLocation::LSB}
    };
    std::string decoded_binary_string = hamming_codec::decode(input_data, n_bits, parity_loc_map.at(parity_loc_str), n_parity_bits);
    uint64_t decoded_int = std::stoul(decoded_binary_string, 0, 2);
    return decoded_int;
}

} 
