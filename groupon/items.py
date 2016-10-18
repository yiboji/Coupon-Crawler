# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GrouponItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    merchant_id = scrapy.Field()
    merchant_type = scrapy.Field()
    merchant_location = scrapy.Field()
    merchant_coord = scrapy.Field()
    merchant_name = scrapy.Field()
    merchant_tel = scrapy.Field()
    coupon_source = scrapy.Field()
    coupon_log_url = scrapy.Field()
    coupon_titles = scrapy.Field()
    coupon_url = scrapy.Field()
    image_url = scrapy.Field()
    radius = scrapy.Field()
    expire_date = scrapy.Field()
    pass
