import scrapy


class VkeaSpider(scrapy.Spider):
    name = "vkea_xiaomi"
    allowed_domains = ["xiaomi.com"]
    start_urls = [
        "http://app.xiaomi.com/"
    ]

    def parse(self, response):
        for sel in response.xpath('//ul[re:test(@class, "category-list")]//li'):
            title = sel.xpath('a/text()').extract()
            link = sel.xpath('a/@href').extract()
            url = response.urljoin(link[0])
            print title, link, url
