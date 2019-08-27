# -*- coding: utf-8 -*-
import pymongo
from pymongo.errors import DuplicateKeyError
from sina.items import RelationshipsItem, TweetsItem, InformationItem, CommentItem
from sina.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME   

from sina.settings import LOCAL_PG_HOST, LOCAL_PG_PORT , PG_USER_NAME , PG_USER_PW ,PG_DATABASE  
from sina.settings import QQAI_APPID, QQAI_APPKEY 
import psycopg2 

import qqai
import re 


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


class EscapePipeline(object):
    def process_item( self,item,spider) :
        if 'content' in item:  
            item["content"] = item["content"].replace("'"," ")  
        if isinstance(item,InformationItem) : 
            item["brief_introduction"] = item["brief_introduction"].replace("'"," ")  
        return item
             


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
        
class ItemValidCheckPipeline(object): 
    def __init__(self):
        datepattern = '([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))'
        self.datePattern = re.compile(datepattern)
    
    def _date_validate(self,date_str) : 
        if self.datePattern.match(date_str) :
            return True 
        return False 
    
    def process_item(self, item, spider):
        if isinstance(item, InformationItem): 
            if not self._date_validate(item["birthday"]):
                item["birthday"] = "1900-01-01"
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
        self.relationship_insert_str = "insert into relationship values('{id}','{fan_id}','{followed_id}','{crawl_time}')"  
        self.comment_insert_str = "insert into comment values ('{id}','{comment_user_id}','{content}','{weibo_url}',\
            '{created_at}','{like_num}','{crawl_time}','{polar}','{polar_confidence}')" 
        
    
    def close_spider(self, spider):
        self.cur.close() 
        self.conn.close() 

    def process_item(self, item,spider): 
        spider.logger.info(("process_item by pgsql saver ",item))
        if isinstance(item, RelationshipsItem) : 
            try :
                self.cur.execute(self.relationship_insert_str.format_map(dict(item)))  
                self.conn.commit() 
            except Exception as e : 
                spider.logger.error(e)
                self.conn.rollback() 
        elif isinstance(item, TweetsItem) :
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


class QQAITextPolarPipeline(object): 
    
    def __init__(self):
        self.handler = qqai.nlp.text.TextPolar(QQAI_APPID, QQAI_APPKEY) 
    
    def process_item(self,item, spider) : 

        if isinstance(item, CommentItem) : 
            try :
                result = self.handler.run(item["content"][:60])  # 仅能够处理69个字符串
                if result['ret'] == 0 :
                    item["polar"]  = result["data"]["polar"] 
                    item["polar_confidence"] = result["data"]["confd"]   
            except Exception as e : 
                item["polar"] = "null" 
                item["polar_confidence"] = "null"
                spider.logger.error(("textpolar", e))  
        return item