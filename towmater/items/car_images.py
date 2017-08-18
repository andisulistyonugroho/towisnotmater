# -*- coding: utf-8 -*-

# Define here the models for your scraped items
# car images
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class CarImage(Item):
    # define the fields for your item here like:
    car_id = Field()
    image_url = Field()