import pymongo
import pymysql
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        name = item.collection
        self.db[name].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()


class MysqlPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.sql = ''

    @classmethod
    def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
        """
        数据库建立连接
        :param settings: 配置参数
        :return: 实例化参数
        """
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            port=settings["MYSQL_PORT"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )

        # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
        dbpool = adbapi.ConnectionPool('pymysql', **dbparms)
        # 返回实例化参数
        return cls(dbpool)

    def process_item(self, item, spider):
        # 并发太快 没什么作用
        # query = self.dbpool.runQuery("SELECT uid from zz_lease_info where uid=%s", item["uid"])
        # query.addCallback(self.filter_item, item, spider)
        # query.addErrback(self.handle_error, item, spider)  # 处理异常
        # return item

        #直接插入数据库 数据库使用唯一索引来避免重复
        query = self.dbpool.runInteraction(self.do_insert, item)  # 指定操作方法和操作数据
        # 添加异常处理
        query.addCallback(self.handle_error, item, spider)  # 处理异常

    def do_insert(self, cursor, item):

        cursor.execute(self.sql,
                       (item["uid"],
                        item["display_source"],
                        item["display_rent_type"],
                        item["icon"],
                        item["publish_date"],
                        item["pictures"],
                        item["title"],
                        item["text"],
                        item["pic_urls"],
                        item["location"],
                        item["city"],
                        item["longitude"],
                        item["latitude"],
                        item["rent_type"],
                        item["tags"],
                        item["labels"],
                        item["pub_time"],
                        item["online_url"],
                        item["district"],
                        item["price"],
                        item["source"],
                        item["report_num"],
                        item["add_time"]
                        ))

    @property
    def sql(self):
        if not self._sql:
            self._sql = '''
                    insert  into zz_lease_info(uid, display_source, display_rent_type, icon,publish_date, pictures, title, text, pic_urls, location,city,longitude,latitude,rent_type,tags,labels,pub_time,online_url,district,price,source,report_num,add_time)
                       values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
                    '''
            return self._sql
        return self._sql

    # addCallback函数返回，result是查询结果，item是要存入的数据
    # 如果表内已经有数据，则直接返回，不再保存数据。
    def filter_item(self, result, item, spider):
        if result:
            return item
        else:
            query = self.dbpool.runInteraction(self.do_insert, item)
            query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    @sql.setter
    def sql(self, value):
        self._sql = value


class ImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Downloaded Failed')
        return item

    def get_media_requests(self, item, info):
        yield Request(item['url'])
