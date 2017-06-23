# _*_ coding: utf-8 _*_
import re
from urllib import parse, request
from urllib.error import HTTPError, URLError
import http.cookiejar
from PIL import Image
import time
import random
import json
import hashlib
import pytesseract
from bs4 import BeautifulSoup


# 建立LWPCookieJar实例，可以存Set-Cookie3类型的文件。
# 而MozillaCookieJar类是存为'/.txt'格式的文件
cookie = http.cookiejar.LWPCookieJar('cookie')
# 若本地有cookie则不用再post数据了
try:
    cookie.load(ignore_discard=True)
except IOError:
    print('Cookie未加载！')

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
           "Host": "toefl.etest.net.cn",
           "Referer": "https://toefl.etest.net.cn/cn",
           }
opener = request.build_opener(request.HTTPCookieProcessor(cookie))
# 给openner添加headers, addheaders方法接受元组而非字典
opener.addheaders = [(key, value) for key, value in headers.items()]

account = '3915741'
secret = "Jiatianyu0116"
month = "201710"
province = "Beijing"


base_url = "https://toefl.etest.net.cn/cn/"
home_url = base_url + 'MyHome/?'

rec_wrong = 0
rec_total = 0

foutput = open("output.txt", 'w', encoding='utf8')


def md5_encode(string):
    m = hashlib.md5()
    m.update(string.encode('utf8'))
    v=m.hexdigest()
    return v

def pwd_encode(pwd, username, captcha_code):
    c1 = md5_encode(pwd+username)
    return md5_encode(c1+captcha_code.lower())

def my_open(url, post_data=''):
    try:
        if post_data:
            res = opener.open(url, post_data).read()
        else:
            res = opener.open(url).read()
    except HTTPError as e:
        #print(e)
        print("系统很忙")
        return False
    except URLError as e:
        print(e)
        print(e.reason)
        return False
    else:
        #print('这个网站真垃圾！！')
        return res

def get_captcha():
    """
    获取验证码本地显示
    返回你输入的验证码
    """
    t = int(time.time())*1000
    r = random.random()
    string = "%13d%.17f"%(t, r)

    captcha_url = base_url+string+"VerifyCode3.jpg"
    # 获取验证码也用同一个opener
    image_data = my_open(captcha_url)
    # 系统繁忙
    if not image_data:
        return False

    with open('captcha.jpg', 'wb') as f:
        f.write(image_data)
    im = Image.open('captcha.jpg')
    im.show()
    captcha = input('本次登录需要输入验证码： ')
    return captcha

def get_captcha2(captcha_url):
    """
    查询考位需再次输入验证码
    """
    image_data = my_open(captcha_url)
    if not image_data:
        print("无法获取查询考位的验证码")
        return False
    with open('captcha2.jpg', 'wb') as f:
        f.write(image_data)
    img = Image.open('captcha2.jpg')
    return img
    #im.show()
    #captcha = input('查询考位需要输入验证码： ')
    #return captcha

def captcha_recognize(img):
    """
    输入验证码，自动识别，返回结果
    """
    img = img.convert('RGBA')  # 转换为RGBA
    pix = img.load()  # 读取为像素

    yuzhi = 150
    for y in range(img.size[1]):  # 二值化处理，这个阈值为150
        for x in range(img.size[0]):
            if pix[x, y][0] > yuzhi or pix[x, y][1] > yuzhi or pix[x, y][2] > yuzhi:
                pix[x, y] = (0, 0, 0, 255)
            else:
                pix[x, y] = (255, 255, 255, 255)
    img.save("temp.jpg")
    text=pytesseract.image_to_string(Image.open("temp.jpg"), config="-psm 7")
    text = char_filter(text)
    if len(text) == 0:
        print(text)
        print("无法识别验证码")
        return 0
    #global rec_total += 1
    return text.lower()

def char_filter(string):
    """
    只保留字母和数字
    """
    res = ""
    for c in string:
        if (c <= '9' and c >= '0') or (c <= "z" and c >= "A"):
            res += c
    return res


def login(username, password):
    """
    输入自己的账号密码，模拟登录知乎
    """
    #print("尝试模拟登录")
    login_url = base_url + "TOEFLAPP"
    data = {'username':username,
            '__act':'__id.24.TOEFLAPP.appadp.actLogin',
            'password':'',
            'LoginCode':'',
            'btn_submit.x':18,
            'btn_submit.y':10}
    # 获取验证码        
    captcha_code = get_captcha()
    if not captcha_code:
        return False
    data['LoginCode'] = captcha_code
    # 密码加密
    pwd = pwd_encode(password, username, captcha_code)
    data['password'] = pwd

    #print(data)
    post_data = parse.urlencode(data).encode('utf-8')
    # 异常处理
    r = my_open(login_url, post_data)
    if not r:
        return False

    #print((json.loads(result))['msg'])
    # 保存cookie到本地
    cookie.save(ignore_discard=True, ignore_expires=True)

    res = my_open(home_url)
    if not res:
        return False

    if "修改密码" in res.decode('gbk'):
        print("登录成功")
        return True
    else:
        return False
    #print(res, file=foutput)

def logout():
    logout_url = base_url + "?__id=TOEFLAPP.EUSessionAdp.Logout"
    res = opener.open(logout_url).read().decode('gbk')
    print("自动登出")
    print(res, file=foutput)
    return 

def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    res = my_open(home_url)
    if not res:
        return False
    if "修改密码" in res.decode('gbk'):
        return True
    else:
        return False

