# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class ZufangspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HouseItem(scrapy.Item):
    # collection = table = 'house_info'
    # title = Field()
    # house_url = Field()
    # location = Field()
    # source = Field()

    collection = table = 'zz_lease_info'
    uid = Field()
    display_source = Field()
    display_rent_type = Field()
    icon = Field()
    publish_date = Field()
    pictures = Field()
    title = Field()
    text = Field()
    pic_urls = Field()
    location = Field()
    city = Field()
    longitude = Field()
    latitude = Field()
    rent_type = Field()
    tags = Field()
    labels = Field()
    pub_time = Field()
    online_url = Field()
    district = Field()
    price = Field()
    source = Field()
    report_num = Field()
    add_time = Field()
