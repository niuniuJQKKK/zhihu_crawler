""""
知乎工具类
"""
from common.encrypt import encrypt
import re
from zhihu_crawler.constants import X_ZSE_93
from zhihu_crawler.zhihu_types import *
from math import ceil
from urllib.parse import unquote, urljoin, quote
from my_fake_useragent import UserAgent


def get_proxy():
    """
    获取代理
    """
    proxy_meta = {}
    return proxy_meta


def get_headers(url):
    sign, cookies = encrypt(X_ZSE_93, ''.join(re.sub(r'.*zhihu\.com', '', url)))
    headers = {
        'cookie': f'd_c0={cookies}',
        'user-agent': get_useragent(),
        'x-zse-93': X_ZSE_93,
        'x-zse-96': sign
    }
    return headers


def extract_time(json_data: Dict) -> Dict[str, Union[str, int]]:
    """
    时间处理
    """
    pub_time = json_data.get('created_time', '') or json_data.get('created_at', '') or \
               json_data.get('createdTime', '') or json_data.get('created', '') or \
               json_data.get('publishedAt', '') or json_data.get('published_at', '')

    edit_time = json_data.get('updated_time', '') or json_data.get('updated_at', '') or \
                json_data.get('updatedTime', '') or json_data.get('updated', '') or json_data.get('updatedAt', '')
    return {
        'pub_time': pub_time,
        'edit_time': edit_time
    }


def generating_page_links(base_url, total_num=50, limit=20):
    """
    根据总数及每页显示的个数生成下一页的urls
    @param base_url: 基础的url
    @param total_num: 数据总数 默认50
    @param limit: 每页展示的个数 默认20
    """
    page_urls = []
    for i in range(ceil(total_num/limit)):
        page_urls.append(re.sub(rf'offset=[\d+]&limit=[\d+]', f'offset={i*limit}&limit={limit}', base_url))
    return page_urls


def get_useragent():
    """
    随机获取useragent
    Returns: useragent
    """
    return UserAgent(phone=False, family='chrome', os_family='windows').random()