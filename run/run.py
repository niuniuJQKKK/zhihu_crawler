from gevent import monkey
monkey.patch_all()
from zhihu_crawler import *


def get_proxy():
    """
    获取代理
    """
    proxy_meta = {}
    # 代理服务器
    proxy_host = "http-dyn.abuyun.com"
    proxy_port = "9020"
    # 代理隧道验证信息
    proxy_user = "H4761267I6DC816D"
    proxy_pass = "ED09104BE93C5DC3"
    proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxy_host,
        "port": proxy_port,
        "user": proxy_user,
        "pass": proxy_pass,
    }
    return {'http': proxy_meta, 'https': proxy_meta}


if __name__ == '__main__':
    set_proxy(get_proxy())
    set_cookie({'d_c0': 'AvAQDHN4mxSPTtVyJn9kQSMi43V1kPWH_qc=|1646810832'})
    for info in search_crawler(key_word='滴普', nums=3, agree_users=True):
        # print(info)
        pass

    # for info in common_crawler(task_id='528030527', data_type='question', drill_down_count=3, comment_count=3):
    #     print(info)
    #     pass

    # for info in user_crawler('wo-men-de-tai-kong',
    #                          column_count=1,
    #                          comment_count=15,
    #                          drill_down_count=15,
    #                          ):
    #     print(info)

    # for info in hot_questions_crawler(question_count=2, drill_down_count=2, comment_count=2):
    #     # print(info)
    #     ...

    # for info in hot_list_crawler(drill_down_count=3, comment_count=3):
    #     print(info)

    # print(top_search_crawl())
