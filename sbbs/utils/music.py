# coding:utf8
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Date, DateTime
from redis import StrictRedis
redis = StrictRedis(host='127.0.0.1', port=6379)

# sqlalchemy设置，生成session。供定时爬虫使用
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'sbbs'
USERNAME = 'yk'
PASSWORD = 'yk123456'
# DB_URI的格式：dialect（mysql/sqlite）+driver://username:password@host:port/database
DB_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
engine = create_engine(DB_URI)
Session = sessionmaker(engine)
session = Session()
# 1. 必须继承自sqlalchemy的某个基类
Base = declarative_base(engine)
# 2. 定义好一些属性，与user表中的字段进行映射，并且这个属性要属于某个类型


class MusicModel(Base):
    # 设置映射到数据库中的表名
    __tablename__ = 'music'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_time = Column(String(100))
    song_name = Column(String(100))
    artist_name = Column(String(100))
    song_id = Column(Integer)

base_url = 'http://music.163.com/'
discover_url = 'http://music.163.com/discover'
hot_list = 8  # 热门推荐前八歌单
list_front = 4  # 歌单中选两首
all_songs = 10


# 歌曲爬虫
def music_spider(url=discover_url, h_list=hot_list, b_url=base_url, l_front=list_front):
    # 抓包可知是get方式
    result = requests.get(url)
    html_discover = result.content
    soup = BeautifulSoup(html_discover, 'html.parser')
    # 取前8的a标签，即热门推荐八个歌单
    soup_a = soup.find_all('a', class_='msk')[0:h_list]
    # 提取前八歌单的url，取歌单前二的歌曲，剔除电台节目，累计共十首
    # 首先清除redis的music队列
    redis.delete('music')
    for a in soup_a:
        #  完整url
        hot_url_one = b_url+a['href']
        if 'playlist' not in hot_url_one:
            continue
        result_hot_one = requests.get(hot_url_one)
        html_hot_one = result_hot_one.content
        hot_one_soup = BeautifulSoup(html_hot_one, 'html.parser')
        tag_a = hot_one_soup.find_all('div', id='song-list-pre-cache')[0].find_all('textarea')[0].string
        songs_num = 0
        for tag_a_a in json.loads(tag_a):
            # 歌曲信息存入字典，最终以字典形式存入redis
            redis_dic = {}
            tag_a_json = tag_a_a
            # 筛选不能外链播放的歌曲
            if tag_a_json['copyrightId'] != 0:
                continue
            song_name = tag_a_json[u'name']
            redis_dic['song_name'] = song_name
            song_id = tag_a_json[u'id']
            redis_dic['song_id'] = song_id
            # 若歌曲已存在数据库中，则过滤掉
            if session.query(MusicModel).filter_by(song_id=redis_dic['song_id']).first():
                continue
            artist_name = tag_a_json[u'artists'][0][u'name']
            redis_dic['artist_name'] = artist_name
            time = get_time()
            redis_dic['time'] = time
            # 存入redis
            into_redis_music(redis_dic)
            # 存入MySQL
            song = MusicModel(date_time=time, song_name=song_name, artist_name=artist_name, song_id=song_id)
            session.add(song)
            session.commit()
            songs_num += 1
            # 每个歌单选择2首歌
            if songs_num >= l_front:
                break


def get_time():
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    return str(year)+'-'+str(month)+'-'+str(day)


# 将歌曲存入redis
def into_redis_music(dic):
    dic_json = json.dumps(dic)
    redis.lpush('music', dic_json)


# 读取redis中的歌曲列表，返回歌曲列表
def redis_music_return():
    dic = redis.lrange('music', 0, -1)
    dic_after = []
    for d in dic:
        dic_after.append(json.loads(d))
    return dic_after

# 定时更新数据
if __name__ == '__main__':
    time = datetime.now()
    time_str = str(time.year)+'-'+str(time.month)+'-'+str(time.day)
    if not session.query(MusicModel).filter_by(date_time=time_str).first():
        music_spider()


