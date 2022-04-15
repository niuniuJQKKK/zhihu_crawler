from gevent import monkey
monkey.patch_all()
from zhihu_crawler import *

if __name__ == '__main__':
    # for info in search_crawler(key_word='天空', count=3, drill_down_count=3, comment_count=4):
    #     print(info)
    #     pass

    # for info in common_crawler(task_id='20589123', data_type='question', drill_down_count=3, comment_count=3):
    #     print(info)
    #     pass

    # for info in user_crawler('wo-men-de-tai-kong',
    #                          answer_count=2,
    #                          zvideo_count=3,
    #                          question_count=2,
    #                          article_count=3,
    #                          column_count=2,
    #                          pin_count=3,
    #                          following=3,
    #                          followers=3,
    #                          following_columns=3,
    #                          following_questions=3,
    #                          following_topics=3,
    #                          comment_count=3,
    #                          drill_down_count=3,
    #                          ):
    #     print(info)

    for info in hot_questions_crawler(question_count=1, drill_down_count=2):
        print(info)
