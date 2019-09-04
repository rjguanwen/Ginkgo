# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/28 14:00

""" 百度翻译服务调用 """

import http.client
import hashlib
import urllib.parse
import random
import json
from config import BAIDU_TRANSLATOR_CLIENT_ID, BAIDU_TRANSLATOR_CLIENT_SECRET


def translate_by_baidu(text, from_lang, to_lang):
    """ 调用百度翻译服务，实现对文本的翻译 """
    httpClient = None
    myurl = '/api/trans/vip/translate'
    salt = random.randint(32768, 65536)

    sign = BAIDU_TRANSLATOR_CLIENT_ID + text + str(salt) + BAIDU_TRANSLATOR_CLIENT_SECRET
    m1 = hashlib.md5()
    m1.update(sign.encode("utf-8"))
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + BAIDU_TRANSLATOR_CLIENT_ID + '&q=' + urllib.parse.quote(text) + \
            '&from=' + from_lang + '&to=' + to_lang + '&salt=' + str(salt) + '&sign=' + sign
    result_text = ''
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_text = response.read().decode()
        result_json = json.loads(result_text)
        result = result_json.get('trans_result')[0].get('dst')
        # print('翻译结果为：==>%s' % result_text)
    except Exception:
        print('发生异常……')
    finally:
        if httpClient:
            httpClient.close()
        return result


if __name__ == '__main__':
    text = 'apple'
    from_lang = 'en'
    to_lang = 'zh'
    result = translate_by_baidu(text, from_lang, to_lang)
    print(result)
