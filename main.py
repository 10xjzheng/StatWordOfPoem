# coding=utf8
import requests
from bs4 import BeautifulSoup
import jieba
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from sys import argv
import re
domain = 'http://www.shicimingju.com'
authorUrl = domain + '/chaxun/zuozhe_list/'
if len(argv) < 2:
    print('Please input an author name!')
    exit()

response = requests.get(authorUrl+argv[1])
soup = BeautifulSoup(response.content, 'html.parser')
firstUrl = soup.select('h3>a')
if len(firstUrl) == 0:
    print('The author does\'t exist!')
    exit()
poemUrl = firstUrl[0].get('href')
poemNum = re.findall('\d+', poemUrl)[0]
with open('poem.txt', 'a+', encoding='utf-8') as f:
    f.seek(0)
    f.truncate()  # 清空文件
    page = 1
    while True:
        pageUrl = ''.join([domain, poemUrl]) if (page == 1) else ''.join([domain, poemUrl]).replace(poemNum, poemNum + '_' + str(page))
        response = requests.get(pageUrl)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.content, 'html.parser')
        for h in soup.select('h3>a'):
            url = ''.join([domain, h.get('href')])
            html = requests.get(url)
            soup = BeautifulSoup(html.content, 'html.parser')
            # title = str(soup.select('.shici-title')[0].get_text())
            poem = soup.select('.shici-content>.para')
            if len(poem) == 0:
                poem = str(soup.select('.shici-content')[0].get_text())
            else:
                poem = str(soup.select('.shici-content>.para')[0].get_text())
            # f.write(''.join(['《', title, '》', '\n', poem.strip(), '\n']))
            segList = jieba.cut(poem, cut_all=True)
            f.write(' '.join(segList))
        page += 1
# 画图
# 读文件
text = open('poem.txt', encoding='utf-8').read()
# 读图片
alice_mask = np.array(Image.open("alice_mask.png"))

stopwords = set(STOPWORDS)
stopwords.add("said")

wc = WordCloud(background_color="white", font_path='fzjl.ttf', max_words=2000, mask=alice_mask,
               stopwords=stopwords, contour_width=3, contour_color='steelblue')

# 生成云
wc.generate(text)

# 保存
wc.to_file(argv[1] + ".png")

# 展示图片
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.figure()
plt.imshow(alice_mask, cmap=plt.cm.gray, interpolation='bilinear')
plt.axis("off")
plt.show()

