# -*- coding: utf-8 -*-
import time
import os
import jieba
import glob
import multiprocessing
from tools.model import TrieNode
from tools.utils import get_stopwords, load_dictionary, generate_ngram, save_model, load_model
from tools.config import basedir


def load_data(filename, stopwords):
    """

    :param filename:
    :param stopwords:
    :return: 二维数组,[[句子1分词list], [句子2分词list],...,[句子n分词list]]
    """
    data = []
    with open(filename, 'r', encoding="utf-8") as f:
        for line in f:
            word_list = [x for x in jieba.cut(line.strip(), cut_all=False) if x not in stopwords]
            data.append(word_list)
    return data


def load_data_2_root(data, model):
    print('------> 插入节点')
    for word_list in data:
        # tmp 表示每一行自由组合后的结果（n gram）
        # tmp: [['它'], ['是'], ['小'], ['狗'], ['它', '是'], ['是', '小'], ['小', '狗'], ['它', '是', '小'], ['是', '小', '狗']]
        ngrams = generate_ngram(word_list, 3)
        for d in ngrams:
            model.add(d)
    print('------> 插入成功')


def newWordFind(file_path, model, stopKey):
    # 加载新的文章
    a = time.time()
    filename = file_path
    print("\n{}开始处理，进程号为：{}".format(filename, os.getpid()))
    data = load_data(filename, stopKey)

    # 将新的文章插入到Root中
    load_data_2_root(data, model)

    result, add_word = model.find_word()

    # 如果想要调试和选择其他的阈值，可以print result来调整
    # 前后效果对比
    with open(filename, encoding="utf-8") as f:
        test_sentence = f.read()

    jieba_out = [x for x in jieba.cut(test_sentence) if x not in stopKey and len(x) != 1]   # jieba的分词结果
    # 这种方式分词后，再去掉jieba分词的结果（也就是发现的新词）
    # add_word是一个字典{word: score}
    results = [w for w in add_word if w not in jieba_out and len(w) != 1 and w not in stopKey]

    # 结果保存
    results_path = r"./results/result_3"
    if not os.path.exists(results_path):
        os.makedirs(results_path, exist_ok=True)

    result_file_name = os.path.basename(filename)
    result_file_path = os.path.join(results_path, result_file_name)
    with open(result_file_path, "w", encoding="utf-8") as f:
        for res in results:    # 结果是按照score从高到低排序了的
            f.write("{}\n".format(res))
    b = time.time()
    print("{}整体用时：{:.2f}\n".format(filename, b - a))


if __name__ == "__main__":

    model_name = "./data/root.pkl"
    stopwords = get_stopwords()
    if os.path.exists(model_name):
        model = load_model(model_name)
    else:
        dict_name = r"./data/dict.txt"
        word_freq = load_dictionary(dict_name)
        model = TrieNode('*', word_freq)
        save_model(model, model_name)

    root_dir = r"./data/preprocessing_data"
    files_path = glob.glob(root_dir + "/*.txt")
    pool = multiprocessing.Pool(4)
    for file_path in files_path:
        pool.apply_async(newWordFind, (file_path, model, stopwords))
    print("-----------start-----------")
    pool.close()
    pool.join()
    print("-----------end-----------")


