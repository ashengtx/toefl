# _*_ coding: utf-8 _*_
import re, json 
import hashlib
import requests
from urllib.parse import quote, urlencode
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from utils import *

from PIL import Image


"""
第一步，验证码图片
"""
url = "https://toefl.etest.net.cn/cn" 
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}


def md5_encode(string):
    m = hashlib.md5()
    m.update(string.encode('utf8'))
    v=m.hexdigest()
    return v

def pwd_encode(pwd, username, captcha_code):
    c1 = md5_encode(pwd+username)
    return md5_encode(c1+captcha_code.lower())

def get_html_raw(url):
    req = Request(url, headers=headers)  
    html = urlopen(req).read().decode('gbk')
    return html

def get_captcha():
    url1 = "https://toefl.etest.net.cn/cn/14972602669990.7574693705371078VerifyCode3.jpg"
    urlretrieve(url1, "captcha.jpg") # 将验证码图片存到本地
    #print(get_html_raw(url1), file=foutput)
    #print(get_html_raw(url1))
    image = Image.open('captcha.jpg')
    image.show()
    return image

def login():

    cookies = get_cookie()

    foutput = open("output.txt", 'w', encoding='utf8')
    get_captcha()
    captcha_code = input("please enter captcha code: ")
    print(captcha_code)
    username = ''
    pwd = ""
    password = pwd_encode(pwd, username, captcha_code)
    params = {'username':username,
              '__act':'__id.24.TOEFLAPP.appadp.actLogin',
              'password':password,
              'LoginCode':captcha_code,
              'btn_submit.x':18,
              'btn_submit.y':10}
    post_url = "https://toefl.etest.net.cn/cn/TOEFLAPP"
    r = requests.post(post_url, data=params, headers=headers)
    print(r.content.decode('gbk'), file=foutput)
    responseObj = BeautifulSoup(r.content, 'html.parser')

def get_cookie():
    r = requests.get(url)
    return r.cookies

if __name__ == '__main__':
    login()
    #get_cookie()
