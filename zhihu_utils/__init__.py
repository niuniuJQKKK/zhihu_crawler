from zhihu_utils import zhihu_utils


def get_proxy():
    return zhihu_utils.get_proxy()


def get_headers(url):
    """
    获取加密参数
    :param url:
    :return:
    """
    return zhihu_utils.get_headers(url)
