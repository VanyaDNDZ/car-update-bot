from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re


from carinfo.items import CarInfoItem


class PlanetaSpider(CrawlSpider):
    name = "carinfo_planeta"
    allowed_domains = ["planetavto.com.ua"]
    start_urls = [
        "https://planetavto.com.ua/?page=1",
    ]
    rules = [
        Rule(LinkExtractor(allow=re.compile("page=(\d+)"), deny="dealer"), callback='parse_items', follow=True),
    ]

    def parse_items(self, response):
        items = []
        for row in response.xpath('//*[@id="listObj"]/tr/td/div/table'):
            car_info = CarInfoItem()
            car_info['base_url'] = "https://planetavto.com.ua"
            car_info['id'] = row.xpath('.//a[contains(@href, "car") and @class="img"]/@href').extract_first().split('/')[-1]
            car_info['url'] = row.xpath('.//a[contains(@href, "car") and @class="img"]/@href').extract_first()
            car_info['desc'] = row.xpath('.//strong/a/text()').extract_first()
            car_info['year'] = row.xpath('.//strong/text()').extract()[1].strip()[-4:]
            car_info['price'] = row.xpath('.//strong/text()').extract()[2].strip()
            car_info['gear'] = row.xpath('./tr[2]/td[1]/text()')[2].extract().strip()
            car_info['mileage'] = row.xpath('./tr[2]/td[2]/text()')[0].extract().strip()
            items.append(car_info)
        return items
