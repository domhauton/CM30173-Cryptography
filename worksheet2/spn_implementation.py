substitutionKey = [4, 1, 'e', 8, 'd', 6, 2, 'b', 'f', 'c', 9, 7, 3, 'a', 5, 0]
permutationKey = [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16]
rounds = 4


def pretty_bin(binary):
    return ' '.join([binary[i:i + 4] for i in range(0, len(binary), 4)])


def xor(data, hex_key):
    output = int(data, 2) ^ int(hex_key, 16)
    return '{0:0{1}b}'.format(output, len(data))


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
    input_hex = '{:0{width}x}'.format(int(input_binary, 2), width=4)
    output_hex = ''.join([str(key[int(letter, 16)]) for letter in input_hex])
    return '{0:0{1}b}'.format(int(output_hex,16), len(input_binary))


def key_schedule_gen(bin_key):
    hex_key = '{:0{width}x}'.format(int(bin_key, 2), width=4)
    return [hex_key[x:x+4] for x in range(0, 5)]


def spn_encrypt(data, key, sub_key, perm_key):
    data = data.replace(" ", "")
    keys = key_schedule_gen(key.replace(" ", ""))
    for rndIdx in range(1, rounds+1):
        print("ROUND " + str(rndIdx))
        data = xor(data, keys[rndIdx-1])
        print("xor:  " + pretty_bin(data))
        data = substitution_box(data, sub_key)
        print("sub:  " + pretty_bin(data))
        if rndIdx < rounds:
            data = permutation(data, perm_key)
            print("perm: " + pretty_bin(data))
        else:
            data = xor(data, keys[rndIdx])
            print("xor:  " + pretty_bin(data))
    return pretty_bin(data)

inputKey = "1110 0111 0110 0111 1001 0000 0011 1101"
plainText = "0100 1110 1010 0001"

cipherText = spn_encrypt(plainText, inputKey, substitutionKey, [x-1 for x in permutationKey])
