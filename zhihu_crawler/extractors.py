"""
知乎清洗器
"""
from .zhihu_types import *
from .constants import *
from requests_html import HTML
from loguru import logger
import re
import copy
import json
from utils import urljoin, extract_time, generating_page_links


def extract_data(raw_html, options: Options, request_fn: RequestFunction, full_html=None) -> Union[QuestionType,
                                                                                                   AnswerType,
                                                                                                   ArticleType]:
    return BaseExtractor(raw_html, options, request_fn, full_html).extract_data()


def extract_user(raw_html, options: Options, request_fn: RequestFunction, full_html=None) -> UserType:
    return UserExtractor(raw_html, options, request_fn, full_html).extract_data()


def extract_question_data(raw_html, options: Options, request_fn: RequestFunction, full_html=None) -> QuestionType:
    return QuestionExtractor(raw_html, options, request_fn, full_html).extract_data()


def init_question_reaction():
    """
    问题的互动量
    """
    return {
        "new_pv": 0,  # 浏览增量
        "new_pv_7_days": 0,  # 浏览7日增量
        "new_follow_num": 0,  # 关注增量
        "new_follow_num_7_days": 0,  # 关注7日增量
        "new_answer_num": 0,  # 回答增量
        "new_answer_num_7_days": 0,  # 回答7日增量
        "new_upvote_num": 0,  # 点赞增量
        "new_upvote_num_7_days": 0,  # 点赞7日增量
        "pv": 0,  # 总浏览量
        "follow_num": 0,  # 总关注量
        "answer_num": 0,  # 总回答量
        "upvote_num": 0,  # 总点赞量
        "new_pv_yesterday": 0,
        "new_pv_t_yesterday": 0,
        "score": 0,  # 热力值
        "score_level": 0  # 热力等级
    }


