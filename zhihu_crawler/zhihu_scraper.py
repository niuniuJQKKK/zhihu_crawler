from requests_html import HTMLSession, AsyncHTMLSession
from functools import partial
from .page_iterators import *
from .extractors import extract_data, extract_user, extract_hot_data
from zhihu_utils.zhihu_utils import get_useragent
import itertools
from loguru import logger
import asyncio


class ZhiHuScraper:
    """
    知乎采集
    """
    default_headers = {
        # 'connection': 'close',
        "user-agent": get_useragent(),
        'cookie': 'd_c0="AIBfvRMxmhSPTk1AffR--QLwm-gDM5V5scE=|1646725014"'
    }

    def __init__(self, session=None, async_session=None, requests_kwargs=None):
        if session is None:
            session = HTMLSession()
            session.headers.update(self.default_headers)
        if requests_kwargs is None:
            requests_kwargs = {}
        if async_session is None:
            async_session = AsyncHTMLSession(workers=ASYNC_COUNT)
            async_session.headers.update(self.default_headers)
        self.async_session = async_session
        self.session = session
        for key in ['Connection', 'Accept', 'Accept-Encoding']:
            self.async_session.headers.pop(key)
            self.session.headers.pop(key)
        self.requests_kwargs = requests_kwargs

    def set_proxy(self, proxy: Optional[str] = None):
        """
        设置代理
        :param proxy: 字符串形式的代理
        :return:
        """
        proxies = {
            'proxies': {
                'http': proxy,
                'https': proxy
            }
        }
        self.requests_kwargs.update(proxies)

    def search_crawler(self, key_word: Union[str], **kwargs):
        """
        通过关键词对检索结果进行采集
        :param key_word: 需要采集的关键词
        :return:
        """
        kwargs['scraper'] = self
        iter_search_pages_fn = partial(iter_search_pages, key_word=key_word, request_fn=self.send, **kwargs)
        return self._generic_crawler(extract_data, iter_search_pages_fn, **kwargs)

    def question_crawler(self, question_id: Union[str], **kwargs):
        """
        通过问题id采集
        """
        kwargs['scraper'] = self
        iter_question_pages_fn = partial(iter_question_pages, question_id=question_id, request_fn=self.send, **kwargs)
        count = 0
        answer_count = kwargs.get('drill_down_count')
        for result in self._generic_crawler(extract_data, iter_question_pages_fn, **kwargs):
            if count >= answer_count:
                break
            count += 1
            yield result

    def article_crawler(self, article_id: Union[str], **kwargs):
        """
        通过文章id采集文章页数据
        """
        kwargs['scraper'] = self
        iter_article_pages_fn = partial(iter_article_pages, article_id=article_id, request_fn=self.send, **kwargs)
        return self._generic_crawler(extract_data, iter_article_pages_fn, **kwargs)

    def video_crawler(self, video_id: Union[str], **kwargs):
        """
        通过视频id采集视频页数据
        """
        kwargs['scraper'] = self
        iter_video_pages_fn = partial(iter_video_pages, video_id=video_id, request_fn=self.send, **kwargs)
        return self._generic_crawler(extract_data, iter_video_pages_fn, **kwargs)

    def user_crawler(self, user_id: Union[str], **kwargs):
        """
        通过账号id采集个人主页数据
        """
        kwargs['scraper'] = self
        iter_user_page_fn = partial(iter_user_pages, user_id=user_id, request_fn=self.send, **kwargs)
        return self._generic_crawler(extract_user, iter_user_page_fn, **kwargs)

    def hot_list_crawler(self, **kwargs):
        """
        首页热榜采集
        """
        kwargs['scraper'] = self
        iter_hot_page_fn = partial(iter_hot_list_pages, request_fn=self.send, **kwargs)
        return self._generic_crawler(extract_hot_data, iter_hot_page_fn, **kwargs)

    def hot_question_crawler(self, domains, **kwargs):
        """
        热点问题采集
        """
        kwargs['scraper'] = self
        question_count = kwargs.get('question_count', 0)
        for domain in domains:
            iter_hot_question_page_fn = partial(iter_hot_question_pages, domain=domain, request_fn=self.send, **kwargs)
            count = 0
            for result in self._generic_crawler(extract_hot_data, iter_hot_question_page_fn, **kwargs):
                if count >= question_count:
                    break
                count += 1
                yield result
            if count >= question_count:
                break

    def send(self, url, **kwargs):
        if not url:
            logger.error('url is null')
        method = kwargs.get('method', 'GET')
        return self.post(url, **kwargs) if method == 'POST' else self.get(url, **kwargs)

    def get(self, url, **kwargs):
        """
        请求方法，在该方法中获取代理及x_zse_96参数加密
        @ x_zse_96: 是否需要x_zse_96参数加密
        """
        x_zse_96 = kwargs.pop('x_zse_96', False)
        cookie = kwargs.pop('cookie', {})
        # 获取代理信息
        # proxies = {'http': get_proxy(), 'https': get_proxy()}
        proxies = {'http': 'http://127.0.0.1:8125', 'https': 'http://127.0.0.1:8125'}
        if isinstance(url, str):
            if x_zse_96 or cookie:
                self.session.headers.update(get_headers(url) or {})
                self.session.headers.update(cookie)
            try:
                response = self.session.get(url, proxies=proxies, **self.requests_kwargs)
                response.raise_for_status()
                return response
            except Exception as e:
                logger.error(f'http error: {e}')
        if isinstance(url, list):  # 使用协程请求
            return self.generic_response(url, x_zse_96=x_zse_96, proxies=proxies)

    def generic_response(self, urls, x_zse_96, proxies):
        urls = [urls[i: i + ASYNC_COUNT] for i in range(0, len(urls), ASYNC_COUNT)]
        for sub_urls in urls:
            tasks = [lambda url=url: self.async_get(url, x_zse_96=x_zse_96, proxies=proxies) for url in sub_urls]
            results = self.async_session.run(*tasks)
            yield results

    async def async_get(self, url, **kwargs):
        if kwargs.get('x_zse_96'):
            self.async_session.headers.update(get_headers(url))
        proxies = kwargs.get('proxies', {})
        response = await self.async_session.get(url, proxies=proxies, timeout=5)
        if response and response.status_code != 200:
            logger.error(f'request url: {url}, response code: {response.status_code}')
        await asyncio.sleep(2)
        return response

    def post(self, url, **kwargs):
        pass

    def _generic_crawler(self,
                         extract_fn,
                         iter_pages_fn,
                         options=None,
                         **kwargs):
        """
        中转函数
        @extract_fn 数据清洗方法
        @iter_pages_fn 页面处理方法
        @options 参数
        """
        page_limit = kwargs.get('page_limit') if kwargs.get('page_limit', 0) else DEFAULT_PAGE_LIMIT
        counter = itertools.count(0) if page_limit is None else range(page_limit)
        if options is None:
            options = {}
        elif isinstance(options, set):
            options = {k: True for k in options}
        for i, page in zip(counter, iter_pages_fn()):
            if not page:
                break
            for element in page:
                info = extract_fn(element, options=options, request_fn=self.send)
                yield info
