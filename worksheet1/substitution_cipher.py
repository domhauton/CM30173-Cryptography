# Solve permutation cipher

import re
import itertools
from random import shuffle
from random import randint
from worksheet1 import word_lists
from collections import Counter

cipherText = "AGBAPZTGELGPTIPMGHQCGAECHZFVCEXXGLYIGHEULTQATQHPUFEUYGZZEVGUYHGUYIPUYIGQUGYIPYEAYIGFNKTYYCEGLYIGFSQKZLEUMGUYPSEXIGCYIPYUQQUGSQKZLDCGPO"
solution = "FEW FALSE IDEAS HAVE MORE FIRMLY GRIPPED THE MINDS OF SO MANY INTELLIGENT MEN THAN THE ONE THAT IF THEY JUST TRIED THEY COULD INVENT A CIPHER THAT NO ONE COULD BREAK"

solution2 = "DO RDKMGO IF OKGSKLO HE NOD IN H MY QNIBBOFASOHITFGEDGEHKTYITAOMMIQOTA HOT ASK TASOE TO ASK AIDASOYUPGAANIOFASOYWEPMFITLOTAKWIBSONASKATEETOWEPMFXNOKZ"

mostCommonWords = [x.lower() for x in word_lists.get_top_3000_words()]


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


def decode_cipher(cipher_text, key):
    # print("Key: {}".format(key))
    return ''.join([chr(key[ord(letter)-ord('A')]+ord('A')) for letter in cipher_text.upper()])


def brute_force_substitution_cipher(cipher_text):
    keys = itertools.permutations(range(26))
    # print(keys)
    plain_texts = [decode_cipher(cipher_text, x) for x in keys]
    return max(plain_texts, key=lambda x: english_proportion(x))


def permute_key(key):
    new_permutation = list(key)
    shuffle(new_permutation)
    return new_permutation


def small_permute_key(key):
    a = randint(0, len(key)-1)
    b = randint(0, len(key)-1)
    new_key = list(key)
    new_key[a] = key[b]
    new_key[b] = key[a]
    return new_key

def find_random_best_start_key(cipher_text):
    return max([permute_key(range(26)) for _ in range(200)],
        key=lambda key: english_proportion(decode_cipher(cipher_text, key)))


def genetic_solve_substitution_cipher(cipher_text, start_key):
    current_best_key = ""
    best_key = start_key
    while best_key != current_best_key:
        print("Best key: {}, Score: {:02f}".format(best_key, english_proportion(decode_cipher(cipher_text, best_key))))
        current_best_key = best_key
        key_permutations = []
        for permutation in [small_permute_key(current_best_key) for _ in range(10)]:
            key_permutations.append(permutation)
            for permutation2 in [small_permute_key(permutation) for _ in range(5)]:
                key_permutations.append(permutation2)
                key_permutations.extend([small_permute_key(permutation2) for _ in range(2)])
        key_permutations.append(current_best_key)
        best_key = max(key_permutations, key=lambda key: english_proportion(decode_cipher(cipher_text, key)))
    return decode_cipher(cipher_text, best_key)


def get_common_letter_list(ciper_text):
    counter = Counter(list(ciper_text))
    return [x[0] for x in counter.most_common(26)]


def get_start_key(letter_distribution, ideal_distribution):
    current_key = list(range(26))
    for idx in reversed(range(len(letter_distribution))):
        current_letter = ord(letter_distribution[idx].lower()) - ord('a')
        ideal_letter = ord(ideal_distribution[idx].lower())-ord('a')
        victim_idx = current_key.index(ideal_letter)

        current_key[victim_idx] = current_key[current_letter]
        current_key[current_letter] = ideal_letter
    return current_key


print("Cipher Text {:.02f}: {}".format(english_proportion(cipherText), cipherText))

startLetterDistribution = get_common_letter_list(cipherText)
idealDistribution = word_lists.get_letter_dist_list()

startKey = get_start_key(startLetterDistribution, idealDistribution)
print(startKey)
startingPoint = decode_cipher(cipherText, startKey)
trueStartLetterDistribution = get_common_letter_list(startingPoint)

print("Ideal: {}\nGiven: {}\nStart: {}\n{}".format(idealDistribution, startLetterDistribution, trueStartLetterDistribution, startingPoint))

finalPlainText = genetic_solve_substitution_cipher(cipherText, startKey)

print("Final: {}".format(get_common_letter_list(finalPlainText)))
print("Ideal: {}".format(get_common_letter_list(solution)))

print("Plain Text  {:.02f}: {}".format(english_proportion(finalPlainText), finalPlainText))
