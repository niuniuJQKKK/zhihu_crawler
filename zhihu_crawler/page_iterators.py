"""
页面生成器
"""
import json
from zhihu_crawler.zhihu_types import *
from zhihu_crawler.constants import *
from loguru import logger
import re
from utils import get_proxy, get_headers, quote, urljoin, unquote


def iter_search_pages(key_word: str, request_fn: RequestFunction, **kwargs) -> Iterator[Page]:
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
    kwargs['z_c0'] = '2|1:0|10:1647511173|4:z_c0|92:Mi4xMWtwS053QUFBQUFDOEJBTWMzaWJGQ1lBQUFCZ0FsVk5oVlFnWXd' \
                     'CMEUyQW5RZ0dGb1hZT1NDRXRybF81QUtmU3hR|d37c9324eb2e6a989a4bb9e3fb145d33ead3c233653e8c0e' \
                     'a9eda77883c098eb'
    print()
    return generic_iter_pages(start_url, PageParser, request_fn, **kwargs)


def iter_question_pages(question_id: str, request_fn: RequestFunction, **kwargs) -> Iterator[Page]:
    start_url = kwargs.pop('start_url', None)
    pubdate_sort = kwargs.pop('pubdate_sort', False)
    if not start_url:
        start_url = urljoin('https://www.zhihu.com/question/', question_id)
        if not pubdate_sort:
            start_url = start_url.replace('&sort_by=updated', '&sort_by=default')
    return generic_iter_pages(start_url, QuestionPageParser, request_fn, **kwargs)


def iter_article_pages(article_id: str, request_fn: RequestFunction, **kwargs) -> Iterator[Page]:
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        start_url = urljoin(BASE_API, f'articles/{article_id}')
    return generic_iter_pages(start_url, ArticlePageParser, request_fn, **kwargs)


def iter_video_pages(video_id: str, request_fn: RequestFunction, **kwargs) -> Iterator[Page]:
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        start_url = urljoin(BASE_API, f'zvideos/{video_id}')
    return generic_iter_pages(start_url, VideoPageParser, request_fn, **kwargs)


def iter_answer_pages(answer_id: str, request_fn: RequestFunction, **kwargs) -> Iterator[Page]:
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        start_url = urljoin('https://www.zhihu.com/answer/', answer_id)
        # kwargs['x_zse_96'] = X_ZSE_96
    return generic_iter_pages(start_url, AnswerPageParser, request_fn, **kwargs)


def iter_user_pages(user_id: str, request_fn: RequestFunction, **kwargs) -> Iterator[Page]:
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        start_url = urljoin(BASE_API, f'people/{user_id}')
    return generic_iter_pages(start_url, UserPageParser, request_fn, **kwargs)


def iter_hot_list_pages(request_fn: RequestFunction, **kwargs) -> Iterator[Page]:
    start_url = kwargs.pop('start_url', None)
    if not start_url:
        start_url = urljoin(BASE_API, 'topstory/hot-lists/total?limit=50')
    return generic_iter_pages(start_url, HotListPageParser, request_fn, **kwargs)


def iter_hot_question_pages(domain: str, request_fn: RequestFunction, **kwargs) -> Iterator[Page]:
    start_url = kwargs.pop('start_url', None)
    period = kwargs.pop('period', '')
    question_count = kwargs.pop('question_count', 200)
    question_count = 200 if question_count > 200 else question_count
    if not start_url:
        start_url = BASE_API + f'creators/rank/hot?domain={domain}&limit={question_count}&offset=0&period={period}'
    return generic_iter_pages(start_url, HotQuestionPageParser, request_fn, **kwargs)


def generic_iter_pages(start_url, page_parser_cls, request_fn, **kwargs) -> Iterator[Page]:
    next_url = start_url
    response = None
    while next_url:
        try:
            response = request_fn(next_url, **kwargs)
        except Exception as e:
            logger.error(f'error: {e}')
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
        assert self.response is not None, 'response is null'
        if self.json_prefix in self.response.text:
            jsons = self.json_regex.findall(self.response.text)
        self.json_data = json.loads(self.response.text) if not jsons else json.loads(jsons[0])
        self.html = self.response.html

    def get_raw_page(self) -> RawPage:
        return self.html

    def get_next_page(self) -> Dict[str, Union[str, bool]]:
        assert self.json_data is not None, 'json_data is null'
        is_end = self.json_data.get('paging', {}).get('is_end', '')
        return {'next_url': self.json_data.get('paging', {}).get('next'), 'is_end': is_end}

    def get_pages(self) -> Page:
        assert self.json_data is not None, 'json_data is null'
        data_list = self.json_data.get('data', [])
        if not data_list:
            data_list = [self.json_data]
        assert data_list is not None, 'data_list is null'
        return data_list


class HotListPageParser(PageParser):
    def get_pages(self) -> Page:
        assert self.json_data is not None, 'json_data is null'
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

    def get_pages(self) -> Page:
        assert self.json_data is not None, 'json_data is null'
        data_list = self.json_data.get('data', [])
        questions = []
        for data in data_list:
            question_info = {}
            question_info.update(data.get('question', {}))
            question_info['reaction'] = data.get('reaction', {})
            questions.append(question_info)
        del data_list
        return questions


class AnswerPageParser(PageParser):
    """
    回答页面
    """
    def get_pages(self) -> Page:
        assert self.json_data is not None, 'json_data is null'
        answers = self.json_data.get('initialState', {}).get('entities', {}).get('answers', {})
        answers = [answers[key] for key in answers.keys() if key and key.isdigit()]
        return answers


class QuestionPageParser(PageParser):
    """
    问题json数据清洗
    """
    def get_pages(self) -> Page:
        assert self.json_data is not None, 'json_data is null'
        questions = self.json_data.get('initialState', {}).get('entities', {}).get('questions', {})
        questions = [questions[key] for key in questions.keys() if key and key.isdigit()]
        return questions


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
