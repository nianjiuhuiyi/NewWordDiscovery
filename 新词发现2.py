from collections import Counter
import numpy as np
import re
import os
import jieba
import time
import multiprocessing
import glob


def n_gram_words(text, n_gram):
    """
    To get n_gram word frequency dict
    input: str of the chinese sentence ，int of n_gram
    output: word frequency dict

    """
    words = []
    for i in range(1, n_gram + 1):
        words += [text[j:j + i] for j in range(len(text) - i + 1)]
    words_freq = dict(Counter(words))
    return words_freq


def PMI_filter(word_freq_dic, min_p):
    """
    To get words witch  PMI  over the threshold
    input: word frequency dict , min threshold of PMI
    output: condinated word list

    """
    new_words = []
    for word in word_freq_dic:
        if len(word) == 1:
            pass
        else:
            p_x_y = min([word_freq_dic.get(word[:i]) * word_freq_dic.get(word[i:]) for i in range(1, len(word))])
            mpi = p_x_y / word_freq_dic.get(word)
            if mpi > min_p:
                new_words.append(word)
    return new_words


def calculate_entropy(char_list):
    """
    To calculate entropy for  list  of char
    input: char list
    output: entropy of the list  of char
    """
    char_freq_dic = dict(Counter(char_list))
    entropy = (-1) * sum(
        [char_freq_dic.get(i) / len(char_list) * np.log2(char_freq_dic.get(i) / len(char_list)) for i in char_freq_dic])
    return entropy


def Entropy_left_right_filter(condinate_words, text, min_entropy):
    """
    To filter the final new words from the condinated word list by entropy threshold
    input:  condinated word list ,min threshold of Entropy of left or right
    output: final word list
    """
    final_words = []
    for word in condinate_words:
        try:
            left_right_char = re.findall('(.)%s(.)' % word, text)

            left_char = [i[0] for i in left_right_char]
            left_entropy = calculate_entropy(left_char)

            right_char = [i[1] for i in left_right_char]
            right_entropy = calculate_entropy(right_char)

            if min(right_entropy, left_entropy) > min_entropy:
                final_words.append(word)
        except:
            pass
    return final_words


def newWordFind(file_path, stopKey):
    # file_paht:txt文件绝地路径
    a = time.time()
    print("\n{}开始处理，进程号为：{}".format(file_path, os.getpid()))
    with open(file_path, encoding="utf-8") as f:
        text = f.read()
        text = text.replace("\n", "")

    stop_word = ['.', ',', '、', ';', '。', '%', '~', '“', '”', '：', ':', '!', '(', ')', '（', '）', ' ', '，']
    for i in stop_word:
        text = text.replace(i, "")

    # finding the new words
    min_p = 7  # 词的最大长度；越大，下面的n_gram的个数越多
    min_e = 3  # PMI的阈值,超参 ;一开始是2
    # 结果是一个字典；每种字出现个数、每连续两个字的出现个数、3个字、..、最大min_p个字
    n_gram = n_gram_words(text, min_p)

    condinate = PMI_filter(n_gram, min_e)   # 凝固度过滤
    # 新词发现的结果
    final = Entropy_left_right_filter(condinate, text, 2)  # 自由度过滤；；一开始是1

    # jieba的结果
    jieba_out = [i for i in jieba.cut(text) if i not in stopKey and len(i) != 1]

    # 得到的新词里去掉jieba分词结果里的
    result = [w for w in final if w not in jieba_out and len(w) != 1 and w not in stopKey]
    print("去重前的个数：", len(final))
    print("去重后的个数：", len(result))

    # 结果保存
    results_path = r"./results/result_2"
    if not os.path.exists(results_path):
        os.makedirs(results_path, exist_ok=True)
    result_file_name = os.path.basename(file_path)
    result_file_path = os.path.join(results_path, result_file_name)
    with open(result_file_path, "w", encoding="utf-8") as f:
        for res in result:
            f.write("{}\n".format(res))
    b = time.time()
    print("{}整体用时：{:.2f}\n".format(result_file_name, b - a))


if __name__ == '__main__':
    stopkey = [w.strip() for w in open(r"./data/stopWord.txt", encoding="utf-8").readlines()]
    root = r"./data/preprocessing_data"
    files_path = glob.glob(root + "/*.txt")
    pool = multiprocessing.Pool(4)
    for file_path in files_path:
        pool.apply_async(newWordFind, (file_path, stopkey))
    print("-----------start-----------")
    pool.close()
    pool.join()
    print("-----------end-----------")
