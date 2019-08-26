
DROP DATABASE sina;
create DATABASE sina;   --如果有重复数据库，会报错，但是不会中止程序 

\c sina; 

create table if not EXISTS Tweet(
    id  TEXT PRIMARY KEY,
    weibo_url TEXT,
    created_at TIMESTAMP,
    like_num int,
    repost_num int,
    comment_num int, 
    content TEXT, 
    user_id BIGINT, 
    tool TEXT,
    image_url TEXT, 
    video_url TEXT, 
    location TEXT, 
    location_map_info TEXT, 
    origin_weibo TEXT,
    crawl_time BIGINT
);

CREATE table if not EXISTS Information(
    id BIGINT PRIMARY KEY,
    nick_name TEXT,
    gender TEXT,
    province TEXT,
    city TEXT,
    brief_inftroduction TEXT,
    brithday Date,
    tweets_num INT,
    follows_num INT,
    fans_num INT,
    sex_orientation TEXT,
    sentiment TEXT,
    vip_level TEXT,
    authentication TEXT,
    person_url TEXT,
    labels TEXT,
    crawl_time BIGINT
);

create table if not EXISTS Relationship (
    id  TEXT PRIMARY KEY,
    fan_id BIGINT,
    followed_id BIGINT,
    crawl_time BIGINT
);

CREATE table if not EXISTS Comment(
    id TEXT PRIMARY KEY,
    comment_user_id  BIGINT ,
    CONTENT TEXT,
    weibo_url TEXT,
    created_at TIMESTAMP,
    like_num INT,
    crawl_time BIGINT,
    polar int ,
    polar_confidence float
)