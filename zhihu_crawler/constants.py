# 知乎基础url
BASE_URL = 'https://www.zhihu.com/'
# 知乎基础api
BASE_API = 'https://api.zhihu.com/'
# 知乎搜索综合url
SEARCH_URL = 'https://api.zhihu.com/search?t=general&q={key_word}&correction=1&offset=0&limit=20&filter_fields=&' \
             'lc_idx=0&show_all_topics=0&search_source=Filter&vertical={data_type}'
# 视频请求url
VIDEO_BASE_URL = 'https://lens.zhihu.com/api/v4/videos/'
# 文章url
ARTICLE_BASE_URL = 'https://zhuanlan.zhihu.com/p/'
# 单个问题回答的接口，发布时间排序
QUESTION_ANSWERS_URL = 'https://api.zhihu.com/questions/{question_id}/answers?include=data%5B%2A%5D.is_normal%2' \
                      'Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2' \
                      'Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2' \
                      'Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2' \
                      'Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2C' \
                      'question%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Creaction_instruction%2' \
                      'Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3' \
                      'Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cvip_info%2' \
                      'Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&' \
                      'limit=20&offset=0&platform=desktop&sort_by=updated'
# 用户回答的接口 时间排序
USER_ANSWERS_URL = 'https://api.zhihu.com/members/{user_id}/answers?include=data%5B*%5D.is_normal%2' \
                   'Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2' \
                   'Ccollapse_reason%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2' \
                   'Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2' \
                   'Cmark_infos%2Ccreated_time%2Cupdated_time%2Creview_info%2Cexcerpt%2Cis_labeled%2Clabel_info%2' \
                   'Crelationship.is_authorized%2Cvoting%2Cis_author%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3' \
                   'Bdata%5B*%5D.vessay_info%3Bdata%5B*%5D.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3' \
                   'Bdata%5B*%5D.author.vip_info%3Bdata%5B*%5D.question.has_publishing_draft%2Crelationship&' \
                   'offset=0&limit=20&sort_by=created'
# 用户视频的接口
USER_VIDEO_URL = 'https://www.zhihu.com/api/v4/members/{user_id}/zvideos?offset=0&limit=20'

# 用户文章的接口
USER_ARTICLE_URL = 'https://www.zhihu.com/api/v4/members/{user_id}/articles?include=data%5B*%5D.comment_count%2C' \
                   'suggest_edit%2Cis_normal%2Cthumbnail_extra_info%2Cthumbnail%2Ccan_comment%2Ccomment_permission%2C' \
                   'admin_closed_comment%2Ccontent%2Cvoteup_count%2Ccreated%2Cupdated%2Cupvoted_followees%2Cvoting%2C' \
                   'review_info%2Cis_labeled%2Clabel_info%3Bdata%5B*%5D.vessay_info%3Bdata%5B*%5D.author.badge' \
                   '%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B*%5D.author.vip_info%3B&' \
                   'offset=0&limit=20&sort_by=created'

# 用户问题列表接口
USER_QUESTION_URL = 'https://api.zhihu.com/members/{user_id}/questions?include=data%5B*%5D.created%2' \
                    'Canswer_count%2Cfollower_count%2Cauthor%2Cadmin_closed_comment&offset=0&limit=20'

# 用户想法列表接口
USER_PINS_URL = 'https://www.zhihu.com/api/v4/members/{user_id}/pins?offset=0&limit=20&includes=' \
                'data%5B*%5D.upvoted_followees%2Cadmin_closed_comment'

# 用户专栏列表接口
USER_COLUMN_URL = 'https://api.zhihu.com/members/{user_id}/column-contributions?include=data%5B*%5D.' \
                  'column.intro%2Cfollowers%2Carticles_count%2Cvoteup_count%2Citems_count&offset=0&limit=20'
# 专栏文章列表接口
COLUMN_ITEMS_URL = 'https://api.zhihu.com/columns/{column_id}/items?offset=0&limit=20'

# 用户所关注的人列表接口
USER_FOLLOWEE_URL = 'https://www.zhihu.com/api/v4/members/{user_id}/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&offset=0&limit=20'

# 关注该账号的人列表的接口
USER_FOLLOWERS_URL = 'https://www.zhihu.com/api/v4/members/{user_id}/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&offset=0&limit=20'

# 用户关注的专栏列表接口
USER_FOLLOWING_COLUMNS_URL = 'https://www.zhihu.com/api/v4/members/{user_id}/following-columns?include=data%5B*%5D.intro%2Cfollowers%2Carticles_count%2Cvoteup_count%2Citems_count&offset=0&limit=20'

# 用户关注的话题列表接口
USER_FOLLOWING_TOPICS_URL = 'https://www.zhihu.com/api/v4/members/{user_id}/following-topic-contributions?include=data%5B*%5D.topic.introduction&offset=0&limit=20'

# 用户关注的问题的列表接口
USER_FOLLOWING_QUESTIONS_URL = 'https://www.zhihu.com/api/v4/members/{user_id}/following-questions?include=data%5B*%5D.created%2Canswer_count%2Cfollower_count%2Cauthor&offset=0&limit=20'

# 单条回复url
ANSWER_BASE_URL = 'https://www.zhihu.com/question/{question_id}/answer/{answer_id}'
# 热搜
TOP_SEARCH_URL = 'https://www.zhihu.com/api/v4/search/top_search'
# 话题
TOPIC_BASE_URL = 'https://www.zhihu.com/topic/'
# 评论url
COMMENT_URL = 'https://api.zhihu.com/{data_type}/{id}/comments?order=reverse&limit=20&offset=0&status=open'


# x-zse-93
X_ZSE_93 = '101_3_2.0'

# 类型
ANSWER = 'answer'  # 问答
VIDEO_ANSWER = 'videoanswer'  # 视频类问答
VIDEO = 'zvideo'   # 视频
ARTICLE = 'article'  # 文章
GENERAL = 'general'  # 杂志文章 需要付费
QUESTION = 'question'  # 问题
TOPIC = 'topic'  # 话题
USER = 'user'  # 账号
WIKI_BOX = 'wiki_box'

# 协程数
ASYNC_COUNT = 5


#  翻页数
DEFAULT_PAGE_LIMIT = 5

# 采集评论数
DEFAULT_COMMENT_COUNT = 50

# 默认请求休眠时间
DEFAULT_REQUESTS_TIMEOUT = 5

# -------- 搜索过滤条件 ---——- #