class BaseExtractor:
    video_regex = re.compile(r'play_url\".*\"(http.*\.mp4\?.*=hw?)"')
    ele_regex = re.compile(r'<.*</.*>')

    def __init__(self, element, options, request_fn, full_html=None):
        self.element = element
        self.options = options
        self.request_fn = request_fn
        self._type = None
        self._content_html = None
        self.info = {}
        # 详情页
        self._detail_response = None

    @property
    def type(self):
        if self._type is not None:
            return self._type
        self._type = self.element.get('type', '')
        return self._type

    def content_html(self, content=None):
        if self._content_html is not None:
            return self._content_html
        html = content if content else self.element.get('content', '')
        self._content_html = HTML(html=html)
        return self._content_html

    def detail_response(self):
        """
        详情页请求
        :param:
        :return:
        """
        if self._detail_response is not None:
            return self._detail_response
        self._detail_response = self.request_fn(self.info.get('source_url'))
        return self._detail_response

    def extract_data(self):
        """
        数据清洗入口
        :return:
        """
        if self.element.get('tab_type', '') == GENERAL:
            """
            杂志文章需要付费， 跳过清洗
            """
            return {}
        methods = [
            self.extract_id,
            self.extract_video_id,
            self.extract_title,
            self.extract_content,
            self.extract_pub_time,
            self.extract_edit_time,
            self.extract_question,
            self.extract_url,
            self.extract_pictures,
            self.extract_video_url,
            self.extract_author,
            self.extract_labels,
            self.extract_up_count,
            self.extract_appreciate_count,
            self.extract_comment_count,
            self.extract_title_pictures,
            self.extract_title_description,
            self.extract_like_count,
            self.extract_play_count
        ]
        for method in methods:
            try:
                partial_info = method()
                if partial_info is None:
                    continue
                # logger.warning(f'method: {method.__name__} return: {partial_info}')
                self.info.update(partial_info)
            except Exception as ex:
                logger.debug(f'method: {method.__name__} error:{ex}')
        temp_info = copy.deepcopy(self.info)
        # 问题只保留问题相关内容
        for key in temp_info.keys():
            if self.type == QUESTION:
                pop_info = self.info.pop(key)
                if key in ('author_info', 'content', 'pictures'):  # 将问题的user信息和内容信息移至question_info下
                    self.info[key] = pop_info
                if key == 'question_info':
                    self.info.update(pop_info)

        # ********* 如果是问题采集回答 ********* #
        total_count = self.info.get('question_answer_count')
        question_id = self.info.get('question_id', '')
        answer_count = self.options.get('drill_down_count')
        if self._type == QUESTION and answer_count > -1 and total_count > 0:
            total_count = answer_count if 0 < answer_count < total_count else total_count
            url = QUESTION_ANSWERS_URL.format(question_id=question_id)
            self.extract_meta_data(url, type_name='answers', total_count=total_count)

        self.info['type'] = self.type
        # 采集评论:
        self.info.update(self.extract_comments())
        del temp_info
        return self.info

    def extract_id(self) -> PartialType:
        data_id = self.element.get('id', '')
        if not data_id:
            data_id = self.element.get('zvideo_id', '')
        return {
            f'{self.type}_id': data_id
        }

    def extract_video_id(self) -> PartialType:
        """
        清洗视频id
        """
        video_id = self.element.get('attachment', {}).get('attachment_id', '')
        if not video_id:
            video_id = self.element.get('video_id', '')
        if not video_id:
            video_id = self.element.get('video', {}).get('video_id', '')
        return {
            'video_id': video_id
        }

    def extract_title(self) -> PartialType:
        """
        标题
        """
        title = self.element.get('title', '')
        if not title:
            question = self.element.get('question', {})
            title = question.get('title', '') or question.get('name', '')
        if not title:
            title = self.element.get('attachment', {}).get('video', {}).get('title', '')
        title = re.sub('<em>|</em>', '', title)
        return {
            'title': title
        }

    def extract_content(self, content=None) -> PartialType:
        content = self.element.get('content', '') if content is None else content
        if content and self.ele_regex.findall(content):
            contents = []
            for ele in self.content_html(content).find('p,h1,h2,h3,h4,h5,h6,pre>code,li'):
                if ele and ele.text:
                    if ele.text not in contents:
                        contents.append(ele.text)
            content = '\n'.join(contents)
            content = re.sub(r'<.*>', '', content)
        return {
            'content': content
        }

    def extract_pub_time(self) -> PartialType:
        """
        编辑时间
        :return:
        """
        return {
            'pub_time': extract_time(self.element).get('pub_time')
        }

    def extract_edit_time(self) -> PartialType:
        """
        编辑时间
        :return:
        """
        return {
            'edit_time': extract_time(self.element).get('edit_time')
        }

    def extract_question(self) -> PartialType:
        """
        清洗问题信息
        :return:
        """
        question_info = self.element if self.type == QUESTION else self.element.get('question', {})
        question_id = question_info.get('id', '')
        question_title = question_info.get('title', '') or question_info.get('name', '')
        question_reaction = init_question_reaction()
        question_reaction.update(question_info.get('reaction', {}))
        answers = question_reaction.get('answer_num')
        return {
            'question_info': {
                'question_id': question_id,
                'created_time': extract_time(question_info).get('pub_time'),
                'question_title': question_title.replace('<em>', '').replace('</em>', ''),
                'question_type': question_info.get('type', '') or question_info.get('question_type', ''),
                'edit_time': extract_time(question_info).get('edit_time'),
                'question_url': BASE_URL + f'question/{question_id}' if question_id else '',
                'question_follower_count': question_info.get('follower_count', 0) or question_info.get('followerCount',
                                                                                                       0),
                'comment_count': question_info.get('comment_count', 0) or question_info.get('commentCount', 0),
                'question_answer_count': question_info.get('answer_count', 0) or question_info.get('answerCount',
                                                                                                   0) or answers,
                'question_visits_count': question_info.get('visits_count', 0) or question_info.get('visitCount', 0),
                'question_collapsed_count': question_info.get('collapsedAnswerCount', 0),
                'question_up_count': question_info.get('voteupCount', 0),
                'question_description': question_info.get('description', ''),
                'question_labels': [topic_info.get('name') for topic_info in question_info.get('topics', []) if
                                    topic_info],
                'question_reaction': question_reaction
            }
        }

    def extract_url(self) -> PartialType:
        """
        url 清洗
        """
        url = self.element.get('url', '')
        if ANSWER in url or self.type == VIDEO_ANSWER:
            question_id = self.element.get('question', {}).get('id', '')
            url = urljoin(BASE_URL, f"question/{question_id}/answer/{self.info.get(f'{self.type}_id', '')}")
        if not url:
            url = self.element.get('video_url', '')
        url = re.sub('.*/articles/', ARTICLE_BASE_URL, url).replace('api/v4/zvideos', 'zvideo')
        return {
            'source_url': url
        }

    def extract_pictures(self) -> PartialType:
        """
        图片清洗
        """
        pic = ''
        if self._content_html:
            pic = '#'.join([img.attrs.get('src') for img in self._content_html.find('img') if img
                            and img.attrs.get('src', '').startswith('http')])
        if not pic:
            pic = self.element.get('cover_url', '') or self.element.get('thumbnail', '')
        if not pic:
            pic = self.element.get('image_url', '')
        return {
            'pictures': pic
        }

    def extract_video_url(self) -> PartialType:
        """
        视频链接
        """
        video_url = ''
        if self.type in (VIDEO, VIDEO_ANSWER) and self.info.get('video_id'):
            response = self.request_fn(VIDEO_BASE_URL + f'{self.info.get("video_id")}')
            if response:
                result = self.video_regex.findall(response.text)
                video_url = result[0] if result else ''
        return {'video_url': video_url}

    def extract_author(self, author_info=None) -> PartialType:
        """
        用户信息
        """
        author_info = self.element.get('author', {}) if not author_info else author_info
        user_url_token = author_info.get('url_token', '') or author_info.get('urlToken', '')
        user_type = author_info.get('type', '')
        badge = author_info.get('badge', [])
        auth_infos = [badge_dict.get('description') for badge_dict in badge if badge_dict]
        return {
            'author_info': {
                'user_name': author_info.get('name', '').replace('<em>', '').replace('</em>', ''),
                'user_url_token': user_url_token,
                'user_id': author_info.get('id', ''),
                'user_url': urljoin(BASE_URL, f'{user_type}/{user_url_token}') if user_url_token else '',
                'user_headline': author_info.get('headline', ''),
                'user_avatar_url': author_info.get('avatar_url', '') or author_info.get('avatarUrl', ''),
                'user_is_vip': author_info.get('vip_info', {}).get('is_vip', '') or author_info.get('vipInfo', {}).get(
                    'isVip', False),
                'user_follower_count': author_info.get('follower_count', 0) or author_info.get('followerCount', 0),
                'user_up_count': author_info.get('voteup_count', 0) or author_info.get('voteupCount', 0),
                'user_auth_infos': auth_infos,
            }
        }

    def extract_up_count(self) -> PartialType:
        """
        赞同数
        """
        return {
            'up_count': self.element.get('voteup_count', 0)
        }

    def extract_appreciate_count(self) -> PartialType:
        """
        赞赏数
        """
        return {
            'appreciate_count': self.element.get('reward_info', {}).get('reward_member_count', 0)
        }

    def extract_comment_count(self) -> PartialType:
        """
        评论数
        """
        return {
            'comment_count': self.element.get('comment_count', 0) or self.element.get('commentCount', 0)
        }

    def extract_labels(self) -> PartialType:
        """
       详情页的 标签
       :return:
       """
        labels = [topic.get('name', '') for topic in self.element.get('topics', []) if topic]
        if not labels:
            if self._detail_response is None:
                self.detail_response()
            label_ele = self._detail_response.html.find('meta[name="keywords"]', first=True)
            labels = label_ele.attrs.get('content').split(',') if label_ele else []
        return {'labels': labels}

    def extract_title_pictures(self) -> PartialType:
        img_str = '#'.join([self.element.get('titleImage', '') or self.element.get('title_image', '')])
        if not img_str and self._detail_response:
            images = self._detail_response.html.find('div.QuestionHeader-detail img')
            img_str = '#'.join(img.attrs.get('src') for img in images if img)
        return {'title_pictures': img_str}

    def extract_title_description(self) -> PartialType:
        """
        详情页的标题描述
        :return:
        """
        desc = self.element.get('excerpt', '')

        if self._detail_response and not desc:
            divs = self._detail_response.html.find('div.QuestionHeader-detail')
            desc = ''.join([div.text.replace('显示全部', '').replace('\u200b', '') for div in divs if div])
        desc = re.sub(r'<.*>|<em>|</em>', '', desc)
        return {'title_description': desc}

    def extract_relevant_query(self) -> PartialType:
        """
        清洗相关搜索关键词列表
        :return:
        """
        query_list = self.element.get('query_list', [])
        return {
            'relevant_query': [query_dict.get('query' '') for query_dict in query_list if isinstance(query_dict, dict)]
        }

    def extract_play_count(self) -> PartialType:
        """
       视频播放量
       :return:
       """
        return {
            'play_count': self.element.get('play_count', 0) or self.element.get('playCount', 0)
        }

    def extract_like_count(self) -> PartialType:
        return {
            'like_count': self.element.get('liked_count', 0)
        }

    def extract_comments(self, comment_count=0, comment_url=None) -> CommentType:
        """
        评论数据采集. 理论上该部分应该独立采集
        :return:
        """
        comments = []
        comment_count = comment_count if comment_count else self.info.get('comment_count')
        count = self.options.get('comment_count')
        if count == -1 or comment_count == 0:
            return {'comments': comments}
        comment_count = comment_count if count == 0 and comment_count > count else count
        data_type = self.type.replace(VIDEO_ANSWER, ANSWER)
        if comment_url is None:
            comment_url = COMMENT_URL.format(data_type=f'{data_type}s', id=self.info.get(f'{self.type}_id'))
        page_urls = generating_page_links(comment_url, total_num=comment_count)
        logger.info(f'start request links: {page_urls}')
        for responses in self.request_fn(page_urls):
            for response in responses:
                if response is None or (response and response.status_code != 200):
                    continue
                response_json = json.loads(response.text) or {}
                comment_infos = response_json.get('data', [])
                for comment_info in comment_infos:
                    if comment_count <= len(comments):
                        return {'comments': comments}
                    comment_content = comment_info.get('content', '')
                    if '<' in comment_content and '>' in comment_content:
                        comment_content = HTML(html=comment_content)
                        comment_content = ''.join([ele.text for ele in comment_content.find('p,a') if ele and ele.text])
                    info = {
                        'comment_id': comment_info.get('id', ''),
                        'comment_content': comment_content,
                        'comment_pub_time': comment_info.get('created_time', 0),
                        'comment_vote_count': comment_info.get('vote_count', 0),
                        'author_info': {},
                    }
                    reply_to_author = self.extract_author(comment_info.get('reply_to_author', {}).get('member', {}))
                    info['reply_to_author'] = reply_to_author.get('author_info', {})
                    info.update(self.extract_author(comment_info.get('author', {}).get('member', {})))
                    comments.append(info)

                if response_json.get('paging', {}).get('is_end', False):
                    break
        return {'comments': comments}

    def extract_meta_data(self, start_url, type_name, **kwargs) -> PartialType:
        """
        获取账号的回答、文章、视频、专栏、提问等数据
        :param start_url: 请求数据的接口
        :param type_name: 请求数据类型名称
        @ headers 是否需要加密参数
        :return: 返回对应数据集合
        """
        total_count = kwargs.pop('total_count', 0)
        if total_count == 0:
            return
        page_urls = generating_page_links(start_url, total_count)
        data_list = []
        for responses in self.request_fn(page_urls, **kwargs):
            for response in responses:
                if response is None or (response and response.status_code != 200):
                    continue
                response_json = json.loads(response.text) if response else {}
                infos = response_json.get('data', [])
                for info in infos:
                    if total_count <= len(data_list):
                        return {
                            type_name: data_list
                        }
                    extractor = None
                    if type_name in ('questions', 'following_questions'):
                        extractor = UserQuestionExtractor(info, self.options, self.request_fn, full_html=None)
                    elif type_name == 'pins':
                        extractor = UserPinExtractor(info, self.options, self.request_fn, full_html=None)
                    elif type_name in ('columns', 'following_columns'):
                        extractor = UserColumnExtractor(info, self.options, self.request_fn, full_html=None)
                    elif type_name in ('following', 'followers'):
                        extractor = UserFriendExtractor(info, self.options, self.request_fn, full_html=None)
                    elif type_name == 'following_topics':
                        extractor = UserFollowingTopicExtractor(info, self.options, self.request_fn, full_html=None)
                    else:
                        extractor = BaseExtractor(info, self.options, self.request_fn, full_html=None)
                    result = extractor.extract_data()
                    data_list.append(result)
                is_end = response_json.get('paging', {}).get('is_end', False)
                if not infos or is_end:
                    break
        return {type_name: data_list}


