from .zhihu_types import *
from .zhihu_scraper import ZhiHuScraper
from .constants import *

_scraper = ZhiHuScraper()


def set_cookies(cookies):
    pass


def search_crawler(key_word: Optional[str] = None,
                   comment_count: Optional[int] = -1,
                   count: Optional[int] = 0,
                   **kwargs) -> Union[Iterator[AnswerType], Iterator[ArticleType], Iterator[VideoType]]:
    """
    关键词搜索采集（answer、article、video...）
    :param key_word: 关键词
    :param kwargs:
    :param count: (int) 采集指定数量的回答、视频、文章。该值过大可能会导致多次请求。-1 不采集 0采集全部（默认） >0采集指定的数量
    :param comment_count: (int) 采集指定数量的评论。该值过大可能会导致多次请求。默认-1 不采集 0采集全部 >0采集指定的数量
    @ page_limit (int): 需要采集的页数, 默认为constants下的 DEFAULT_PAGE_LIMIT
    @ data_type:（str or list or set or tuple） 获取数据类型 可选择（answer、article、zvideo） 默认三个类型都会采集
    @ sort: (str or None)排序。默认sort=None综合排序，sort=created_time最新发布时间排序; sort=upvoted_count最多赞同排序
    @ time_interval: 时效。一天内（time_interval=a_day），可选择一周内（time_interval=a_week） 一月内（time_interval=a_month）
                    三月内（time_interval=three_months） 半年内(time_interval=half_a_year) 一年内（time_interval=a_year）
                    不限时间（time_interval=None）默认
    @ drill_down_count: (int) 下钻内容采集数量(问题下的回答)，，默认-1 不采集 0采集全部 >0采集指定的数量
    :return:
    """
    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)
    options: Union[Dict[str, Any], Set[str]] = kwargs.setdefault('options', {})
    if isinstance(options, set):
        options = {k: True for k in options}
    options.setdefault('key_word', key_word)
    options['drill_down_count'] = kwargs.pop('drill_down_count', -1)
    if comment_count:
        options['comment_count'] = comment_count
    data_types = kwargs.get('data_type', [ANSWER, ARTICLE, VIDEO])
    kwargs['data_type'] = options['data_type'] = data_types
    kwargs['sort'] = options['sort'] = kwargs.get('sort', None)
    kwargs['time_interval'] = options['time_interval'] = kwargs.get('time_interval', None)
    cookies = kwargs.pop('cookies', None)
    kwargs['total_count'] = count
    if cookies:
        pass
    data_types = [data_types] if isinstance(data_types, str) else data_types
    if isinstance(data_types, list):
        for data_type in data_types:
            kwargs['data_type'] = data_type
            for result in _scraper.search_crawler(key_word, **kwargs):
                yield result


def top_search_crawl(top_search_url: Optional[str] = TOP_SEARCH_URL,
                     **kwargs) -> Keyword:
    """
    热搜采集
    :param top_search_url: 热搜固定url
    page_limit (int): 需要采集的页数, 默认为constants下的 DEFAULT_PAGE_LIMIT
    :return:
    """
    return _scraper.top_search_crawler(top_search_url=top_search_url, **kwargs)


def hot_questions_crawler(period: Union[str] = 'hour',
                          domains: Union[str, list, tuple] = 0,
                          **kwargs) -> Iterator[QuestionType]:
    """
    问题热榜
    url = https://www.zhihu.com/knowledge-plan/hot-question/hot/0/hour 小时榜
    api = https://api.zhihu.com/creators/rank/hot?domain=0&limit=20&offset=0&period=hou
    :param period: 榜单类型（小时榜-hour、 日榜-day、周榜-week） 默认hour
    :param domains: 频道id, 支持字符串、列表、元组形式的参数
                    0-所有(默认)    1001-数码     1002-科技      1003-互联网    1004-商业财经   1005-职场
                    1006-教育      1007-法律     1008-军事      1009-汽车      1010-人文社科   1011-自然科学
                    1012-工程技术   1013-情感     1014-心理学    1015-两性      1016母婴亲子    1017-家居
                    1018-健康      1019-艺术     1020-音乐      1021-设计      1022-影视娱乐   1023-宠物
                    1024-体育电竞   1025-运动健身  1026-动漫游戏  1027-美食      1028-旅行       1029-时尚
    @ question_count: 采集问题的数量， 默认0采集所有； >0 采集指定数量
    @ drill_down_count: (int) 下钻内容(answer)采集数量，热榜下钻内容数据量大，默认-1 不采集 0采集全部 >0采集指定的数量
    @ comment_count: (int) 采集指定数量的评论。该值过大可能会导致多次请求;默认-1 不采集 0采集全部 >0采集指定的数量
    """
    if isinstance(domains, int or str):
        domains = [domains]
    options: Union[Dict[str, Any], Set[str]] = kwargs.setdefault('options', {})
    kwargs['question_count'] = kwargs.pop('question_count', 0)
    options['drill_down_count'] = kwargs.pop('drill_down_count', -1)
    options['comment_count'] = kwargs.pop('comment_count', -1)
    kwargs['period'] = period
    return _scraper.hot_question_crawler(domains=domains, **kwargs)


def hot_list_crawler(drill_down_count: Union[int] = -1, **kwargs) -> Iterator[QuestionType]:
    """
    首页热榜
    https://www.zhihu.com/hot
    api: https://api.zhihu.com/topstory/hot-lists/total?limit=50
    :param drill_down_count: (int) 下钻内容采集数量，热榜下钻内容数据量大，默认-1 不采集 0采集全部 >0采集指定的数量
    @ comment_count: (int) 采集指定数量的评论。该值过大可能会导致多次请求;默认-1 不采集 0采集全部 >0采集指定的数量
    """
    options: Union[Dict[str, Any], Set[str]] = kwargs.setdefault('options', {})
    options['comment_count'] = kwargs.pop('comment_count', -1)
    options['drill_down_count'] = drill_down_count
    return _scraper.hot_list_crawler(**kwargs)


