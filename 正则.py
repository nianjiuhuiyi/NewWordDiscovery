import re
import os

"""
问：jieba分词后，只想提出里面的中文分词，不要标点符号
答：我是用正则表达式处理的，
new_sentence = re.sub(r'[^\u4e00-\u9fa5]', ' ', old_sentence)
然后再进行分词的, \u4e00-\u9fa5这个是utf-8中，中文编码的范围

匹配中文标点符号： [\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b] 
该表达式可以识别出： 。 ； ， ： “ ”（ ） 、 ？ 《 》 这些标点符号。



# 正则表达式转换，只提取汉字、数字、字母
        re_clean = re.compile('[^\u4e00-\u9fa5 a-zA-Z0-9]')
        # 将多个空格 替换成一个空格
        re_sub = re.compile(' +')
        
        # 正则清洗
        corpus = re.sub(re_clean, ' ', corpus)
        corpus = re.sub(re_sub, ' ', corpus)
"""

root = r"C:\Users\dell\Desktop\txts"

files = os.listdir(root)
for file in files:
    path = os.path.join(root, file)
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    fp = open(f"{file}", "w", encoding="utf-8")
    for line in lines:
        line = line.strip()
        # print(line)
        # 这里就是匹配中文汉字、数字、字母，去掉乱码

        # 下面这四行是一样的效果
        # re_clean = re.compile('[^\u4e00-\u9fa5 a-zA-Z0-9]')
        # re_sub = re.compile(' +')
        # new_sentence = re.sub(re_clean, ' ', line)
        # new_sentence = re.sub(re_sub, ' ', new_sentence)

        # # 提取中文字+数字，好像可以不要逗号，就以空格分开(或者不要空格)，就写r'[^\u4e00-\u9fa5 0-9]'
        new_sentence = re.sub(r'[^\u4e00-\u9fa5 0-9A-z ，。；、.,]', ' ', line)

        print(new_sentence)
        print("***********************")
        print(new_sentence, file=fp, flush=True)
