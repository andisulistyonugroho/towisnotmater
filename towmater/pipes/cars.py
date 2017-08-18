# -*- coding: utf-8 -*-

# Define your item pipelines here
# Using MongoDB
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import datetime
from towmater.items.cars import CarItem

class CarPipeline(object):

    collection_name = 'cars'

    def __init__(self, mongo_uri, mongo_db):
            self.mongo_uri = mongo_uri
            self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_SERVER'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'cars')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item,CarItem):
            return self.handleCars(item,spider)
        else:
            return item # return the item to let other pipeline to handle it

    def handleCars(self,item,spider):
        #handle cars here
        if self.doWeHaveIt(item['car_id']):
            self.updateAndCreateHistory(item)
            return item
        else:
            # insert new document
            item['date_collected_from'] = item['date_collected_to']
            item['date_collected_to'] = item['date_collected_to']
            item['last_changed_date'] = None
            item['status'] = 'open'
            self.collection.insert(dict(item))
            return item
    pass

    def doWeHaveIt(self,car_id):
        find_any = self.collection.find({
            'car_id': car_id
        }).count()

        if find_any == 0:
            return False
        else:
            return True
    pass

    # that car info from scraped website has changed
    # save the old info and update with new data
    # reattach last_update
    def updateAndCreateHistory(self,item):
        # check for changes, save to history and update
        date_collected_to = item['date_collected_to']
        item.pop('date_collected_to')

        find_identical_record = self.collection.find_one(item)

        if find_identical_record is None:
            # get document with the car id
            old_data = self.collection.find_one(
                {'car_id': item['car_id']},
                {'_id':0}
            )

            if old_data is not None:
                old_data['history_created_at'] = datetime.datetime.utcnow()
                self.db['car_change_history'].insert(dict(old_data))
                # update the document
                item['last_changed_date'] = datetime.datetime.utcnow()
                item['date_collected_from'] = old_data['date_collected_from']
                item['date_collected_to'] = date_collected_to
                item['status'] = 'open'
                self.collection.replace_one(
                    {'car_id': item['car_id']},
                    dict(item)
                )
        else:
            self.collection.update_one(
                {'car_id': item['car_id']},
                {'$set': {'date_collected_to': date_collected_to,'status': 'open'}}
            )
    pass