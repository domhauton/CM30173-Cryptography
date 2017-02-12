# Solve permutation cipher

import re
import itertools
from worksheet1 import word_lists

cipherText = "EMRMESEBREITCRUACYSINIHIANLTOSSEYSAEACRUEWSHTESEKANKTIL"
solution = "REMEMBER SECURITY IS A CHAIN ITS ONLY AS SECURE AS THE WEAKEST LINK"

mostCommonWords = [x.lower() for x in word_lists.get_top_1000_words()]


def english_proportion(plain_text):
    lower_plain_text = plain_text.lower()
    match_list = [False for x in range(len(plain_text))]
    for word in mostCommonWords:
        for position in [m.start() for m in re.finditer(word, lower_plain_text)]:
            for idx in [i + position for i in range(len(word))]:
                # print("WORD: {} POS: {} IDX: {}".format(word, position, idx))
                match_list[idx] = True
    final_score = float(sum(match_list))/float(len(plain_text))
    # print("Score: {:.02f} - {}".format(final_score, plain_text))
    return final_score


def decode_permutation_cipher(cipher_text, key):
    redundant_cipher_text = len(cipher_text) % len(key)
    plain_text = list(cipher_text)
    for idx in range(len(cipher_text) - redundant_cipher_text):
        inner_idx = idx % len(key)
        offset = idx - inner_idx
        new_idx = offset + key[inner_idx]
        # print("offset: {}, inner_idx: {}, idx: {}, newIdx: {}".format(offset, inner_idx, idx, new_idx))
        plain_text[new_idx] = cipher_text[idx]
    return ''.join(plain_text)


def get_permutations(key_len):
    return itertools.permutations(range(key_len))


def brute_force_permutation_cipher(cipher_text, max_key_len):
    key_list_set = [get_permutations(key_len) for key_len in range(2, max_key_len+1)]
    keys = list(itertools.chain.from_iterable(key_list_set))
    # print(keys)
    plain_texts = [decode_permutation_cipher(cipher_text, x) for x in keys]
    return max(plain_texts, key=lambda x: english_proportion(x))

print("Cipher Text {:.02f}: {}".format(english_proportion(cipherText), cipherText))

finalPlainText = brute_force_permutation_cipher(cipherText, 5)

print("Plain Text  {:.02f}: {}".format(english_proportion(finalPlainText), finalPlainText))

