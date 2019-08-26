# -*- coding: utf-8 -*-

BOT_NAME = 'sina'

SPIDER_MODULES = ['sina.spiders']
NEWSPIDER_MODULE = 'sina.spiders'

ROBOTSTXT_OBEY = False

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
}

# CONCURRENT_REQUESTS 和 DOWNLOAD_DELAY 根据账号池大小调整 目前的参数是账号池大小为200

CONCURRENT_REQUESTS = 10

DOWNLOAD_DELAY = 0.5
DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'sina.middlewares.CookieMiddleware': 300,
    'sina.middlewares.RedirectMiddleware': 200,
    'sina.middlewares.IPProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101
}

SPIDER_MIDDLEWARES = {

    # "sina.depth.DepthMiddleware":99,
    # "sina.middlewares.UserDistanceMiddleware":99
    # "sina.middlewares.DepthMiddleware":100
}


# items go through from lower valued to higher valued classes ,从低到高处理方式 
ITEM_PIPELINES = {
    'sina.pipelines.MongoDBPipeline': 300, 
    'sina.pipelines.PgsqlDBPipeline':500,    # save to db 
    'sina.pipelines.DefaultValuePipeline':100 ,
    'sina.pipelines.QQAITextPolarPipeline': 100,
    "sina.pipelines.ItemValidCheckPipeline":400,
    "sina.pipelines.EscapePipeline":400
} 

# MongoDb 配置

LOCAL_MONGO_HOST = '127.0.0.1'
LOCAL_MONGO_PORT = 27017
DB_NAME = 'Sina' 


# Postgresql congfig 
LOCAL_PG_HOST = "127.0.0.1" 
LOCAL_PG_PORT = 5432 
PG_USER_NAME = "postgres" 
PG_USER_PW = "root"  
PG_DATABASE = "sina"


# Redis 配置
LOCAL_REDIS_HOST = '127.0.0.1'
LOCAL_REDIS_PORT = 6379

# Ensure use this Scheduler
SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"

# Ensure all spiders share same duplicates filter through redis
DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"

# Redis URL
REDIS_URL = 'redis://{}:{}'.format(LOCAL_REDIS_HOST, LOCAL_REDIS_PORT)

# Number of Hash Functions to use, defaults to 6
BLOOMFILTER_HASH_NUMBER = 6

# Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
BLOOMFILTER_BIT = 31

# Persist
SCHEDULER_PERSIST = True

# IP
DOWNLOAD_TIMEOUT = 10

RETRY_TIMES = 15

# adjust the scheduler value for different values  
PRIORITY_TWEET = 0
PRIORITY_USER = 0 
PRIORITY_COMMENT = 10
PRIORITY_RELATIONSHIP = 0

# Miximum Number for Tweet and Comment 

MAXIMUM_PAGE_OF_TWEET = 100 
MAXIMUM_PAGE_OF_COMMENT = 100  
MAXIMUM_PAGE_OF_RELATIONSHIP = 100  

# control the link degree 
MAX_LINK_DEGREE =  1

# depth contol  
DEPTH_LIMIT = 0
DEPTH_STATS_VERBOSE = True


# Log settings 
LOG_LEVEL = "INFO"
LOG_FILE = "weibo_spider.log"  
LOG_FORMAT = "%(name)-12s: %(levelname)-8s %(filename)s  %(funcName)s  ： %(message)s  "


USER_DISTANCE_LIMIT = 1

# qqai app config 
QQAI_APPID = "2121003566" 
QQAI_APPKEY = "GCjiqiVgOcT5osVx"  