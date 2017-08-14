# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class CarItem(Item):
    # define the fields for your item here like:
    car_id = Field()
    name = Field()
    price = Field()
    state = Field()
    listing_feature = Field()
    date_collected_from = Field() # first time we scrape it
    date_collected_to = Field() # last scraped time
    last_changed_date = Field() # last scraped time