class QuestionExtractor(BaseExtractor):
    """
    热榜问题
    """

    def extract_data(self):
        question_info = self.extract_question().get('question_info') or {}
        count = self.options.get('drill_down_count')
        total_count = question_info.get('question_answer_count')
        if count > -1 and total_count > 0:
            total_count = count if 0 < count < total_count else total_count
            url = QUESTION_ANSWERS_URL.format(question_id=question_info.get('question_id', ''))
            result = self.extract_meta_data(start_url=url, total_count=total_count, type_name='answers') or {}
            question_info.update(result)
        return question_info


class UserExtractor(BaseExtractor):
    """
    用户信息
    """

    def extract_data(self):
        methods = [
            self.extract_user
        ]
        for method in methods:
            try:
                partial_info = method()
                if partial_info is None:
                    continue
                logger.warning(f'method: {method.__name__} return: {partial_info}')
                self.info.update(partial_info)
            except Exception as ex:
                logger.debug(f'method: {method.__name__} error:{ex}')

        user_id = self.info.get('user_url_token', '')
        # ********* 用户回答列表采集 ********* #
        total_count = self.info['user_answer_count']
        count = self.options.get('answer_count')
        sort = self.options.get('sort', '')
        if count > -1 and total_count > 0:
            start_url = USER_ANSWERS_URL.format(user_id=user_id)
            if sort == 'included':
                start_url = re.sub(r'/answers\?', '/marked-answers?', start_url)
            else:
                start_url = re.sub('sort_by=created', f'sort_by={sort}', start_url)
            total_count = count if 0 < count < total_count else total_count
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='answers',
                                            total_count=total_count) or {}
            self.info.update(result)

        # ********* 用户视频列表采集 ********* #
        total_count = self.info['user_zvideo_count']
        count = self.options.get('zvideo_count')
        if count > -1 and total_count > 0:
            total_count = count if 0 < count < total_count else total_count
            start_url = USER_VIDEO_URL.format(user_id=user_id)
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='zvideos',
                                            total_count=total_count) or {}
            self.info.update(result)

        # ********* 用户文章列表采集 ********* #
        total_count = self.info['user_articles_count']
        count = self.options.get('article_count')
        if count > -1 and total_count > 0:
            total_count = count if 0 < count < total_count else total_count
            start_url = USER_ARTICLE_URL.format(user_id=user_id)
            if sort == 'included':
                start_url = start_url.replace('/articles?', '/included-articles?'). \
                    replace('sort_by=created', 'sort_by=included')
            else:
                start_url = re.sub('sort_by=created', f'sort_by={sort}', start_url)
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='articles',
                                            x_zse_96=True,
                                            total_count=total_count) or {}
            self.info.update(result)

        # ********* 用户提问列表采集 ********* #
        total_count = self.info['user_question_count']
        count = self.options.get('question_count')
        if count > -1 and total_count > 0:
            total_count = count if 0 < count < total_count else total_count
            start_url = USER_QUESTION_URL.format(user_id=user_id)
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='questions',
                                            total_count=total_count) or {}
            self.info.update(result)

        # ********* 用户想法列表采集 ********* #
        total_count = self.info['user_pins_count']
        count = self.options.get('pin_count')
        if count > -1 and total_count > 0:
            total_count = count if 0 < count < total_count else total_count
            start_url = USER_PINS_URL.format(user_id=user_id)
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='pins',
                                            x_zse_96=True,
                                            total_count=total_count) or {}
            self.info.update(result)

        # ********* 用户专栏列表采集 ********* #
        total_count = self.info['user_columns_count']
        count = self.options.get('column_count')
        if count > -1 and total_count > 0:
            start_url = USER_COLUMN_URL.format(user_id=user_id)
            total_count = count if 0 < count < total_count else total_count
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='columns',
                                            total_count=total_count) or {}
            self.info.update(result)

        # ********* 用户关注的人列表采集 ********* #
        total_count = self.info['user_following_count']
        count = self.options.get('following')
        if count > -1 and total_count > 0:
            start_url = USER_FOLLOWEE_URL.format(user_id=user_id)
            total_count = count if 0 < count < total_count else total_count
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='following',
                                            total_count=total_count,
                                            x_zse_96=True) or {}
            self.info.update(result)

        # ********* 关注该用户的人列表采集 ********* #
        total_count = self.info['user_follower_count']
        count = self.options.get('followers')
        if count > -1 and total_count > 0:
            start_url = USER_FOLLOWERS_URL.format(user_id=user_id)
            total_count = count if 0 < count < total_count else total_count
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='followers',
                                            total_count=total_count,
                                            x_zse_96=True) or {}
            self.info.update(result)

        # ********* 用户关注的专栏列表采集 ********* #
        total_count = self.info['user_following_columns_count']
        count = self.options.get('following_columns')
        if count > -1 and total_count > 0:
            start_url = USER_FOLLOWING_COLUMNS_URL.format(user_id=user_id)
            total_count = count if 0 < count < total_count else total_count
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='following_columns',
                                            total_count=total_count,
                                            x_zse_96=True) or {}
            self.info.update(result)

        # ********* 用户关注的问题列表采集 ********* #
        total_count = self.info['user_following_question_count']
        count = self.options.get('following_questions')
        if count > -1 and total_count > 0:
            start_url = USER_FOLLOWING_QUESTIONS_URL.format(user_id=user_id)
            total_count = count if 0 < count < total_count else total_count
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='following_questions',
                                            total_count=total_count,
                                            x_zse_96=True) or {}
            self.info.update(result)

        # ********* 用户关注的话题列表采集 ********* #
        total_count = self.info['user_following_topic_count']
        count = self.options.get('following_topics')
        if count > -1 and total_count > 0:
            start_url = USER_FOLLOWING_TOPICS_URL.format(user_id=user_id)
            total_count = count if 0 < count < total_count else total_count
            result = self.extract_meta_data(start_url=start_url,
                                            type_name='following_topics',
                                            total_count=total_count,
                                            x_zse_96=True) or {}
            self.info.update(result)

        return self.info

    def extract_user(self) -> Dict[str, Dict[str, Union[List, int, str]]]:
        badges = self.element.get('badge', [])
        return {
            'user_id': self.element.get('id', ''),
            'user_name': self.element.get('name'),
            'user_url_token': self.element.get('url_token', ''),
            'user_head_img': self.element.get('avatar_url', ''),
            'user_is_org': self.element.get('is_org', False),
            'user_headline': self.element.get('headline', ''),
            'user_type': self.element.get('type', ''),
            'user_is_active': self.element.get('is_active', True),
            'user_description': re.sub(r'<.*>|</.*>', '', self.element.get('description', '')),
            'user_is_advertiser': self.element.get('is_advertiser', False),
            'user_is_vip': self.element.get('vip_info', {}).get('is_vip', False),
            'user_badges': [badge.get('description', '') for badge in badges if badge and isinstance(badge, dict)],
            'user_follower_count': self.element.get('follower_count', 0),
            'user_following_count': self.element.get('following_count', 0),
            'user_answer_count': self.element.get('answer_count', 0),
            'user_question_count': self.element.get('question_count', 0),
            'user_articles_count': self.element.get('articles_count', 0),
            'user_columns_count': self.element.get('columns_count', 0),
            'user_zvideo_count': self.element.get('zvideo_count', 0),
            'user_pins_count': self.element.get('pins_count', 0),
            'user_favorite_count': self.element.get('favorite_count', 0),  # 用户创建的收藏夹的数量
            'user_favorited_count': self.element.get('favorited_count', 0),  # 获得其余用户的收藏数
            'user_reactions_count': self.element.get('reactions_count', 0),
            'user_shared_count': self.element.get('shared_count', 0),
            'user_voteup_count': self.element.get('voteup_count', 0),  # 获得点赞数
            'user_thanked_count': self.element.get('thanked_count', 0),  # 获得喜欢数
            'user_following_columns_count': self.element.get('following_columns_count', 0),  # 关注的专栏数
            'user_following_topic_count': self.element.get('following_topic_count', 0),  # 关注的话题
            'user_following_question_count': self.element.get('following_question_count', 0),  # 关注的问题
            'user_following_favlists_count': self.element.get('following_favlists_count', 0),
            'user_participated_live_count': self.element.get('participated_live_count', 0),  # 参与的直播数
            'user_included_answers_count': self.element.get('included_answers_count', 0),  # 知乎收录的回答
            'user_included_articles_count': self.element.get('included_articles_count', 0),  # 知乎收录的文章
            'user_recognized_count': self.element.get('recognized_count', 0),  # 获得专业认可数
            'user_cover_url': self.element.get('cover_url', ''),
            'user_org_name': self.element.get('org_detail', {}).get('organization_name', ''),
            'user_org_industry': self.element.get('org_detail', {}).get('industry', ''),
            'user_org_url': self.element.get('home_page', ''),
            'user_org_lic_code': self.element.get('business_lic_code', '') or
                                 self.element.get('org_detail', {}).get('social_credit_code', '')
        }


