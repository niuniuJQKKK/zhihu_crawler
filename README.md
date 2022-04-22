#### 免责声明：本项目涉及仅供学习交流使用。禁止将本项目或者Github源码用于任何商业目的。由此引发的任何法律纠纷与本人无关！
支持获取知乎的关键词搜索、热榜、用户、回答、专栏文章、评论、关联关键词、关联文章等信息。代码思路来源于facebook_scraper

### 项目目录:
#### zhihu_crawler 核心代码区
* __\_\_init\_\_.py__ 为程序的对外统一入口  
* __constants.py__ 常量  
* __exceptions.py__ 自定义异常  
* __extractors.py__ 数据清洗  
* __page_iterators.py__ 页面处理  
* __zhihu_scraper.py__ 页面请求、cookie设置  
* __zhihu_types.py__ 类型提示、检查。项目自定义类型 
#### common 重要参数的加密
#### zhihu_utils 工具包
__注意事项__ 项目内有部分异步操作，在模块引用之前需要使用猴子补丁; 该项目已对核心参数进行了js逆向，但没有对ip限制、登录做针对性处理。
如有海量数据获取需求，可自行搭建IP池和cookie池。

```
# 猴子补丁
from gevent import monkey
monkey.patch_all()
from zhihu_crawler import *
```

__搜索采集使用案例__:
```
if __name__ == '__main__':
    for info in search_crawl(key_word='天空', count=10):
        print(info)
# 可传入data_type 指定搜索类型
    for info in search_crawl(key_word='天空', count=10, data_type='answer'):
        print(info)
```

__用户信息采集使用案例（数据样例请游览user_info.json）__:
```
    for info in user_crawler('wo-men-de-tai-kong',
                             answer_count=2,
                             zvideo_count=3,
                             question_count=2,
                             article_count=3,
                             column_count=2,
                             pin_count=3,
                             following=3,
                             followers=3,
                             following_columns=3,
                             following_questions=3,
                             following_topics=3,
                             comment_count=3,
                             drill_down_count=3,
                             ):
        print(info)
        

```

__热点问题采集使用案例（数据样例请游览hot_question.json）__:

```
if __name__ == '__main__':
    # 采集 前10个问题, 每个问题采集10条回答
    for info in hot_questions_crawl(question_count=10, drill_down_count=10):
        print(info)

    # 可传入period 指定热榜性质。如小时榜、日榜、周榜、月榜
    # 传入domains 采集指定主题的问题
    for info in hot_questions_crawl(question_count=10, period='day', domains=['1001', 1003]):
        print(info)
```

