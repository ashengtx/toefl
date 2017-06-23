import jieba.analyse
import re, nltk, string
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

'''
爬取 http://www.cnblogs.com/AlexNull/ 下所有博文
每篇博文提取三个关键词
所有博文词频统计
'''

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
start_url = 'http://www.cnblogs.com/AlexNull/'

def get_html(url):
    req = Request(url, headers=headers)  
    html = urlopen(req).read().decode('utf8')
    return html

def get_article_link(html):
    pattern = r'href="(http://www\.cnblogs\.com/AlexNull/p/.*?\.html)"'
    article = re.findall(pattern, html)
    return article

def get_next_page(html):
    pattern1 = r'<a.*?>.*?</a>'
    all_link = re.findall(pattern1, html)
    pattern2 = r'<a href="(.*)">下一页</a>'
    next_page = []
    for link in all_link:
        res = re.findall(pattern2, link)
        if res:
            next_page = res
    #print('next page ', next_page)
    if next_page == []:
        return None
    return get_html(next_page[0])

def get_all_article_link(html):
    links = []
    cur_page = html
    while cur_page is not None:
        article = get_article_link(cur_page)
        #print(article)
        links.extend(article)
        cur_page = get_next_page(cur_page)
    return set(links)

def get_post_title(bsObj):
    return bsObj.find(id="cb_post_title_url").get_text()

def get_post_body(bsObj):
    return bsObj.find(id='cnblogs_post_body').get_text()

def get_keyword(text):
    res = jieba.analyse.extract_tags(text, topK=20, withWeight=True, allowPOS=())
    return res[0:5]

def del_punc(astr):
    pattern = r'[,.;:，。；：\/\(\)\{\}]'
    return re.sub(pattern, '', astr)

def get_freqdist():
    html = get_html(start_url)
    links = get_all_article_link(html)
    words = []
    for link in links:
        html = get_html(link)
        bsObj = BeautifulSoup(html, 'html.parser')
        body = get_post_body(bsObj)
        #body = del_punc(body)
        seg_list = jieba.cut(body)
        words.extend(seg_list)
    text = nltk.Text(words)
    fdist = nltk.FreqDist(text)
    return fdist

def get_keywords():
    html = get_html(start_url)
    links = get_all_article_link(html)
    words = []
    with open('alex_keyword.txt', 'w', encoding='utf8') as fl:
        for link in links:
            html = get_html(link)
            bsObj = BeautifulSoup(html, 'html.parser')
            title = get_post_title(bsObj)
            print(title, file=fl)
            body = get_post_body(bsObj)
            res = jieba.analyse.extract_tags(body, topK=20, withWeight=True, allowPOS=())
            for tp in res[0:5]:
                print(tp, file=fl)
            print('--------------------------------', file=fl)
#提取关键词 res = jieba.analyse.extract_tags(text, topK=20, withWeight=True, allowPOS=())

if __name__ == '__main__':
    get_keywords()