class UserQuestionExtractor(UserExtractor):
    """
    用户问题
    """

    def extract_data(self):
        question_info = self.extract_question().get('question_info', {})
        count = self.options.get('drill_down_count')
        total_count = question_info.get('question_answer_count')
        if total_count > 0 and count > -1:
            total_count = count if 0 < count < total_count else total_count
            url = QUESTION_ANSWERS_URL.format(question_id=question_info.get('question_id', ''))
            answer_info = self.extract_meta_data(url, type_name='answers', total_count=total_count)
            question_info.update(answer_info)
        return question_info


class UserPinExtractor(UserExtractor):
    """
    用户想法
    """

    def extract_data(self):
        methods = [
            self.extract_author,
            self.extract_pin,
            self.extract_pin_content,
            self.extract_pin_pictures,
        ]
        for method in methods:
            try:
                partial_info = method()
                if partial_info is None:
                    continue
                logger.warning(f'method: {method.__name__} return: {partial_info}')
                self.info.update(partial_info)
            except Exception as ex:
                logger.debug(f'method: {method.__name__} error:{ex}')

        # ********* 采集想法的评论 ********* #
        self.info.update(self.extract_comments())
        return self.info

    def extract_pin(self) -> Dict[str, Union[str, int]]:
        return {
            'pin_title': self.element.get('excerpt_title', ''),
            'pin_type': self.element.get('type', ''),
            'pin_reaction_count': self.element.get('reaction_count', 0),
            'pin_like_count': self.element.get('like_count', 0),
            'pin_id': self.element.get('id', ''),
            'pin_edit_time': extract_time(self.element).get('pub_time', ''),
            'pin_pub_time': extract_time(self.element).get('edit_time', ''),
            'pin_source_url': urljoin(BASE_URL, self.element.get('url', '')),
            'comment_count': self.element.get('comment_count', 0),
        }

    def extract_pin_content(self) -> Dict[str, str]:
        """
        用户想法的内容
        """
        content = ''.join([content.get('content', '') for content in self.element.get('content', [])
                           if content and content.get('content', '')])
        content = re.sub(r'<.*>', '', content)
        return self.extract_content(content)

    def extract_pin_pictures(self) -> Dict[str, str]:
        """
        用户想法的图片
        """
        pic = '#'.join([pic.get('url', '') for pic in self.element.get('content', []) if pic and pic.get('url', '')])
        return {
            'pin_pictures': pic
        }


