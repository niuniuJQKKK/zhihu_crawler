from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
from zhihu_crawl import *

if __name__ == '__main__':
    for info in search_crawl(key_word='天空', count=10):
        print(info)

    # for info in common_crawl(task_id='20589123', data_type='question', answer_count=3):
    #     pprint(info)
    #     pass

    # for info in user_crawl('wo-men-de-tai-kong', answer_count=20):
    #     print(info)
    #
    for info in hot_questions_crawl(question_count=1, answer_count=2):
        print(info)
