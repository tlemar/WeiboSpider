# encoding: utf-8
import random

import pymongo


import requests 
from sina.settings import LOCAL_MONGO_PORT, LOCAL_MONGO_HOST, DB_NAME 
from scrapy.http import Request 
import re 
import logging

class CookieMiddleware(object):
    """
    每次请求都随机从账号池中选择一个账号去访问
    """

    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.account_collection = client[DB_NAME]['account']

    def process_request(self, request, spider):
        all_count = self.account_collection.find({'status': 'success'}).count()
        if all_count == 0:
            raise Exception('当前账号池为空')
        random_index = random.randint(0, all_count - 1)
        random_account = self.account_collection.find({'status': 'success'})[random_index]
        request.headers.setdefault('Cookie', random_account['cookie'])
        request.meta['account'] = random_account


class RedirectMiddleware(object):
    """
    检测账号是否正常
    302 / 403,说明账号cookie失效/账号被封，状态标记为error
    418,偶尔产生,需要再次请求
    """

    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.account_collection = client[DB_NAME]['account']

    def process_response(self, request, response, spider):
        http_code = response.status
        if http_code == 302 or http_code == 403:
            self.account_collection.find_one_and_update({'_id': request.meta['account']['_id']},
                                                        {'$set': {'status': 'error'}}, )
            return request
        elif http_code == 418:
            spider.logger.error('ip 被封了!!!请更换ip,或者停止程序...')
            return request
        else:
            return response


class IPProxyMiddleware(object):

    def fetch_proxy(self):
        # 如果需要加入代理IP，请重写这个函数
        # 这个函数返回一个代理ip，'ip:port'的格式，如'12.34.1.4:9090'  
        try :
            r = requests.get("http://api.ip.data5u.com/dynamic/get.html?order=a06943e591dd8d8e290ee92fbfa13c02&sep=3")
            content = r.content.decode("utf-8").strip()  
            if "过期" in content :
                return None 
            return content 
        except Exception :
            print("获取ip地址，失败。") 
            return None 

    def process_request(self, request, spider):
        proxy_data = self.fetch_proxy()
        if proxy_data:
            current_proxy = f'http://{proxy_data}'
            spider.logger.debug(f"当前代理IP:{current_proxy}")
            request.meta['proxy'] = current_proxy   


        


            
class UserDistanceMiddleware(object):
    
    def __init__(self, max_distance, stats, verbose_stats = False, prio=1) :
        self.max_distance = max_distance 
        self.stats = stats
        self.verbose_stats = verbose_stats 
        self.prio = prio 
    
    @classmethod 
    def from_crawler(cls, crawler):
        settings = crawler.settings 
        max_distance = settings.getint("USER_DISTANCE_LIMIT")  
        verbose = settings.getbool("USER_DISTANCE_VERBOSE") 
        prio = settings.getint("USER_DISTANCE_PRIORITY") 
        return cls(max_distance, crawler.stats, verbose, prio) 

    def process_spider_output(self, response, result, spider):  

        # def isUserRequest(request):
        #     "根据url规则来判断一个请求是否为新用户的url请求"  
        #     if isinstance(request, Request) :
        #         url = request.url  
        #         spider.logger.info("target url is "+ url)
        #         # 用户请求的url的形式为 https://weibo.cn/xxxx/info
        #         return url.endswith("info")
        #     return False 
        
        def _filter(request) :  
            if isinstance(request,Request) and request.meta.get("user",False) :# and isUserRequest(request):                 
                spider.logger.info((request, request.meta))
                user_distance = response.meta["user_distance"] + 1 
                request.meta["user_distance"] = user_distance   
                spider.logger.info(("user distance is:",user_distance,request.url))
                # if self.prio:
                #     request.priority -= user_distance * self.prio 

                if self.max_distance and user_distance > self.max_distance :
                    spider.logger.info("Ignore user link(user distance > %(max_distance)d) : %(requrl)s ",
                    {"max_distance":self.max_distance, "requrl":request.url},
                    extra= {"spider":spider} )  
                    return False
                spider.logger.info(("request meta",request.meta))

            return True 

        if ("user_distance" not in response.meta) :
            response.meta["user_distance"] = 0 

        expr = (r for r in result or () if _filter(r))
        return  expr  