from gevent import monkey
monkey.patch_all()
from zhihu_crawler import *

if __name__ == '__main__':
    set_proxy({'http': 'http://127.0.0.1:8125', 'https': 'http://127.0.0.1:8125'})
    # set_cookie({'d_c0': 'AIBfvRMxmhSPTk1AffR--QLwm-gDM5V5scE=|1646725014'})
    # for info in search_crawler(key_word='滴普', count=30):
    #     print(info)
    #     pass

    # for info in common_crawler(task_id='528030527', data_type='question', comment_count=3):
    #     # print(info)
    #     pass

    for info in user_crawler('wo-men-de-tai-kong',
                             answer_count=50,
                             comment_count=3,
                             drill_down_count=3,
                             ):
        print(info)

    # for info in hot_questions_crawler(question_count=2, drill_down_count=2, comment_count=2):
    #     print(info)
    #     ...

    # for info in hot_list_crawler(drill_down_count=3):
    #     print(info)

    # print(top_search_crawl())
