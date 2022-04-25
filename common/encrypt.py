# -*- coding = utf-8 -*-
# 知乎加密
import hashlib
import random
import os
import execjs


COOKIE_LIST = [
    '"AvAQDHN4mxSPTtVyJn9kQSMi43V1kPWH_qc=|1646810832"',
    '"ANBQa9czlRSPThnOgiTPFdnLtVpygBC7eWk=|1646390194"'
]


def _md5(txt: str):
    """
    MD5加密
    """
    return hashlib.md5(txt.encode(encoding='UTF-8')).hexdigest()


def encrypt(num: str, api: str, d_c0: str):
    """
    知乎加密
    :param num: headers中的x-zse-93
    :param api: 接口及后面的参数
    :param d_c0: d_c0 必要参数
    :return: signature
    """
    sign = _md5(f'{num}+{api}+{d_c0}')
    path = os.path.dirname(__file__)
    with open(f'{path}/encrypt.js') as f:
        js_signature = execjs.compile(f.read(), cwd=f'{path}/node_modules')
        signature = js_signature.call('b', sign)
        signature = '2.0_' + signature
    return signature

