#### 免责声明：本项目涉及仅供学习交流使用。禁止将本项目或者Github源码用于任何商业目的。由此引发的任何法律纠纷与本人无关！
本程序支持关键词搜索、热榜、用户信息、回答、专栏文章、评论等信息的抓取。代码思路来源于facebook_scraper

**项目目录:**  
\___init_\__.py 为程序的对外统一入口  
__constants.py__ 常量  
__exceptions.py__ 自定义异常  
__extractors.py__ 数据清洗  
__page_iterators.py__ 简单的页面处理  
__zhihu_scraper.py__ 页面请求、cookie设置  
__zhihu_types.py__ 类型提示、检查。项目自定义类型  
__注意事项__ 项目内有部分异步操作，在模块引用之前需要使用猴子补丁; 同时该项目没有对ip限制、登录做针对性处理
```
# 猴子补丁
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
from zhihu_crawl import *
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
__热点问题采集使用案例__:

```
if __name__ == '__main__':
    # 采集 前10个问题, 每个问题采集10条回答
    for info in hot_questions_crawl(question_count=10, answer_count=10):
        print(info)

    # 可传入period 指定热榜性质。如小时榜、日榜、周榜、月榜
    # 传入domains 采集指定主题的问题
    for info in hot_questions_crawl(question_count=10, period='day', domains=['1001', 1003]):
        print(info)
```

**zhihu_crawl目录:**  工具类

