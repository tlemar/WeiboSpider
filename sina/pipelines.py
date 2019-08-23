# -*- coding: utf-8 -*-
import pymongo
from pymongo.errors import DuplicateKeyError
from sina.items import RelationshipsItem, TweetsItem, InformationItem, CommentItem
from sina.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME   

from sina.settings import LOCAL_PG_HOST, LOCAL_PG_PORT , PG_USER_NAME , PG_USER_PW ,PG_DATABASE 
import psycopg2 


class MongoDBPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        db = client[DB_NAME]
        self.Information = db["Information"]
        self.Tweets = db["Tweets"]
        self.Comments = db["Comments"]
        self.Relationships = db["Relationships"]

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, RelationshipsItem):
            self.insert_item(self.Relationships, item)
        elif isinstance(item, TweetsItem):
            self.insert_item(self.Tweets, item)
        elif isinstance(item, InformationItem):
            self.insert_item(self.Information, item)
        elif isinstance(item, CommentItem):
            self.insert_item(self.Comments, item)
        return item

    @staticmethod
    def insert_item(collection, item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            """
            说明有重复数据
            """
            pass 


class PgsqlDBPipeline(object): 

    def init_db(self) : 
        pass 
        
        
    def open_spider(self,spider) :
        hostname = LOCAL_MONGO_HOST 
        username = PG_USER_NAME 
        password = PG_USER_PW 
        database = PG_DATABASE  

        self.conn = psycopg2.connect(host = hostname, user = username, password = password, dbname = database)
        self.cur = self.conn.cursor() 
        self.information_insert_str = "insert into infomation value({id}, {crawl_time},{nick_name},{gender},{province},\
            {vip_level},{tweets_num},{follows_num},{fans_num},{city},{brief_introduct},{birthday},{authentication},\
                {labels},{sex_orientation},{sentiment})" 
        self.tweet_insert_str = "insert into tweet values({id},{crawl_time},{weib_url},{user_id},{created_at},{tool},\
            {like_num},{repost_num},{comment_num},{image_url},{content},{video_url},{orgin_weibo})" 
        self.relationship_insert_str = "insert into relationships value({id},{crawl_time},{fan_id},{followed_id})"  
        self.comment_insert_str = "insert into comments value ({id},{crawl_time},{weibo_url},{comment_user_id},{content},{like_num},{create_at} )"
        
    
    def close_spider(self, spider):
        self.cur.close() 
        self.conn.close() 

    def process_item(self, item,spider):
        self.cur.execute("")  
        if isinstance(item, RelationshipsItem) :
            # 
            self.cur.execute() 
        elif isinstance(item, TweetsItem) :
            # 
        elif isinstance(item, InformationItem): 
            # 
        elif isinstance(item, Comment) : 
            # 
        
        self.conn.commit() 

        return item
