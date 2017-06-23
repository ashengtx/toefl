# _*_ coding: utf-8 _*_
import time
import math
import random
import re
from bs4 import BeautifulSoup

html = open("output.html", 'r', encoding='utf8').read()
obj = BeautifulSoup(html, 'html.parser')
#table = obj.findAll('table', cellpadding='4')
forms = obj.find('table', cellpadding='4').findAll('form')

seat_num = 0
for form in forms:
    tds = form.findAll('td')
    seat_state = tds[4].get_text()
    if seat_state == '有名额':
        seat_code = tds[1].get_text()
        school = tds[2].get_text()
        seat_num += 1
        print(seat_code, school, seat_state)
print("共有%d个考位有名额"%seat_num)
