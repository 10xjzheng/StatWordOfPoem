# coding=utf8
import requests
from sys import argv
from bs4 import BeautifulSoup
import re, time
import aiohttp
import asyncio
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import jieba


async def do_task(domain, url, f):
    print(url)
    async with aiohttp.ClientSession() as session:  # 获取session
        async with session.request('GET', url) as resp:  # 提出请求
            if resp.status != 200:
                html = ''
            else:
                html = await resp.read()
    if html != '':
        soup = BeautifulSoup(html, 'html.parser')
        for h in soup.select('h3>a'):
            url = ''.join([domain, h.get('href')])
            async with aiohttp.ClientSession() as session:  # 获取session
                async with session.request('GET', url) as resp:  # 提出请求
                    if resp.status != 200:
                        phtml = ''
                    else:
                        phtml = await resp.read()
            if phtml == '':
                continue
            soup = BeautifulSoup(phtml, 'html.parser')
            # title = str(soup.select('.shici-title')[0].get_text())
            poem = soup.select('.shici-content>.para')
            if len(poem) == 0:
                poem = str(soup.select('.shici-content')[0].get_text())
            else:
                poem = str(soup.select('.shici-content>.para')[0].get_text())
            segList = jieba.cut(poem, cut_all=True)
            f.write(' '.join(segList))
def main():
    domain = 'http://www.shicimingju.com'
    authorUrl = domain + '/chaxun/zuozhe_list/'
    if len(argv) < 2:
        print('Please input an author name!')
        exit()

    print(authorUrl + argv[1])
    response = requests.get(authorUrl + argv[1])
    soup = BeautifulSoup(response.content, 'html.parser')
    firstUrl = soup.select('h3>a')
    if len(firstUrl) == 0:
        print('The author does\'t exist!')
        exit()
    poemUrl = firstUrl[0].get('href')
    print(poemUrl)
    poemNum = re.findall('\d+', poemUrl)[0]
    print(poemNum)
    page = 1
    pageUrls = []
    while page < 88:
        pageUrl = ''.join([domain, poemUrl]) if (page == 1) else \
            ''.join([domain, poemUrl]).replace(poemNum, poemNum + '_' + str(page))
        pageUrls.append(pageUrl)
        page += 1
    with open('poem.txt', 'a+', encoding='utf-8') as f:
        f.seek(0)
        f.truncate()  # 清空文件
        loop = asyncio.get_event_loop()           # 获取事件循环
        tasks = [do_task(domain, url, f) for url in pageUrls]  # 把所有任务放到一个列表中
        loop.run_until_complete(asyncio.wait(tasks)) # 激活协程
        loop.close()  # 关闭事件循环

def draw():
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
    plt.show()

if __name__ == '__main__':
    start = time.time()
    main()  # 调用方
    draw()
    print('总耗时：%.5f秒' % float(time.time()-start))
