# -*- coding: utf-8 -*-
import json
import codecs
import pymongo
import logging
from scrapy.conf import settings

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
logger = logging.getLogger()


class KlvCrawlerPipeline(object):
    def __init__(self):
        self.file = codecs.open('KlvCrawlerPipeline.json',
                                'wb', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        # print line
        # print 'in process_item of pipeline=================================='
        self.file.write(line.decode("unicode_escape"))
        return item


class MongoDBPipeline(object):
    def __init__(self):
        mongoClient = pymongo.MongoClient(
	        'mongodb://10.118.100.103,10.118.100.104,10.118.100.105/?replicaSet=rideo&ssl=false&readPreference=primary&connectTimeoutMS=10000&socketTimeoutMS=10000&maxPoolSize=500&waitQueueMultiple=2&waitQueueTimeoutMS=3000&w=1'
        )
        # db = connection[settings['MONGODB_DB']]
        self.mongodb = mongoClient[settings['MONGODB_DB']]
        self.collection = self.mongodb[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        save_data(item)
        return item

    def save_data(item):
        try:
            item["_id"] = item[u'app_detail_url'].lower()
            self.collection.update({'_id': item["_id"]}, {"$set": item}, upsert=True)
        except KeyError as e:
            logger.error(sys._getframe().f_code.co_name + item)

