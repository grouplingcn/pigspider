# -*- coding: utf-8 -*-
import datetime
import json
import math
import re
from copy import deepcopy

import scrapy
from pydispatch import dispatcher
from scrapy import Selector, signals, Request
from zufangspider.items import HouseItem

class LianjiaSpider(scrapy.Spider):
    name = 'lianjia'
    allowed_domains = ['lianjia.com']
    root_url = 'https://gy.lianjia.com'
    start_url = root_url + '/zufang/pg{page}rco11/#contentList'

    def __init__(self, city='sz'):  # 初始化
    #     self.browser = webdriver.Chrome()  # 创建谷歌浏览器对象
    #     super(LianjiaSpider, self).__init__()  # 设置可以获取上一级父类基类的，__init__方法里的对象封装值
        super(LianjiaSpider, self).__init__()
        self.root_url = 'https://%s.lianjia.com' % city
        self.start_url = self.root_url + '/zufang/pg{page}rco11/#contentList'
        # dispatcher.connect()信号分发器，第一个参数信号触发函数，
        # 第二个参数是触发信号，signals.spider_closed是爬虫结束信号
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    #
    #     # 运行到此处时，就会去中间件执行，RequestsChrometmiddware中间件了
    #
    def spider_closed(self, spider):  # 信号触发函数
        print('爬虫结束 停止爬虫')
    #     self.browser.quit()

    def start_requests(self):
        for i in range(1, 2):
            url = self.start_url.format(page=i)
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        result_lis = response.xpath(
            "//div[@id='content']/div[@class='content__article']/div[@class='content__list']/div[@class='content__list--item']")
        # print(result_lis)
        for li in result_lis:
            item = HouseItem()
            online_url = li.xpath(
                "./div[@class='content__list--item--main']/p[@class='content__list--item--title']/a[@class='twoline']/@href").get().strip()
            title = li.xpath(
                "./div[@class='content__list--item--main']/p[@class='content__list--item--title']/a[@class='twoline']/text()").get().strip()
            item['uid'] = online_url.split('/')[-1].split('.')[0]
            item['display_source'] = '链家租房'
            item['display_rent_type'] = title.split('·')[0]
            item['icon'] = 'LightGreen.png'
            item['title'] = title
            item['text'] = title
            item['rent_type'] = '1'
            item['labels'] = '1'
            item['pub_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['online_url'] = self.root_url + online_url
            item['district'] = '1'
            item['source'] = 'lianjia'
            item['report_num'] = '1'
            item['add_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            yield scrapy.Request(url=self.root_url + online_url, meta={"item": deepcopy(item)},
                                 callback=self.parseDetail, dont_filter=True)

    def parseDetail(self, response):
        item = response.meta['item']
        item['publish_date'] = response.xpath("//div[@class='content__subtitle']/text()").get().strip().split('：')[
                                   -1] + ' 00:00:00'
        item['city'] = response.xpath("//meta[@name='location']/@content").get().strip().split('=')[-1]
        location_info = response.xpath('//script[contains(., "g_conf.coord")]/text()')
        pattern1 = re.compile(r"longitude: '([0-9]*\.[0-9]+)',", re.MULTILINE | re.DOTALL)
        pattern2 = re.compile(r"latitude: '([0-9]*\.[0-9]+)'", re.MULTILINE | re.DOTALL)
        longitude = location_info.re(pattern1)[0]
        latitude = location_info.re(pattern2)[0]
        bd_longitude = round(float(longitude), 6)
        bd_latitude = round(float(latitude), 6)
        gd_coordinate = self.bd09_to_gcj02(bd_longitude, bd_latitude)
        item['longitude'] = round(float(gd_coordinate[0]), 6)
        item['latitude'] = round(float(gd_coordinate[1]), 6)
        # item['rent_type'] = response.xpath("//div[@class='content__core']/div[@id='aside']/ul[@class='content__aside__list']/li[1]/text()").get().strip()
        pictures = response.xpath("//div[@class='content__article__slide__item']/img/@data-src").extract()
        item['pictures'] = json.dumps(pictures, ensure_ascii=False)
        item['pic_urls'] = item['pictures']
        item['location'] = response.xpath("//p[@class='content__title']/text()").get().strip()
        item['tags'] = response.xpath("//p[@class='content__aside--tags']/i/text()").get().strip()
        item['price'] = response.xpath(
            "//div[@id='aside']/div[@class='content__aside--title']/span/text()").get().strip()
        yield item

    def bd09_to_gcj02(self, bd_lon, bd_lat):
        """
        百度坐标系(BD-09)转火星坐标系(GCJ-02)
        百度——>谷歌、高德
        :param bd_lat:百度坐标纬度
        :param bd_lon:百度坐标经度
        :return:转换后的坐标列表形式
        """
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return [gg_lng, gg_lat]
