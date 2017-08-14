# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class CarDetail(Item):
    # define the fields for your item here like:
    car_id = Field()
    kilometers = Field()
    colour = Field()
    drive = Field()
    body_style = Field()
    doors = Field()
    seat_capacity = Field() # first time we scrape it
    # engine_size = Field() # last scraped time
    # engine_type = Field() # last scraped time
    # reg_plate = Field()
    # compliance_date = Field()
    # towing_capacitybraked = Field()
    # towing_capacityunbraked = Field()
    # cylinders = Field()
    # power = Field()
    # generic_gear_type = Field()
    # gears = Field()
    # fuel_type = Field()
    # fuel_consumption_combined = Field()
    # ancap_rating = Field()
    # p_plate_status = Field()