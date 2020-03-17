import scrapy
import re
import os.path
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
# from scrapy.selector import HtmlXPathSelector Select代替HtmlXPathSelector
from scrapy.selector import Selector
from craigslist_sample.items import ALJItem
# from scrapy.utils.response import body_or_str

class MySpider(CrawlSpider):
    name = "alj"
    allowed_domains = ["aljazeera.com"]
    start_urls = ['http://www.aljazeera.com/']
    '''
    Sitemap: https://www.aljazeera.com/sitemap.xml
    '''
    base_url = 'https://www.aljazeera.com/xml/sslsitemaps/sitemap2013_1.xml'
    year = ['2017_1','2018_1','2019_1']

    def parse(self,response):
        for y in self.year:
            url = self.base_url+y+'.xml'
            yield scrapy.Request(url,self.parseList)

    def parseList(self,response):
        nodename = 'loc'
        text = response.text#代替body_or_str,在新版本函数已经废弃
        r = re.compile(r"(<%s[\s>])(.*?)(</%s>)" % (nodename, nodename), re.DOTALL)
        for match in r.finditer(text):
            url = match.group(2)
            yield scrapy.Request(url,self.parse_items)

    def parse_items(self, response):
        hxs = Selector(response)
        items = []
        item = ALJItem()
        #//*[@id="body-200771816342556199"]/p//text()
        item["title"] = hxs.xpath('//h1[@class="post-title"]/text()').extract()[0]
        # article = hxs.xpath('string(//div[contains(@class,"article-body") or contains(@class ,"article-body-full")])').extract()
        article = hxs.xpath(
            '//*[@id="body-200771816342556199"]/p//text()').extract()

        item["article"] = "\n".join(article).encode('utf8')
        item['link'] = response.url
        #//time[@class='timeagofunction']/text()的最后一个
        # item['date'] = hxs.xpath('//time/text()').extract()[0].encode('utf-8')
        item['date'] = hxs.xpath('//time/text()').extract()[0].encode('utf-8')
        items.append(item)

        return(items)