class UserColumnExtractor(UserExtractor):
    """
    用户专栏
    """

    def extract_data(self):
        column = self.element.get('column', {}) or self.element
        author = self.extract_author(column.get('author', {}))
        column_info = {
            'column_title': column.get('title', ''),
            'column_url': column.get('url', '').replace('api.', '').replace('columns', 'column'),
            'column_image_url': column.get('image_url', ''),
            'column_edit_time': column.get('updated', ''),
            'column_followers': column.get('followers', 0),
            'column_articles_count': column.get('articles_count', 0),
            'column_intro': column.get('intro', ''),
            'column_id': column.get('id', ''),
            'column_voteup_count': column.get('voteup_count', 0),
            'column_all_count': column.get('items_count', 0),
            'column_author': author
        }
        total_count = column_info['column_all_count']
        count = self.options.get('drill_down_count')
        if count > -1 and total_count > 0:
            total_count = count if 0 < count < total_count else total_count
            url = COLUMN_ITEMS_URL.format(column_id=column_info.get('column_id', ''))
            items = self.extract_meta_data(start_url=url,
                                           type_name='column_articles',
                                           total_count=total_count) or {}
            column_info.update(items)
        return column_info


class UserFriendExtractor(UserExtractor):
    """
    用户关注人或粉丝
    """

    def extract_data(self):
        return self.extract_user()


