from scrapy.item import Item, Field


class CarInfoItem(Item):
    base_url = Field()
    id = Field()
    url = Field()
    desc = Field()
    price = Field()
    gear = Field()
    year = Field()
    mileage = Field()
