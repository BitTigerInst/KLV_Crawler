# -*- coding: utf-8 -*-
import scrapy
import logging
import re
from KLV_Crawler.items import ProxyItem
import urllib2, socket
import thread  


socket.setdefaulttimeout(180)

logger = logging.getLogger()

class CnproxySpider(scrapy.Spider):
    count = 0
    name = "cnproxy"
    allowed_domains = ["cnproxy.com"]
    indexes    = [1,2,3,4,5,6,7,8,9,10]
    start_urls = []
    for i in indexes:
        url = 'http://www.cnproxy.com/proxy%s.html' % i
        start_urls.append(url)
    start_urls.append('http://www.cnproxy.com/proxyedu1.html')
    start_urls.append('http://www.cnproxy.com/proxyedu2.html')

    def parse(self, response):
        # ref: http://www.cnblogs.com/qq78292959/p/3372704.html
        script_div = '//head/script[position()=1]/text()'
        script_re = re.compile('data=(.*)>')
        variables = response.xpath(script_div).extract()[0][1:]
        # logger.debug(variables)
        list_pair = variables.split(";")
        dict_variable = dict()

        for pair in list_pair:
            temp = pair.split("=")            
            if len(temp) == 2:
                dict_variable[temp[0]] = temp[1].replace('"','')

        # logger.debug(script_re.findall(response.xpath(script_div).extract()[0]))
        list_div = '//div[re:test(@id, "proxylisttb")]//tr[position()>1]'
        address_td = '//td[position()=1]/text()'
        protocl_td = '//td[position()=2]/text()'
        location_td = '//td[position()=4]/text()'
        port_td = '//td/script/text()'
        # sel = response.xpath()
        addresses = response.xpath(list_div + address_td).re('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        protocols = response.xpath(list_div + protocl_td).extract()
        locations = response.xpath(list_div + location_td).extract()
        ports_re  = re.compile('write\(":"(.*)\)')
        # raw_ports = ports_re.findall()
        raw_ports = list()
        for sel in response.xpath(list_div + port_td).extract():
            raw_ports.append(''.join(ports_re.findall(sel)))
        ports = []
        for port in raw_ports:
            tmp = port.replace('+','')
            for key  in dict_variable:

                tmp = tmp.replace(key, dict_variable[key])
            ports.append(tmp)

        # logger.debug(variables)
        # logger.debug(protocols[0] +'://'+addresses[0] +':'+ ports[0])
        items = []
        proxyList = list()
        for i in range(len(addresses)):
            item = ProxyItem()
            item['address']  = addresses[i]
            item['protocol'] = protocols[i]
            item['location'] = locations[i]
            item['port']     = ports[i]
            # items.append(item)
            # logger.debug(protocols[i] +'://'+addresses[i] +':'+ ports[i] +'@' + locations[i])
            proxyList.append(addresses[i] +':'+ ports[i])

        fp   = open('./proxies.txt','a')
        for item in proxyList:
            # logger.debug(item)
            if thread.start_new_thread(self.is_bad_proxy, (item,)):
                line = item+'\n'
                fp.write(line)
                self.count += 1
                # logger.debug( "Bad Proxy: "+ item)
            else:
                logger.debug( item+ " is working")
                self.count += 1
        if self.count >=len(proxyList):
            fp.close()
            

    def is_bad_proxy(self, pip):    
        try:        
            proxy_handler = urllib2.ProxyHandler({'http': pip})        
            opener = urllib2.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib2.install_opener(opener)        
            req=urllib2.Request('http://www.your-domain.com')  # change the url address here
            sock=urllib2.urlopen(req)
        except urllib2.HTTPError, e:        
            # print 'Error code: ', e.code
            return e.code
        except Exception, detail:
            # print "ERROR:", detail
            return 1
        # logger.debug( pip+ " is working")

        return 0




