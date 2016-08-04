# -*- coding: utf-8 -*-
import scrapy
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class VkeaSpider(scrapy.Spider):
    name = "vkea_xiaomi"
    download_delay = 1
    allowed_domains = ["xiaomi.com"]
    start_urls = [
        "http://app.xiaomi.com/"
    ]

    def parse(self, response):
        for sel in response.xpath('//ul[re:test(@class, "category-list")]//li'):
            # title = sel.xpath('a/text()').extract()
            link = sel.xpath('a/@href').extract()
            url = response.urljoin(link[0])
            # print title, link, url
            yield scrapy.Request(url, callback=self.parse_category_contents)

    def parse_category_contents(self, response):
        for sel in response.xpath('//ul[re:test(@id, "all-applist")]//li'):
            link = sel.xpath('a/@href').extract()
            url = response.urljoin(link[0])
            # print url
            yield scrapy.Request(url, callback=self.parse_app_contens)

    def parse_app_contens(self, response):
        # print 'in parse_app_contens ---------------------'
        item = dict()
        texts = ""
        for sel in response.xpath('//p[re:test(@class,"pslide")]/text()'):
            # item = containItem()
            # item = dict()
            texts += sel.extract().encode('utf-8')
        name_path = '//div[re:test(@class,"intro-titles")]/h3/text()'
        for sel in response.xpath(name_path):
            item['name'] = sel.extract().encode('utf-8')
        item['details'] = texts
        yield item
