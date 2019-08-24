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


class DefaultValuePipeline(object):

    def process_item(self,item, spider): 
        
        if isinstance(item, InformationItem) :
            
            item.setdefault("city","null")
            item.setdefault("province","null")   
            item.setdefault("brief_introduction","null")
            item.setdefault("sentiment","null")
            item.setdefault("vip_level","null")
            item.setdefault("authentication","null")
            item.setdefault("person_url","null")
            item.setdefault("labels","null")
            item.setdefault("birthday","1900-01-01")  # 日期类型 
            item.setdefault("gender","null") 
            item.setdefault("sex_orientation","null")
            
        elif isinstance(item, TweetsItem ) :
            item.setdefault("tool","null")
            item.setdefault("image_url","null")
            item.setdefault("video_url","null")
            item.setdefault("location","null")
            item.setdefault("location_map_info","null")
            item.setdefault("origin_weibo","null")

        spider.logger.info(("default value item", item)) 
        return item 
        


class PgsqlDBPipeline(object): 
        
    def open_spider(self,spider) : 
        
        hostname = LOCAL_MONGO_HOST 
        username = PG_USER_NAME 
        password = PG_USER_PW 
        database = PG_DATABASE  

        self.conn = psycopg2.connect(host = hostname, user = username, password = password, dbname = database)
        self.cur = self.conn.cursor() 
        self.information_insert_str = "insert into information values('{id}','{nick_name}','{gender}','{province}','{city}',\
          '{brief_introduction}', '{birthday}','{tweets_num}','{follows_num}','{fans_num}','{sex_orientation}','{sentiment}',\
           '{vip_level}','{authentication}','{person_url}','{labels}','{crawl_time}')" 
        self.tweet_insert_str = "insert into tweet values('{id}','{weibo_url}','{created_at}','{like_num}','{repost_num}',\
            '{comment_num}','{content}','{user_id}','{tool}','{image_url}','{video_url}','{location}','{location_map_info}',\
                '{origin_weibo}','{crawl_time}')" 
        self.relationship_insert_str = "insert into relationship values({id},{crawl_time},{fan_id},{followed_id})"  
        self.comment_insert_str = "insert into comment values ({id},'{comment_user_id}','{content}','{weibo_url}',\
            '{created_at}','{like_num}','{crawl_time}' )"
        
        spider.logger.info("open spider")
    
    def close_spider(self, spider):
        self.cur.close() 
        self.conn.close() 

    def process_item(self, item,spider): 
        
        # spider.logger.info(("process_item",item))
        
        if isinstance(item, RelationshipsItem) :
            try :
                self.cur.execute(self.relationship_insert_str.format_map(dict(item)))  
                self.conn.commit() 
            except Exception as e : 
                spider.logger.error(e)
                self.conn.rollback() 
        elif isinstance(item, TweetsItem) :

            spider.logger.info(self.tweet_insert_str.format_map(dict(item)))
            try :
                self.cur.execute(self.tweet_insert_str.format_map(dict(item))) 
                self.conn.commit()
            except Exception as e : 
                spider.logger.error(e)
                self.conn.rollback() 
        elif isinstance(item, InformationItem): 
            try:
                self.cur.execute(self.information_insert_str.format_map(dict(item))) 
                self.conn.commit()
            except Exception as e :
                spider.logger.error(e)
                self.conn.rollback()
        elif isinstance(item, CommentItem) : 
            try :
                self.cur.execute(self.comment_insert_str.format_map(dict(item))) 
                self.conn.commit() 
            except Exception as e : 
                spider.logger.error(e) 
                self.conn.rollback()  
        return item
