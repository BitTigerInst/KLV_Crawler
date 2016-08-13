# -*- coding: utf-8 -*-
import scrapy
import sys
import logging
import json
import base64
import random
import pymongo
from scrapy.conf import settings
import re
reload(sys)
sys.setdefaultencoding("utf-8")

logger = logging.getLogger()

class VkeaSpider(scrapy.Spider):

    name = "vkea_xiaomi"
    # 已经在setting中设置了download_delay，所以时间间隔会是rando(0.5~1.5*设定值)
    # download_delay = 3
    allowed_domains = ["xiaomi.com"]
    start_urls = [
        # "http://app.xiaomi.com/"
        # "http://app.xiaomi.com/category/16"
    ]
     for i in indexes:
        url = 'http://app.xiaomi.com/categotyAllListApi?page=0&categoryId=%d&pageSize=1000' % i
        start_urls.append(url) 
    user_agents =[
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125",
    ]
    xiaomi_headers = {
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'Accept-Language': "en-US,en;q=0.5",
        "Connection": "keep-alive",
        # "Host": "developer.xiaomi.com",dev
        # "Refer": "http://app.xiaomi.com",
        'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 "
        }

    mongoClient = pymongo.MongoClient(
        'mongodb://10.118.100.103,10.118.100.104,10.118.100.105/?replicaSet=rideo&ssl=false&readPreference=primary&connectTimeoutMS=10000&socketTimeoutMS=10000&maxPoolSize=500&waitQueueMultiple=2&waitQueueTimeoutMS=3000&w=1'
    )
    # db = connection[settings['MONGODB_DB']]
    mongodb = mongoClient[settings['MONGODB_DB']]
    collection = mongodb[settings['MONGODB_COLLECTION']]

    category_page_url_template = "http://app.xiaomi.com/categotyAllListApi?page=%d&categoryId=%d&pageSize=%d"
    app_detail_url_templae = "http://app.xiaomi.com/details?id=%s"
    category_page_size = 300
    
    def process_request(self, request, spider):
        fd = open('./proxy_list.txt','r')
        data = fd.readlines()
        fd.close()
        length = len(data)
        index = random.randint(0, length -1)
        item = data[index]
        request.meta['proxy'] = 'http://' + item
        self.xiaomi_headers['user-agent'] = user-agent[random.randint(0, len(user_agents) -1)]
        request.headers = self.xiaomi_headers
        logger.debug('proxy:' + self.request.meta['proxy'] )
   
    # def parse(self, response):
    #     for sel in response.xpath('//ul[re:test(@class, "category-list")]//li'):
    #         # title = sel.xpath('a/text()').extract()
    #         link = sel.xpath('a/@href').extract()
    #         url = response.urljoin(link[0])
    #         # print title, link, url
    #         yield scrapy.Request(url, callback=self.parse_category_contents, headers=self.xiaomi_headers)

    def parse_category_contents(self, response):
        # item_count = 0
        logger.debug("in parse_category_contents")
        logger.debug( response.url)
        categoryId = int(response.url.split('/')[-1])
        # for sel in response.xpath('//ul[re:test(@id, "all-applist")]//li'):
        #     link = sel.xpath('a/@href').extract()
        #     url = response.urljoin(link[0])
        #     item_count += 1
        # if item_count >= self.category_page_size:
        url = self.category_page_url_template%(0,categoryId,self.category_page_size)
        yield scrapy.Request(url, callback=self.parse_category_contents_json)


    # def parse_category_contents_json(self, response):

    def parse(self, response):
        # logger.debug("in parse_category_contents_json")
        logger.debug( response.url)
        unicode_body = response.body_as_unicode()
        json_obj = json.loads(unicode_body, 'utf-8')
        items = dict()
        data_list = list()
        data_list = json_obj["data"]
        data_size = len(data_list)
        for item in data_list:
            if self.search_app_id(item["packageName"]) == 0:
                yield scrapy.Request(self.app_detail_url_templae%(item["packageName"]), callback=self.parse_app_contens)

        pageId = int ((response.url.split('page=')[-1].split('&categoryId')[0]))+1
        page_param = 'page=' + str(pageId)+'&'
        url = re.sub('(page=[0-9]*?&)',page_param,response.url)
        if data_size >= self.category_page_size:
            yield scrapy.Request(url, callback=self.parse_category_contents_json)

    def parse_app_contens(self, response):
        # logger.debug("in parse_app_contens")
        # logger.debug( response.url)
        item = dict()
        category_name_path = '//div[re:test(@class,"bread-crumb")]/ul/li/a/text()'
        for sel in response.xpath(category_name_path):
            item["category_name"] = sel.extract().encode('utf-8')
        categoryId_path = '//div[re:test(@class,"bread-crumb")]/ul/li/a/@href'
        for sel in response.xpath(categoryId_path):
            item["category_id"] = sel.extract().encode('utf-8').replace("/category/","")
        item["app_id"] = response.url.replace("http://app.xiaomi.com/details?id=","")
        texts = ""
        for sel in response.xpath('//p[re:test(@class,"pslide")]/text()'):
            texts += sel.extract().encode('utf-8')
        name_path = '//div[re:test(@class,"intro-titles")]/h3/text()'
        for sel in response.xpath(name_path):
            item['app_name'] = sel.extract().encode('utf-8')
        imgs_path = '//div[re:test(@id,"J_thumbnail_wrap")]/img[position()>0]'
        img_array = list()
        for sel in response.xpath(imgs_path).extract():
            img_array.append(sel.split("\"")[1])
        item['app_details'] = texts
        item['app_imgages'] = img_array
        item['app_detail_url'] = response.url
        yield item

    def search_app_id(self, app_id):
        result = self.collection.find({'_id':app_id.lower()})
        for item in result:
            return 1
        return 0