def get_CityTable(try_times=1):
    foutput = open("cititable.txt", 'w', encoding='utf8')
    max_try_times = 50
    city_url = base_url + "CityAdminTable"
    res = my_open(city_url)
    if not res:
        print("查询城市列表失败")
        if try_times > max_try_times:
            return False
        else:
            try_times += 1
            print("第%d尝试查询城市列表"%try_times)
            time.sleep(3)
            foutput.close()
            return get_CityTable(try_times)
    html = res.decode("gbk")
    if "点击更换验证码" in html:
        print("查询城市列表成功")
        return html
    else:
        print(html, file=foutput)
        foutput.close()
        print("没有获取正确的城市列表页面")
        return False

def get_seat_table(try_times=1):
    max_try_times = 50

    res_text = get_CityTable()
    if not res_text:
        if try_times > max_try_times:
            print("超过定义的最大查询考位次数")
            return False
        else:
            try_times += 1
            print("第%d尝试查询考位"%try_times)
            time.sleep(7)
            return get_seat_table(try_times)
    captcha_name = re.findall(r'<img src="/cn/(.*?)" title="点击更换验证码".*?/>', res_text)[0]
    captcha_url = base_url + captcha_name
    #print(captcha_url)
    captcha_img = get_captcha2(captcha_url)
    if not captcha_img:
        if try_times > max_try_times:
            print("超过定义的最大查询考位次数")
            return False
        else:
            try_times += 1
            print("第%d尝试查询考位"%try_times)
            time.sleep(7)
            return get_seat_table(try_times)
    captcha_code = captcha_recognize(captcha_img)

    print("自动识别出来的验证码是 ", captcha_code)
    if len(captcha_code) < 4:
        print("识别出的验证码小于4位，识别错误")
        if try_times > max_try_times:
            print("超过定义的最大查询考位次数")
            return False
        else:
            try_times += 1
            print("第%d尝试查询考位"%try_times)
            time.sleep(7)
            return get_seat_table(try_times)

    search_url = base_url + "SeatsQuery?mvfAdminMonths="+month+"&mvfSiteProvinces="+province+"&whichFirst=AS&afCalcResult="+captcha_code+"&__act=__id.34.AdminsSelected.adp.actListSelected&submit.x=59&submit.y=8"
    time.sleep(3)
    
    res = my_open(search_url)
    if not res:
        print("网站错误")
        if try_times > max_try_times:
            print("超过定义从最大查询考位次数")
            return False
        else:
            try_times += 1
            print("第%d尝试查询考位"%try_times)
            time.sleep(7)
            return get_seat_table(try_times)

    html = res.decode("gbk")
    if "请输入验证码" in html:
        print("验证码识别错误！！！")
        if try_times > max_try_times:
            print("超过定义的最大查询考位次数")
            return False
        else:
            try_times += 1
            print("第%d尝试查询考位"%try_times)
            time.sleep(7)
            return get_seat_table(try_times)

    if "提示：这个值小于" in html:
        second = re.findall(r'<p><img src=".*?"> \(提示：这个值小于(.*?)\)</p>', html)[0]
        print("查询考位失败，网站需要你%s秒之后再刷新"%second)
        if try_times > max_try_times:
            print("超过定义的最大查询考位次数")
            return False
        else:
            try_times += 1
            print("第%d尝试查询考位"%try_times)
            time.sleep(int(second))
            return get_seat_table(try_times)

    if "名额" in html:
        return html
    else:
        return False


def registration(try_times=1):
    max_try_times = 15
    res = get_seat_table()
    if not res:
        print("查询考位失败")
        return False
    print(res, file=foutput)
    seat_num = check_seat(res, month, province)

    if seat_num == 0:
        try_times += 1
        if try_times > max_try_times:
            print("考位一直为0")
            return False
        else:
            time.sleep(int(7))
            return registration(try_times)
    else:
        return auto_register(res)

def auto_register(html):
    print("现在模拟注册")
    obj = BeautifulSoup(html, 'html.parser')
    forms = obj.find('table', cellpadding='4').findAll('form')
    for form in forms:
        tds = form.findAll('td')
        seat_state = tds[4].get_text()
        if seat_state == '有名额':
            seat_code = tds[1].get_text()
            school = tds[2].get_text()
            print("准备注册如下考位：")
            print(seat_code, school, seat_state)
            return True
    print("名额不见了...")
    return False

def check_seat(html, month, province):
    obj = BeautifulSoup(html, 'html.parser')
    forms = obj.find('table', cellpadding='4').findAll('form')
    seat_num = 0
    for form in forms:
        tds = form.findAll('td')
        seat_state = tds[4].get_text()
        if seat_state == '有名额':
            seat_code = tds[1].get_text()
            school = tds[2].get_text()
            seat_num += 1
            #print(seat_code, school, seat_state)
    print("%s %s 共有%d个考位有名额"%(month, province, seat_num))
    return seat_num


if __name__ == '__main__':
    
    #account = input('输入账号：')
    #secret = input('输入密码：')
    
    #login(account, secret)
    print("验证是否已经登录")
    if isLogin():
        print("已登录")
        time.sleep(7)
        regist_state = registration()
    else:
        print("未登录")
        login_state = login(account, secret)
        n = 0
        while not login_state:
            if n > 50:
                print("can not login, try it later")
                quit()
            n += 1
            time.sleep(3)
            print("try to login %d time"%n)
            login_state = login(account, secret)
        time.sleep(7)
        regist_state = registration()
    if not regist_state:
        print("注册考位失败")
    else:
        print("注册考位成功")
