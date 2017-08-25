# -*- coding: utf-8 -*-

# Define your item pipelines here
# Using MongoDB
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import datetime
from towmater.items.cars import CarItem
from pprint import pprint

class CarPipeline(object):

    collection_name = 'cars'
    collected_cars = {}
    item_car = []
    tmp_site_id = None

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
        self.compareScrapedCars('',self.collected_cars)
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item,CarItem):
            return self.handleCars(item,spider)
        else:
            return item # return the item to let other pipeline to handle it

    def handleCars(self,item,spider):
        # handle cars here
        # check for existence
        if self.doWeHaveIt(item['car_id']):
            self.updateAndCreateHistory(item)
        else:
            # insert new document
            item['date_collected_from'] = item['date_collected_to']
            item['date_collected_to'] = item['date_collected_to']
            item['last_changed_date'] = None
            item['status'] = 'open'
            self.collection.insert(dict(item))

        # create a list of dictionary of cars that exist on the site
        if self.tmp_site_id is None:
            self.item_car.append(item['car_id'])
            self.collected_cars[item['site_id']] = self.item_car
        elif self.tmp_site_id != item['site_id']:
            # if site changes, run the comparison method
            # then remove the collected cars from dictionary
            # the other item inside dict will be process when the spider closed
            self.compareScrapedCars(self.tmp_site_id,self.item_car)
            del self.collected_cars[self.tmp_site_id]

            self.item_car = []
            self.item_car.append(item['car_id'])
            self.collected_cars[item['site_id']] = self.item_car
        else:
            self.item_car.append(item['car_id'])
            self.collected_cars[item['site_id']] = self.item_car

        self.tmp_site_id = item['site_id']

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

    # compare the result
    def compareScrapedCars(self,site_id,collected_cars):
        if site_id != '' and type(collected_cars) is not dict:
            all_cars = self.collection.find( {'site_id':site_id}, {'_id':0, 'car_id':1} )
            if all_cars is not None:
                list_cars = []
                for cars in all_cars:
                    list_cars.append(cars['car_id'])

                closed_car = set(list_cars).difference(collected_cars)

                try:
                   last_changed_date = datetime.datetime.utcnow()
                   closed_car = [s.encode('ascii') for s in closed_car]
                   self.collection.update_many(
                      { 'site_id': site_id, 'car_id': { '$in': closed_car } },
                      { '$set': { 'status' : 'closed', 'last_changed_date': last_changed_date } }
                   );
                except Exception as inst:
                   pprint(inst)

        else:
            # cars is a dict
            for site_id in collected_cars:
                all_cars = self.collection.find( {'site_id': site_id}, {'_id':0, 'car_id':1} )
                if all_cars is not None:
                    list_cars = []
                    for cars in all_cars:
                        list_cars.append(cars['car_id'])

                    closed_car = set(list_cars).difference(collected_cars[site_id])

                    try:
                       last_changed_date = datetime.datetime.utcnow()
                       closed_car = [s.encode('ascii') for s in closed_car]
                       self.collection.update_many(
                          { 'site_id': site_id, 'car_id': { '$in': closed_car } },
                          { '$set': { 'status' : 'closed', 'last_changed_date': last_changed_date } }
                       );
                    except Exception as inst:
                       pprint(inst)

    pass