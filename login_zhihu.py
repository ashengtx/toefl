import re
from urllib import parse, request
import http.cookiejar
from PIL import Image
import time
import json

# 建立LWPCookieJar实例，可以存Set-Cookie3类型的文件。
# 而MozillaCookieJar类是存为'/.txt'格式的文件
cookie = http.cookiejar.LWPCookieJar('cookie')
# 若本地有cookie则不用再post数据了
try:
    cookie.load(ignore_discard=True)
except IOError:
    print('Cookie未加载！')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36',
           "Host": "www.zhihu.com",
           "Referer": "https://www.zhihu.com/",
           }
opener = request.build_opener(request.HTTPCookieProcessor(cookie))
# 给openner添加headers, addheaders方法接受元组而非字典
opener.addheaders = [(key, value) for key, value in headers.items()]


def get_xsrf():
    """
    获取参数_xsrf
    """
    response = opener.open('https://www.zhihu.com')
    html = response.read().decode('utf-8')
    get_xsrf_pattern = re.compile(r'<input type="hidden" name="_xsrf" value="(.*?)"')
    _xsrf = re.findall(get_xsrf_pattern, html)[0]
    return _xsrf


def get_captcha():
    """
    获取验证码本地显示
    返回你输入的验证码
    """
    t = str(int(time.time() * 1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    # 获取验证码也用同一个opener
    image_data = opener.open(captcha_url).read()
    with open('cptcha.gif', 'wb') as f:
        f.write(image_data)
    im = Image.open('cptcha.gif')
    im.show()
    captcha = input('本次登录需要输入验证码： ')
    return captcha


def login(username, password):
    """
    输入自己的账号密码，模拟登录知乎
    """
    # 检测到11位数字则是手机登录
    if re.match(r'\d{11}$', account):
        url = 'http://www.zhihu.com/login/phone_num'
        data = {'_xsrf': get_xsrf(),
                'password': password,
                'remember_me': 'true',
                'phone_num': username
                }
    else:
        url = 'https://www.zhihu.com/login/email'
        data = {'_xsrf': get_xsrf(),
                'password': password,
                'remember_me': 'true',
                'email': username
                }

    # 若不用验证码，直接登录
    post_data = parse.urlencode(data).encode('utf-8')
    r = opener.open(url, post_data)
    result = r.read().decode('utf-8')
    # 打印返回的响应，r = 1代表响应失败，msg里是失败的原因
    # 要用验证码，post后登录
    if (json.loads(result))["r"] == 1:
        data['captcha'] = get_captcha()
        post_data = parse.urlencode(data).encode('utf-8')
        r = opener.open(url, post_data)
        result = r.read().decode('utf-8')
        print((json.loads(result))['msg'])
    # 保存cookie到本地
    cookie.save(ignore_discard=True, ignore_expires=True)


def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = 'https://www.zhihu.com/settings/profile'
    # 获得真实网址，可能重定向了
    actual_url = opener.open(url).geturl()
    if actual_url == 'https://www.zhihu.com/settings/profile':
        return True
    else:
        return False


if __name__ == '__main__':
    if isLogin():
        print('您已经登录')
    else:
        account = input('输入账号：')
        secret = input('输入密码：')
        login(account, secret)
