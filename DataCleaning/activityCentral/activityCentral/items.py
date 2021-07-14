# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ActivitycentralItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    activity_date = scrapy.Field()
    organizer = scrapy.Field()
    description = scrapy.Field()
    location = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    platform = scrapy.Field()
    rating = scrapy.Field()
    tags = scrapy.Field()
    source = scrapy.Field()
    price = scrapy.Field()
    thumbnail = scrapy.Field()
