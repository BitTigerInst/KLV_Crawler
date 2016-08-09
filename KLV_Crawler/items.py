# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class KlvCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()

class ProxyItem(scrapy.Item):
     address   = scrapy.Field()
     port      = scrapy.Field()
     protocol  = scrapy.Field()
     location  = scrapy.Field()
 
     type      = scrapy.Field() # 0: anonymity #1 nonanonymity
     delay     = scrapy.Field() # in second
     timestamp = scrapy.Field()
