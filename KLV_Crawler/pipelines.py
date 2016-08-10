# -*- coding: utf-8 -*-
import json
import codecs
import pymongo

from scrapy.conf import settings

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


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
        connection = pymongo.MongoClient(
	        'mongodb://10.118.100.103,10.118.100.104,10.118.100.105/?replicaSet=rideo&ssl=false&readPreference=primary&connectTimeoutMS=10000&socketTimeoutMS=10000&maxPoolSize=500&waitQueueMultiple=2&waitQueueTimeoutMS=3000&w=1')
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.insert(dict(item))
            log.msg("Question added to MongoDB database!",
                    level=log.DEBUG, spider=spider)
        return item
