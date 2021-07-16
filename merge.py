import os
from itertools import chain

"""
这个是把三个方法的结果融合的到最后的结果

"""

"""
    result_1:结果，2个字的不要；其它的都还可以
"""


"""
    result_2:是新词发现2.py的结果，这个2个字符、3个字符的效果都很差，直接不要；
4、5、6、7个字个字的的还勉强
"""


"""
    result_3:是哪个量很大,根据评分排序了的，应该取前百分之多少的(自己判断)；然后这里这面2个字的很少，且效果非常不好，直接不要;
3个字的从直观效果来看还可以；4个字的前面还可以，后面就一般，不知道要不要单独再取舍一波
还要删掉  # 删掉`图1.1`或`1.1所示`这样的数据；超过8个字的也不要(很不好);开头结尾是数字的也不要

"""


# 所有结果的一个总的路径
root_dir = r"./results"

# 每3方法的txt结果的上一级文件夹名称
middle_results = ["./result_1", "./result_2", "./result_3"]

if __name__ == '__main__':
    """result = {"书1": [result_1结果，result_2结果, result_3结果], "书2"：[result_1结果，result_2结果, result_3结果]...}"""
    result = dict()
    # 所有txt文本的names
    txts_name = os.listdir(os.path.join(root_dir, middle_results[0]))
    for file_name in txts_name:
        # # 同一个文件，使用3个方法得到的3中结果的
        a_file_out = []
        # i也就对应了3种方法
        for i, middle_result in enumerate(middle_results):
            temp_path = os.path.join(root_dir, middle_result, file_name)
            with open(temp_path, encoding="utf-8") as f:
                lines = [line.strip() for line in f]
                # 2个字符的词不要(效果都不好);删掉`图1.1`或`1.1所示`这样的数据；开头结尾是数字的也不要;结尾是字母的也不要
                lines = [line for line in lines if (len(line) > 2 and line[0] != "图" and not line.endswith("所示")
                                                    and not line[-1].isdigit() and not line[0].isdigit()
                                                    and not (65 <= ord(line[-1]) <= 122))]

            # 对于"result_1"中的结果:
            if i == 0:
                pass
            # 对于"result_2"中的结果:
            elif i == 1:
                lines = [line for line in lines if len(line) != 3]
            # 对于"result_3"中的结果:
            elif i == 2:
                # 取前10%，详细可见README
                lines = lines[:round(len(lines) * 0.1)]
                # 超过8个字的也不要(很不好);
                lines = [line for line in lines if len(line) < 8]
            a_file_out.append(lines)
        result[file_name] = a_file_out
    print("***********************************************")

    # 最终结果保存地址
    final_result_path = r"./final_result"
    if not os.path.exists(final_result_path):
        os.mkdir(final_result_path)

    for key, value in result.items():
        # 把不同方法的结果融合在一起，去重
        new_words = set(chain(*value))
        new_words = sorted(list(new_words), key=len)
        # 还是以同名txt写入最终结果
        fp = open(os.path.join(final_result_path, key), "w", encoding="utf-8")
        for new_word in new_words:
            print(new_word, file=fp, flush=True)
    print("处理完毕！")
