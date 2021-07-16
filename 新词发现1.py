import os
import glob
import shutil
import jieba
import jieba.posseg
from NewWordDiscovery import new_word_discover  # 新词发现程序


def data_process(file: str, save_path: str, stopwords: list):
    """
        把传进来的txt进行jieba分词，然后根据词性、停用词去掉部分内容，
    再把每行去掉后的内容些会到同名txt并存在save_path
    :param file: 类似'./sample/123.txt',一个txt文本的路径
    :param save_path: 类似'./temp_txt'
    :param stopwords:停用词列表
    :return:None
    """

    # 不需要的词性
    """
    jieba属性：(下面这些属性的词可以不要)
    x:字符串 (一些空格加一个字母的无意义东西)
    r:代词  （这种，为此）
    c:连词  （即为，此时..）
    y:语气词
    o:拟声词
    w:标点符号
    """
    no_pos = ['x', 'r', 'c', 'y', 'o', 'w']
    save_file_path = os.path.join(save_path, os.path.basename(file))
    fp = open(save_file_path, 'w', encoding="utf-8")
    with open(file, encoding="utf-8") as f:
        for line in f:
            line = jieba.posseg.cut(line.strip())
            # 去掉停用词，以及去掉不需要的词性
            word = [w.word for w in line if w.word not in stopwords and w.flag not in no_pos]
            print("".join(word), file=fp, flush=True)
    fp.close()


def result_process(txt_path, csv_path, save_path, stopwords: list):
    """
    把一个txt文本得到的新词从csv_path读取出来，处理并只保留词；
    再把这个txt文本(可以是与处理前或是原始文本，下面用的有处理后)用jieba分词；
    再把csv得到的新词与之去重处理，再一个词一行写到同名txt文件，放进save_path
    :param txt_path: like this -> "./smaple/123.txt"
    :param csv_path: like this -> "./result/123.txt.csv"
    :param save_path:like this -> "./newWord_output", 最终的结果保存地址
    :param stopwords:停用词列表
    :return:None
    """
    # filename = r"./data/merge_line_data2(来源于运达扫描桥隧技术).txt"
    # result_path = r"./result/NewWordDiscovery_merge_line_data2(来源于运达扫描桥隧技术).txt_20210416161100.csv"

    with open(csv_path) as f:
        lines = f.readlines()
    finall = []
    for line in lines[1:]:
        line = line.strip().split(',')
        line = [w for w in line if (not w.isdigit() and w and w.find('.') == -1)]
        finall.extend(line)

    with open(txt_path, encoding="utf-8") as f:
        test_sentence = f.read()
    jieba_out = [x for x in jieba.cut(test_sentence) if len(x) != 1]  # jieba的分词结果

    result = [w for w in finall if (w not in jieba_out and len(w) != 1 and w not in stopwords)]  # 新词发现的最终结果

    # 结果保存
    result_file_name = os.path.basename(txt_path)
    result_file_path = os.path.join(save_path, result_file_name)
    with open(result_file_path, "w", encoding="utf-8") as f:
        for res in result:  # 结果是按照score从高到低排序了的
            f.write("{}\n".format(res))


def main():
    # 原始所有txt所在文件夹的路径
    original_path = r"./data/original_data"
    # 结果保存路径
    result_path = r"./results/result_1"
    if not os.path.exists(result_path):
        os.makedirs(result_path, exist_ok=True)
    # 停用词
    stopwords_path = r"data/stopWord.txt"
    stopwords = [word.strip() for word in open(stopwords_path, encoding="utf-8").readlines()]

    # 上面三个路径可以传进来，下面的不管；且不要用 result 这个名字作为文件夹名

    # 数据通过词性做了预处理筛选的结果(这个结果还要直接用到另外两个方法当做原数据)
    prepro_path = r"./data/preprocessing_data"
    if not os.path.exists(prepro_path):
        os.makedirs(prepro_path, exist_ok=True)

    # 主要程序的开始，上面可以写进配置文件之类的
    files_abspath = glob.glob(original_path + "/*.txt")
    for file in files_abspath:
        # 数据预处理，并把结果放进临时文件夹
        data_process(file, prepro_path, stopwords)
        file_process_path = os.path.join(prepro_path, os.path.basename(file))

        # 新词发现的主要程序，会把结果写进csv,存到同级的"./result"中
        new_word_discover(file_process_path, f_encoding='utf-8', f_data_col=0, f_txt_sep='\n',
                          n_gram=7, p_min=5, co_min=100, h_min=1.5)

        # 预处理后的txt路径，并且根据此得到的csv文件
        temp_txt_path = os.path.join(prepro_path, os.path.basename(file))
        temp_csv_path = os.path.join(r"./result", os.path.basename(file) + ".csv")
        # 最后把csv文件统计整理一下，再跟jieba的分词去重一下
        result_process(temp_txt_path, temp_csv_path, result_path, stopwords)
        print("{} 已经完成\n".format(file))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("错误信息：%s" % e)
    # 无论怎样，最后把临时文件夹都要删除
    finally:
        # `result`是新词发现存放的csv，`temp`是产生csv过程的临时文件夹(我里面做了删除，以防万一)
        # 若想看csv文件，就把"result"从下面列表移开(这个"result"就不要去动它，外面也不要有同名的)
        for path in ["result", "temp"]:
            if os.path.exists(path):
                shutil.rmtree(path)
