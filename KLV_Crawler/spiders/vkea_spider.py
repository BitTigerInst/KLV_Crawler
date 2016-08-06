# -*- coding: utf-8 -*-
import scrapy
import sys
import logging
import json
import base64
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
from scrapy_splash import SlotPolicy
import re
reload(sys)
sys.setdefaultencoding("utf-8")

logger = logging.getLogger()

script = """
    function main(splash)
      # splash:init_cookies(splash.args.cookies)
      # assert(splash:go{
      #   splash.args.url,
      #   headers=splash.args.headers,
      #   http_method=splash.args.http_method,
      #   body=splash.args.body,
      #   })
      # assert(splash:wait(0.5))

      # local entries = splash:history()
      # local last_response = entries[#entries].response
      splash:go("http://www.xiaomi.com")
      splash:wait(0.5)
      locat title = splash:evaljs("document.title")
      return {
        # url = splash:url(),
        # headers = last_response.headers,
        # http_status = last_response.status,
        # cookies = splash:get_cookies(),
        # html = splash:html(),
        title = title
      }
    end
"""

class VkeaSpider(scrapy.Spider):

    name = "vkea_xiaomi"
    download_delay = 5
    allowed_domains = ["xiaomi.com"]
    start_urls = [
        "http://app.xiaomi.com/"
        # "http://app.xiaomi.com/category/16"
    ]
    category_page_url_template = "http://app.xiaomi.com/categotyAllListApi?page=%d&categoryId=%d&pageSize=%d"
    app_detail_url_templae = "http://app.xiaomi.com/details?id=%s"
    category_page_size = 300
    
   
    def parse(self, response):
        for sel in response.xpath('//ul[re:test(@class, "category-list")]//li'):
            # title = sel.xpath('a/text()').extract()
            link = sel.xpath('a/@href').extract()
            url = response.urljoin(link[0])
            # print title, link, url
            yield scrapy.Request(url, callback=self.parse_category_contents)

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


    def parse_category_contents_json(self, response):
        logger.debug("in parse_category_contents_json")
        logger.debug( response.url)
        unicode_body = response.body_as_unicode()
        json_obj = json.loads(unicode_body, 'utf-8')
        items = dict()
        data_list = list()
        data_list = json_obj["data"]
        data_size = len(data_list)
        for item in data_list:
            yield scrapy.Request(self.app_detail_url_templae%(item["packageName"]), callback=self.parse_app_contens)

        pageId = int ((response.url.split('page=')[-1].split('&categoryId')[0]))+1
        page_param = 'page=' + str(pageId)+'&'
        url = re.sub('(page=[0-9]*?&)',page_param,response.url)
        if data_size >= self.category_page_size:
            yield scrapy.Request(url, callback=self.parse_category_contents_json)

    # def parse_category_contents(self, response):
    #     for sel in response.xpath('//ul[re:test(@id, "all-applist")]//li'):
    #         link = sel.xpath('a/@href').extract()
    #         url = response.urljoin(link[0])
    #         yield scrapy.Request(url, callback=self.parse_app_contens)
    #     pages = "//div[re:test(@class, 'main-con')]"
    #     cur_page = "/span[re:test(@class, 'current')]"
    #     next_page = "/a[re:test(@class, 'next')]"
    #     print pages + cur_page
    #     cur_page_num = response.xpath(pages).extract()
    #     print cur_page_num
        # next_page_num = int(cur_page_num[0]) + 1

        # next_page_but = response.xpath(pages + next_page)
        # if next_page_but is not None:
            #  url = response.urljoin(next_page_num)
            # print url

    def parse_app_contens(self, response):
        logger.debug("in parse_app_contens")
        logger.debug( response.url)
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
        item['app_details'] = texts
        item['app_detail_url'] = response.url
        yield item


class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["xiaomi.com"]
    start_urls = ['http://app.xiaomi.com/category/26']

    # http_user = 'splash-user'
    # http_pass = 'splash-password'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse_result, meta={
            'splash': {
                'args': {
                    'lua_source': script,
                    'endpoint':execute
                }
            }
        })

    def parse_result(self, response):
        data = json.loads(response.body_as_unicode())
        # body = data['html']
        # png_bytes = base64.b64decode(data['png'])
        # print response.body_as_unicode()
        # print response

    def parse(self, response):
        le = LinkExtractor()
        for link in le.extract_links(response):
            yield SplashRequest(
                link.url,
                self.parse_link,
                endpoint='render.json',
                args={
                    'har': 1,
                    'html': 1,
                }
            )

    def parse_link(self, response):
        # print("PARSED", response.real_url, response.url)
        print(response.css("title").extract())
        # print(response.data["har"]["log"]["pages"])
        print(response.headers.get('Content-Type'))