def common_crawler(task_id: Union[str],
                   data_type: Optional[str] = None,
                   drill_down_count: Optional[int] = -1,
                   comment_count: Optional[int] = -1,
                   similar_questions: Optional[bool] = False,
                   similar_recommends: Optional[bool] = False,
                   **kwargs) -> Union[Iterator[AnswerType],
                                      Iterator[QuestionType],
                                      Iterator[VideoType],
                                      Iterator[ArticleType]]:
    """
    通用采集(问答、视频、专栏、文章、话题)
    :param task_id: 问题id、视频id、文章id、话题id.
    :param data_type: 指定数据类型的采集 (answer or article or zvideo or question)
    :param drill_down_count: (int) 下钻内容（answer）采集，默认-1 不采集 0采集全部 >0采集指定的数量
    :param comment_count: (int) 采集指定数量的评论。该值过大可能会导致多次请求;默认-1 不采集 0采集全部 >0采集指定的数量
    :param similar_questions: (bool) 是否采集相类似的问题 默认 False 不采集
    :param similar_recommends: (bool) 是否采集相类似的推荐 默认 False 不采集
    pubdate_sort: (bool) 是否通过时间排序. 默认True通过最新发布时间降序形式进行采集
    :return:
    """
    options: Union[Dict[str, Any], Set[str]] = kwargs.setdefault('options', {})
    if isinstance(options, set):
        options = {k: True for k in options}
    if data_type:
        options['data_type'] = data_type
    kwargs['pubdate_sort'] = kwargs.get('pubdate_sort', True)
    options['drill_down_count'] = kwargs['drill_down_count'] = drill_down_count
    options['comment_count'] = comment_count
    if similar_questions:
        options['similar_questions'] = similar_questions
    if similar_recommends:
        options['similar_recommends'] = similar_recommends
    if data_type == QUESTION:
        return _scraper.question_crawler(question_id=task_id, **kwargs)
    elif data_type == ARTICLE:
        return _scraper.article_crawler(article_id=task_id, **kwargs)
    elif data_type == VIDEO:
        return _scraper.video_crawler(video_id=task_id, **kwargs)
    if data_type not in (ARTICLE, VIDEO, QUESTION):
        raise ValueError('匹配不到可以采集的数据类型，请校对data_type的值')


def user_crawler(user_id: Union[str],
                 following: Union[int] = -1,
                 followers: Union[int] = -1,
                 following_topics: Union[int] = -1,
                 following_columns: Union[int] = -1,
                 following_questions: Union[int] = -1,
                 following_collections: Union[int] = -1,
                 **kwargs) -> Iterator[UserType]:
    """
    账号采集
    :param user_id: (str) 账号id 如 https://www.zhihu.com/people/kenneth-pan/answers中 kenneth-pan为user_id
                    数据api：https://api.zhihu.com/people/user_id
    :param following: 是否采集该账号关注人列表；-1不采集（默认）。0采集全部（可能会导致多次请求）；>0将采集指定数量
    :param followers: 是否采集关注该账号的人列表；参数值规则如上
    :param following_topics: 是否采集该账号关注的话题列表；参数值规则如上
    :param following_columns: 是否采集该账号关注的专栏列表；参数值规则如上
    :param following_questions: 是否采集该账号关注的问题列表；参数值规则如上
    :param following_collections: 是否采集该账号关注的收藏列表；参数值规则如上
    @ answer_count: 是否采集该账号的问答列表；参数值规则如上
    @ zvideo_count: 是否采集该账号的视频列表；参数值规则如上
    @ question_count： 是否采集该账号的提问列表；参数值规则如上
    @ article_count： 是否采集该账号的文章列表；参数值规则如上
    @ column_count： 是否采集该账号的专栏列表；参数值规则如上
    @ pin_count： 是否采集该账号的专栏列表；参数值规则如上
    @ collection_count: 是否采集该账号的收藏夹内容；参数值规则如上
    @ sort: (str)排序。默认sort=created 时间排序，sort=included 被收录回答/文章排序; sort=voteups最多赞同排序
    @ drill_down_count: 是否向下钻取内容（如提问的回答、专栏下的文章、收藏话题下的内容等）；参数值规则如上
    @ comment_count: 需要采集的回答、视频、文章、想法的评论数；参数值规则如上
    """
    options: Union[Dict[str, Any], Set[str]] = kwargs.setdefault('options', {})
    if isinstance(options, set):
        options = {k: True for k in options}
    options['comment_count'] = kwargs.pop('comment_count', -1)
    options['answer_count'] = kwargs.pop('answer_count', -1)
    options['zvideo_count'] = kwargs.pop('zvideo_count', -1)
    options['question_count'] = kwargs.pop('question_count', -1)
    options['article_count'] = kwargs.pop('article_count', -1)
    options['column_count'] = kwargs.pop('column_count', -1)
    options['pin_count'] = kwargs.pop('pin_count', -1)
    options['drill_down_count'] = kwargs.pop('drill_down_count', -1)
    options['collection_count'] = kwargs.pop('collection_count', -1)
    options['following'] = following
    options['followers'] = followers
    options['following_topics'] = following_topics
    options['following_columns'] = following_columns
    options['following_questions'] = following_questions
    options['following_collections'] = following_collections
    kwargs['sort'] = options['sort'] = kwargs.get('sort', 'created')
    return _scraper.user_crawler(user_id, **kwargs)
