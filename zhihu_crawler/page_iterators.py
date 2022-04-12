"""
页面迭代器
"""
import json
from zhihu_crawler.zhihu_types import *
from zhihu_crawler.constants import *
from loguru import logger
import time
import re
from zhihu_utils.zhihu_utils import get_proxy, get_headers, quote, urljoin, unquote


def iter_search_pages(key_word: str, request_fn: RequestFunction, **kwargs):
    """
    搜索
    :return:
    """
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        data_type = kwargs.pop('data_type', '')
        sort = kwargs.pop('sort', None)
        time_interval = kwargs.pop('time_interval', None)
        key_word = quote(key_word)
        start_url = SEARCH_URL.format(key_word=key_word, data_type=data_type)
        if sort:
            start_url = start_url + f'&sort={sort}'
        if time_interval:
            start_url = start_url + f'&time_interval={time_interval}'

        # ----------- 需要额外加上 cookie 才能请求成功 --------- #
        kwargs['cookie'] = {
            'cookie': 'd_c0="AvAQDHN4mxSPTtVyJn9kQSMi43V1kPWH_qc=|1646810832"; '
                      'z_c0=2|1:0|10:1647511173|4:z_c0|92:Mi4xMWtwS053QUFBQUFDO'
                      'EJBTWMzaWJGQ1lBQUFCZ0FsVk5oVlFnWXdCMEUyQW5RZ0dGb1hZT1NDRX'
                      'RybF81QUtmU3hR|d37c9324eb2e6a989a4bb9e3fb145d33ead3c23365'
                      '3e8c0ea9eda77883c098eb;'
        }
    return generic_iter_pages(start_url, PageParser, request_fn, **kwargs)


def iter_question_pages(question_id: str, request_fn: RequestFunction, **kwargs):
    start_url = kwargs.pop('start_url', None)
    pubdate_sort = kwargs.pop('pubdate_sort', False)
    if not start_url:
        start_url = QUESTION_ANSWERS_URL.format(question_id=question_id)
        if not pubdate_sort:
            start_url = start_url.replace('&sort_by=updated', '&sort_by=default')
    return generic_iter_pages(start_url, QuestionPageParser, request_fn, **kwargs)


def iter_article_pages(article_id: str, request_fn: RequestFunction, **kwargs):
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        start_url = urljoin(BASE_API, f'articles/{article_id}')
    return generic_iter_pages(start_url, ArticlePageParser, request_fn, **kwargs)


def iter_video_pages(video_id: str, request_fn: RequestFunction, **kwargs):
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        start_url = urljoin(BASE_API, f'zvideos/{video_id}')
    return generic_iter_pages(start_url, VideoPageParser, request_fn, **kwargs)


def iter_user_pages(user_id: str, request_fn: RequestFunction, **kwargs):
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        start_url = urljoin(BASE_API, f'people/{user_id}')
    return generic_iter_pages(start_url, UserPageParser, request_fn, **kwargs)


def iter_hot_list_pages(request_fn: RequestFunction, **kwargs):
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        start_url = urljoin(BASE_API, 'topstory/hot-lists/total?limit=50')
    return generic_iter_pages(start_url, HotListPageParser, request_fn, **kwargs)


def iter_hot_question_pages(domain: str, request_fn: RequestFunction, **kwargs):
    start_url = kwargs.pop('start_url', None)
    period = kwargs.pop('period', '')
    question_count = kwargs.pop('question_count', 200)
    if question_count > 200:
        question_count = 200
    if not start_url:
        start_url = BASE_API + f'creators/rank/hot?domain={domain}&limit={question_count}&offset=0&period={period}'
    return generic_iter_pages(start_url, HotQuestionPageParser, request_fn, **kwargs)


def generic_iter_pages(start_url, page_parser_cls, request_fn, **kwargs):
    next_url = start_url
    while next_url:
        retry_limit = 6
        for retry in range(1, retry_limit + 1):
            try:
                response = request_fn(next_url, **kwargs)
                break
            except Exception as e:
                if retry < retry_limit:
                    sleep_time = retry * 2
                    logger.debug(f'重连第{retry}次，休眠{sleep_time}秒, 异常：{e}')
                    time.sleep(sleep_time)
        parser = page_parser_cls(response)
        page = parser.get_pages()
        yield page
        next_page_info = parser.get_next_page()
        if not next_page_info.get('is_end'):
            next_url = next_page_info.get('next_url')
            logger.warning(f'request next url {next_url}')
        else:
            logger.warning('last page')
            return


class PageParser:
    """
    json数据清洗
    """
    json_prefix = 'js-initialData'
    json_regex = re.compile(r'id="js-initialData".*>(\{"initialState.*subAppName.*?})</script>')

    def __init__(self, response):
        self.response = response
        self.html = None
        self.json_data = None
        self._parse()

    def _parse(self):
        jsons = []
        if self.json_prefix in self.response.text:
            jsons = self.json_regex.findall(self.response.text)
        self.json_data = json.loads(self.response.text) if not jsons else json.loads(jsons[0])
        self.html = self.response.html

    def get_raw_page(self) -> RawPage:
        return self.html

    def get_next_page(self) -> Dict:
        assert self.html is not None
        is_end = self.json_data.get('paging', {}).get('is_end', '')
        return {'next_url': self.json_data.get('paging', {}).get('next'), 'is_end': is_end}

    def get_pages(self):
        data_list = self.json_data.get('data', [])
        if not data_list:
            data_list = [self.json_data]
        return data_list


class HotListPageParser(PageParser):
    def get_pages(self):
        data_list = self.json_data.get('data', [])
        answers = []
        for data in data_list:
            if data:
                target = data.get('target') or {}
                target['heat_text'] = data.get('detail_text', '')
                answers.append(target)
        del data_list
        return answers


class HotQuestionPageParser(PageParser):
    """
    热点问题json数据清洗
    """
    def get_pages(self):
        data_list = self.json_data.get('data', [])
        questions = []
        for data in data_list:
            question_info = {}
            question_info.update(data.get('question', {}))
            question_info['reaction'] = data.get('reaction', {})
            questions.append(question_info)
        del data_list
        return questions


class QuestionPageParser(PageParser):
    """
    问题json数据清洗
    """
    pass


class VideoPageParser(PageParser):
    """
    视频json数据清洗
    """
    pass


class ArticlePageParser(PageParser):
    """
    文章json数据清洗
    """
    pass


class UserPageParser(PageParser):
    """
    用户json数据清洗
    """
    pass


class UserAnswerPageParser(PageParser):
    """
    用户的回答json数据清洗
    """
    pass


class UserVideoPageParser(PageParser):
    """
    用户的视频json数据清洗
    """
    pass


class UserArticlePageParser(PageParser):
    """
    用户的文章json数据清洗
    """
    pass


