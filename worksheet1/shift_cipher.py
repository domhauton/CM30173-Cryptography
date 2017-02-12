# Solve shift cipher

import re
from worksheet1 import word_lists

cipherText = "WKHPDJLFZRUGVDUHVTXHDPLVKRVVLIUDJH"
solution = "THE MAGIC WORDS ARE SQUEAMISH OSS IF RAGE"

mostCommonWords = [x.upper() for x in word_lists.get_top_1000_words()]


def english_proportion(plain_text):
    match_list = [False for x in range(len(plain_text))]
    for word in mostCommonWords:
        for position in [m.start() for m in re.finditer(word, plain_text)]:
            for idx in [i + position for i in range(len(word))]:
                # print("WORD: {} POS: {} IDX: {}".format(word, position, idx))
                match_list[idx] = True
    return float(sum(match_list))/float(len(plain_text))


def decode_shift_cipher(cipher_text, key):
    return ''.join([chr((ord(x)-ord('A') + key)%26 + ord('A')) for x in cipher_text.upper()])


def brute_force_shift_cipher(cipher_text):
    plainTexts = [decode_shift_cipher(cipherText, x) for x in range(0, 26)]
    return max(plainTexts, key=lambda x: english_proportion(x))

print("Cipher Text {:.02f}: {}".format(english_proportion(cipherText), cipherText))

finalPlainText = brute_force_shift_cipher(cipherText)

print("Plain Text  {:.02f}: {}".format(english_proportion(finalPlainText), finalPlainText))
