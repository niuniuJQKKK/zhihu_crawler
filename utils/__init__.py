from utils import zhihu_utils
from zhihu_crawler.zhihu_types import Dict, Union
from urllib.parse import unquote, urljoin, quote


def get_proxy():
    return zhihu_utils.get_proxy()


def get_headers(url: str, d_c0: str):
    """
    获取加密参数
    :param url:
    :param d_c0: cookie中必要参数；加密需要该参数
    :return:
    """
    return zhihu_utils.get_headers(url, d_c0)


def get_useragent():
    return zhihu_utils.get_useragent()


def generating_page_links(base_url, total_num=50, limit=20):
    return zhihu_utils.generating_page_links(base_url=base_url, total_num=total_num, limit=limit)


def extract_time(json_data: Dict) -> Dict[str, Union[str, int]]:
    return zhihu_utils.extract_time(json_data)
