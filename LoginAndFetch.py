#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib2
import cookielib
import urllib
import re
import ssl
import sys
from bs4 import BeautifulSoup


def loadStatusPage(opener):
    request = urllib2.Request('https://supplier.rt-mart.com.cn/php/scm_orders_form_1.php?status=1')
    #print opener.open(request).read()
    resp = opener.open(request).read().decode('gbk')
    soup = BeautifulSoup(resp,"html.parser")

    #输出第一个 title 标签
    print soup.title
    table = soup.form.table.extract()
    orderTree = {}
    for element in table.next_elements:
        if element.name == 'li':
            print element.get_text()
            store = re.search(r".+[店]".decode('utf-8'),element.get_text()).group(0)
            subtable = element.find_next("table").extract()
            for subelement in subtable.find_all("a"):
                if orderTree.has_key(store):
                    orderTree[store].append({'orderNo':subelement.get_text(),'url':subelement['href']})
                else:
                    orderTree[store] = [{'orderNo':subelement.get_text(),'url':subelement['href']}]


    return orderTree

def loadDetialPage(opener,orderTree):

    for orderTreeK,orderTreeV in orderTree.items():
        for order in orderTreeV:
            url ='https://supplier.rt-mart.com.cn/php/'+order['url']
            request = urllib2.Request(url)
            #print opener.open(request).read()
            resp = opener.open(request).read().decode('gbk')
            soup = BeautifulSoup(resp,"html.parser")
            trs = soup.body.find_all_next('tr',align="center")
            print orderTreeK+'--->'+order['orderNo']
            del trs[0]
            itemDetials = []
            for tr in trs:
                itemDetial = {
                    "itemNO":tr.contents[1].get_text(),
                    "receiveNO":tr.contents[2].get_text(),
                    "unitInvoicePrice":tr.contents[3].get_text(),
                    "unit":tr.contents[4].get_text(),
                    "orderCount":tr.contents[5].get_text(),
                    "receiceCount":tr.contents[6].get_text()
                }
                itemDetials.append(itemDetial)
            order['detials']=itemDetials




def login():
    '''模拟登录'''
    #关闭SSL验证
    ssl._create_default_https_context = ssl._create_unverified_context
    # 防止中文报错
    CaptchaUrl = "https://supplier.rt-mart.com.cn/code.php"
    PostUrl = "https://supplier.rt-mart.com.cn/php/scm_login_check.php"
    # 验证码地址和post地址
    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    # 将cookies绑定到一个opener cookie由cookielib自动管理
    username = '123456'
    password = '123455'
    # 用户名和密码
    picture = opener.open(CaptchaUrl).read()
    # 用openr访问验证码地址,获取cookie
    local = open('identifying_code.jpg', 'wb')
    local.write(picture)
    local.close()
    # 保存验证码到本地
    SecretCode = raw_input('type identifying code:')
    print SecretCode
    # 打开保存的验证码图片 输入

    postData = {
        'area':5,
        'image.x':13,
        'image.y':9,
        'userid':username,
        'passwd':password,
        'checkstr':SecretCode
    }
    # 根据抓包信息 构造表单
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Content-Type':'application/x-www-form-urlencoded',
        'Host':'supplier.rt-mart.com.cn',
        'Origin':'https://supplier.rt-mart.com.cn',
        'Referer':'https://supplier.rt-mart.com.cn/php/r_index.php',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
    }
    # 根据抓包信息 构造headers
    data = urllib.urlencode(postData)
    # 生成post数据 ?key1=value1&key2=value2的形式
    request = urllib2.Request(PostUrl, data, headers)
    # 构造request请求
    try:
        print request
        response = opener.open(request)
        #result = response.read().decode('gb2312')
        result = response.read()
        # 由于该网页是gb2312的编码，所以需要解码
        print result
        if 'scm_main.php' in result:
            print 'ok'
            return opener
    # 打印登录后的页面
    except urllib2.HTTPError, e:
        print e.code
        return None

default_encoding = 'utf-8'

opener = login()
if opener is not None:
    print 'ookk'
    orderTree = loadStatusPage(opener)
    loadDetialPage(opener,orderTree)
    output = open('data.txt', 'w')
    for orderTreeK,orderTreeV in orderTree.items():
        for order in orderTreeV:
            for detial in order['detials']:
                output.write(orderTreeK.encode("utf-8")+'|'+order['orderNo'].encode("utf-8")+'|'+detial['itemNO'].encode("utf-8")+'|'+detial['receiveNO'].encode("utf-8")+'|'+detial['unitInvoicePrice'].encode("utf-8")+'|'+detial['unit'].encode("utf-8")+'|'+detial['orderCount'].encode("utf-8")+'|'+detial['receiceCount'].encode("utf-8")+'\n')

    output.write('\n')
    output.close()
