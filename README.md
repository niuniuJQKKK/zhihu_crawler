#### 免责声明：本项目涉及仅供学习交流使用。禁止将本项目或者Github源码用于任何商业目的。由此引发的任何法律纠纷与本人无关！
环境搭建好，拿来即用。支持获取知乎的关键词搜索、热榜、用户、回答、专栏文章、评论、关联关键词、关联文章等信息。代码思路来源于facebook_scraper


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

__安装__:
```
pip install zhihu_crawler
```
__使用案例__:
```
# 猴子补丁
from gevent import monkey
monkey.patch_all()
from zhihu_crawler.zhihu_crawler import *

    if __name__ == '__main__':
        # 设置代理; 如采集量较大，建议每次请求都切换代理
        set_proxy({'http': 'http://127.0.0.1:8125', 'https': 'http://127.0.0.1:8125'})

        # 设置cookie
        set_cookie({'d_c0': 'AIBfvRMxmhSPTk1AffR--QLwm-gDM5V5scE=|1646725014'})

        # 搜索采集使用案例:
        for info in search_crawl(key_word='天空', count=10):
            print(info)

        # 可传入data_type 指定搜索类型
        for info in search_crawl(key_word='天空', count=10, data_type='answer'):
            print(info)

        # 用户信息回答列表使用案例(采集该用户信息及50条回答信息,每条回答包含50条评论):
        for info in user_crawler('wo-men-de-tai-kong',
                                 answer_count=50,
                                 comment_count=50
                                 ):
            print(info)

        # 用户信息提问列表使用案例(采集该用户信息及10条问题信息,每条问题包含10条回答，每条回答包含50条评论):
        for info in user_crawler('wo-men-de-tai-kong',
                                 question_count=10,
                                 drill_down_count=10,
                                 comment_count=50
                                 ):
            print(info)

        # 热点问题采集使用案例
        # 采集 前10个问题, 每个问题采集10条回答
        for info in hot_questions_crawl(question_count=10, drill_down_count=10):
            print(info)

        # 可传入period 指定热榜性质。如小时榜、日榜、周榜、月榜
        # 传入domains 采集指定主题的问题
        for info in hot_questions_crawl(question_count=10, period='day', domains=['1001', 1003]):
            print(info)
```