class UserFollowingTopicExtractor(UserExtractor):
    """
    用户关注的话题
    """

    def extract_data(self):
        topic = self.extract_topic()
        topic['feeds'] = self.extract_feed(topic)
        return topic

    def extract_topic(self):
        topic = self.element.get('topic', {}) or self.element or {}
        topic_api = topic.get('url', '')
        response = self.request_fn(topic_api)
        if response and response.status_code == 200:
            topic = json.loads(response.text)
        return {
            'topic_id': topic.get('id', ''),
            'topic_name': topic.get('name', ''),
            'topic_url': topic.get('url', '').replace('api/v4/topics', 'topic'),
            'topic_avatar_url': topic.get('avatar_url', ''),
            'topic_excerpt': topic.get('excerpt', ''),
            'topic_followers_count': topic.get('followers_count', 0),
            'topic_introduction': topic.get('introduction', ''),
            'topic_father_count': topic.get('father_count', 0),
            'topic_feed_count': topic.get('questions_count', 0),
            'topic_unanswered_count': topic.get('unanswered_count', 0),
            'is_super_topic': topic.get('is_super_topic_vote', False),
            'is_vote': topic.get('is_vote', False),
            'is_black': topic.get('is_black', False)
        }

    def extract_feed(self, topic):
        topic_feed_count = topic.get('topic_feed_count')
        topic_id = topic.get('topic_id')
        count = self.options.get('drill_down_count')
        # *********  采集话题下的feed ********* #
        if count > -1 and topic_feed_count > 0:
            topic_feed_count = count if 0 < count < topic_feed_count else topic_feed_count
            url = TOPIC_FEEDS_URL.format(topic_id=topic_id)
            page_urls = generating_page_links(url, total_num=topic_feed_count)
            feeds = []
            for responses in self.request_fn(page_urls):
                for response in responses:
                    if not response or response.status_code != 200:
                        continue
                    data = json.loads(response.text).get('data', [])
                    for feed in data:
                        target = feed.get('target', {})
                        info = BaseExtractor(target, self.options, self.request_fn).extract_data()
                        if len(feeds) >= topic_feed_count:
                            break
                        feeds.append(info)
                    if len(feeds) >= topic_feed_count:
                        break
            return feeds
