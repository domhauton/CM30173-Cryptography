import numpy
import random

# substitutionKey = [4, 1, 'e', 8, 'd', 6, 2, 'b', 'f', 'c', 9, 7, 3, 'a', 5, 0]
substitutionKey = [7, 'd', 'e', 3, 0, 6, 9, 'a', 1, 2, 8, 5, 'b', 'c', 4, 'f']
permutationKey = [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16]
permutationKey = [x-1 for x in permutationKey]
rounds = 4


def pretty_bin(binary):
    return ' '.join([binary[i:i + 4] for i in range(0, len(binary), 4)])


def xor_bin(data1, data2):
    output = int(data1, 2) ^ int(data2, 2)
    return '{0:0{1}b}'.format(output, len(data1))


def xor(bin_data, hex_data):
    output = int(bin_data, 2) ^ int(hex_data, 16)
    return '{0:0{1}b}'.format(output, len(bin_data))


def permutation(input_bytes, key):
    redundant_cipher_text = len(input_bytes) % len(key)
    plain_text = list(input_bytes)
    for idx in range(len(input_bytes) - redundant_cipher_text):
        inner_idx = idx % len(key)
        offset = idx - inner_idx
        new_idx = offset + key[inner_idx]
        # print("offset: {}, inner_idx: {}, idx: {}, newIdx: {}".format(offset, inner_idx, idx, new_idx))
        plain_text[new_idx] = input_bytes[idx]
    return ''.join(plain_text)


def substitution_box(input_binary, key):
    input_hex = '{:0{width}x}'.format(int(input_binary, 2), width=int(len(input_binary)/4))
    output_hex = ''.join([str(key[int(letter, 16)]) for letter in input_hex])
    return '{0:0{1}b}'.format(int(output_hex, 16), len(input_binary))


def key_schedule_gen(bin_key):
    hex_key = '{:0{width}x}'.format(int(bin_key, 2), width=4)
    return [hex_key[x:x+4] for x in range(0, 5)]


def spn_encrypt(data, key, sub_key, perm_key):
    data = data.replace(" ", "")
    keys = key_schedule_gen(key.replace(" ", ""))
    for rndIdx in range(1, rounds+1):
        # print("ROUND " + str(rndIdx))
        data = xor(data, keys[rndIdx-1])
        # print("xor:  " + pretty_bin(data))
        data = substitution_box(data, sub_key)
        # print("sub:  " + pretty_bin(data))
        if rndIdx < rounds:
            data = permutation(data, perm_key)
            # print("perm: " + pretty_bin(data))
        else:
            data = xor(data, keys[rndIdx])
            # print("xor:  " + pretty_bin(data))
    return pretty_bin(data)


def spn_encrypt_diff_anal(data, key, sub_key, perm_key):
    data = data.replace(" ", "")
    keys = key_schedule_gen(key.replace(" ", ""))
    for rndIdx in range(1, rounds+1):
        # print("ROUND " + str(rndIdx))
        data = xor(data, keys[rndIdx-1])
        # print("xor:  " + pretty_bin(data))
        if rndIdx < rounds:
            data = substitution_box(data, sub_key)
            # print("sub:  " + pretty_bin(data))
            data = permutation(data, perm_key)
            # print("perm: " + pretty_bin(data))
    return data

inputKey = "1110 0111 0110 0111 1001 0000 0011 1101"
plainText = "0100 1110 1010 0001"

# cipherText = spn_encrypt(plainText, inputKey, substitutionKey, [x-1 for x in permutationKey])

# print(plainText + " -> " + cipherText)


def find_s_box_characteristics(s_box_key):
    bin_array = ['{:0{width}b}'.format(x, width=4) for x in range(16)]
    sboxed_array = [substitution_box(x, s_box_key) for x in bin_array]
    result = [[0 for _ in range(16)] for _ in range(16)]
    for bin_num_1 in bin_array:
        for bin_num_2 in bin_array:
            bin_out_1 = sboxed_array[int(bin_num_1, 2)]
            bin_out_2 = sboxed_array[int(bin_num_2, 2)]

            xor_diff_input = xor_bin(bin_num_1, bin_num_2)
            xor_diff_output = xor_bin(bin_out_1, bin_out_2)

            xor_diff_in_idx = int(xor_diff_input, 2)
            xor_diff_out_idx = int(xor_diff_output, 2)
            result[xor_diff_in_idx][xor_diff_out_idx] += 1
    return result


