# -*- coding: utf-8 -*-

# Define your item pipelines here
# Using MongoDB
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import datetime
from towmater.items.car_images import CarImage

class CarImagePipeline(object):

    collection_name = 'car_images'

    def __init__(self, mongo_uri, mongo_db):
            self.mongo_uri = mongo_uri
            self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_SERVER'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'towmater')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item,CarImage):
            return self.handleCars(item,spider)
        else:
            return item # return the item to let other pipeline to handle it

    def handleCars(self,item,spider):
        #handle cars here
        self.collection.remove( { 'car_id' : item['car_id'] } );

        the_images = {} #initialize dict
        for image_url in item['image_url']:
            the_images['car_id'] = item['car_id']
            the_images['image_url'] = image_url
            self.collection.insert(dict(the_images))
    pass