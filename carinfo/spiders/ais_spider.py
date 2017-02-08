from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re


from carinfo.items import CarInfoItem


class AisSpider(CrawlSpider):
    name = "carinfo_ais"
    allowed_domains = ["ais-market.com.ua"]
    start_urls = [
        "http://ais-market.com.ua/?filter=true&transmission=1436",
        "http://ais-market.com.ua/?filter=true&transmission=36",
    ]

    def parse_start_url(self, response):
        items = []
        for row in response.xpath('//ol[@id="products-list"]/li'):
            car_info = CarInfoItem()
            car_info['base_url'] = "http://ais-market.com.ua"
            car_info['id'] = row.xpath('.//p[@id="skuproduct"]/text()').extract_first().split(' ')[-1]
            car_info['url'] = row.xpath('.//h2[@class="product-name"]/a/@href').extract_first()
            car_info['desc'] = row.xpath('.//h2[@class="product-name"]/a/@title').extract_first()
            car_info['year'] = row.select('.//h2[@class="product-name"]/a/text()').extract_first().split()[-1]
            car_info['price'] = row.xpath('.//span[@class="price"]/text()').extract_first().strip()
            car_info['gear'] = "auto" if response.url.endswith('1436') else "manual"
            car_info['mileage'] = row.xpath('.//p[@class="prod_list_summary"]/text()').extract_first().strip().split('\n')[2].strip().split(':')[-1][:-1]
            items.append(car_info)
        return items