def print_characteristics(characteristics):
    s = [[str(e) for e in row] for row in characteristics]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))


def differential_trail_calc(input_xor_bin, s_box_char, permutation_key):
    rnd_likely_xor_bin = input_xor_bin
    probability = 1.0
    for rndIdx in range(1, rounds):
        rnd_input_hex = '{:0{width}x}'.format(int(rnd_likely_xor_bin, 2), width=int(len(rnd_likely_xor_bin) / 4))
        likely_hex = ''.join(['{:01x}'.format(s_box_char[int(val, 16)].index(max(s_box_char[int(val, 16)]))) for val in rnd_input_hex])
        probability *= numpy.prod([max(s_box_char[int(val, 16)])/len(s_box_char[int(val, 16)]) for val in rnd_input_hex])
        rnd_likely_xor_bin = '{0:0{width}b}'.format(int(likely_hex, 16), width=len(input_xor_bin))
        rnd_likely_xor_bin = permutation(rnd_likely_xor_bin, permutation_key)
    return [probability, rnd_likely_xor_bin]


def find_good_differential_trail(s_box_characteristics, permutation_key):
    max_prob = 0.0
    best_input_xor_bin = "0" * 4 * 4
    best_output_xor_bin = "0" * 4 * 4
    for val in ['{:0{width}b}'.format(x, width=4) for x in range(1, 16)]:
        for position in range(4):
            bin_guess = "0" * 3 * 4
            bin_guess = bin_guess[:position*4] + val + bin_guess[position*4:]
            most_likely = differential_trail_calc(bin_guess, s_box_characteristics, permutation_key)
            if most_likely[0] > max_prob:
                max_prob = most_likely[0]
                best_input_xor_bin = bin_guess
                best_output_xor_bin = most_likely[1]
                # print(bin_guess + "->" + most_likely[1] + ": " + str(most_likely[0]))
    return [max_prob, best_input_xor_bin, best_output_xor_bin]


def find_right_pair(input_xor_bin, output_xor_bin, key, s_box_key, p_box_key):
    rand_input_bin_1 = '0'*16
    rand_input_bin_2 = '0'*16
    rand_output_bin_1 = '0'*16
    rand_output_bin_2 = '0'*16
    rand_output_xor_bin = '0'*16

    ctr = 0

    while rand_output_xor_bin != output_xor_bin:
        ctr += 1
        rand_input_bin_1 = ''.join(['{:04b}'.format(random.randint(0, 16)) for _ in range(4)])
        rand_input_bin_2 = xor_bin(rand_input_bin_1, input_xor_bin)

        rand_output_bin_1 = spn_encrypt_diff_anal(rand_input_bin_1, key, s_box_key, p_box_key)
        rand_output_bin_2 = spn_encrypt_diff_anal(rand_input_bin_2, key, s_box_key, p_box_key)

        rand_output_xor_bin = xor_bin(rand_output_bin_1, rand_output_bin_2)
    print("Found right pair in " + str(ctr) + " attempts.")
    return [rand_input_bin_1, rand_input_bin_2, rand_output_bin_1, rand_output_bin_2]


print("Finding difference distribution table")
sBoxCharacteristics = find_s_box_characteristics(substitutionKey)
print_characteristics(sBoxCharacteristics)
diff_trail = find_good_differential_trail(sBoxCharacteristics, permutationKey)
print("Diff Trail: " + diff_trail[1] + "->" + diff_trail[2] + " - Chance: " + str(diff_trail[0]))
rightPair = find_right_pair(diff_trail[1], diff_trail[2], inputKey, substitutionKey, permutationKey)
print("R Pair 1a:  " + rightPair[0] + "->" + rightPair[2])
print("R Pair 1b:  " + rightPair[1] + "->" + rightPair[3])
