# -*- coding: utf-8 -*-

import scrapy
import datetime
import pymongo
from scrapy.loader import ItemLoader
from towmater.items.cars import CarItem
from towmater.items.car_details import CarDetail
from towmater.items.car_images import CarImage

class CarsSpider(scrapy.Spider):
    name = 'cars'
    # do not set domains to allow all domain
    #allowed_domains = ['mabes.dev']
    #start_urls = ['http://mabes.dev/scape_target_detail.html']

    def start_requests(self):
        mongo_uri = self.settings.get('MONGODB_SERVER')
        mongo_db = self.settings.get('MONGODB_DB', 'cars')
        collection = 'sites'

        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]
        self.collection = self.db[collection]

        for site in self.collection.find({'is_active':1}):
            url2scrape = site['url_to_scrape']
            # url2scrape = 'http://mabes.dev/scape_target.html'
            if site['spider_element']['listing'] is not None and site['spider_element']['listing'] != '':
                scrape_request = scrapy.Request(url2scrape, callback=self.parse)
                scrape_request.meta['site_id'] = str(site['_id'])
                scrape_request.meta['listing'] = site['spider_element']['listing']  if site['spider_element']['listing'] is not None and site['spider_element']['listing'] != '' else None
                scrape_request.meta['detail'] = site['spider_element']['detail'] if site['spider_element']['detail'] is not None and site['spider_element']['detail'] != '' else None
                scrape_request.meta['photo'] = site['spider_element']['photo'] if site['spider_element']['photo'] is not None and site['spider_element']['photo'] != '' else None
                yield scrape_request
            else:
                print 'Spider element configuration not found'

    def parse(self, response):
        site_id = response.meta['site_id']
        listing = response.meta['listing']
        detail = response.meta['detail']
        photo = response.meta['photo']
        #--- wrapper search result
        cars = response.xpath(listing['wrapper'])
        for car in cars:
            item = CarItem()
            item['site_id'] = site_id
            item['car_id'] = car.xpath(listing['car_id']).extract_first() if listing['car_id'] is not None and listing['car_id'] != '' else ''
            item['name'] = car.xpath(listing['name']).extract_first() if listing['name'] is not None and listing['name'] != '' else ''
            item['price'] = car.xpath(listing['price']).extract_first() if listing['price'] is not None and listing['price'] != '' else ''
            item['state'] = car.xpath(listing['state']).extract_first() if listing['state'] is not None and listing['state'] != '' else ''
            item['listing_feature'] = car.xpath(listing['listing_feature']).extract() if listing['listing_feature'] is not None and listing['listing_feature'] != '' else ''
            item['date_collected_to'] = datetime.datetime.utcnow()
            yield item
            if detail['detail_url'] is not None and detail['detail_url'] != '':
                detail_page = car.xpath(detail['detail_url']).extract_first()
                if detail_page is not None:
                    detail_page = response.urljoin(detail_page)
                    detail_request = scrapy.Request(detail_page, callback=self.parse_detail)
                    detail_request.meta['car_id'] = item['car_id']
                    detail_request.meta['detail'] = detail
                    detail_request.meta['photo'] = photo
                    yield detail_request

        next_page = response.xpath(listing['next_page']).extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse,meta={'site_id':site_id,'listing':listing,'detail':detail,'photo':photo})

    pass

    # on detail loop inside spider element
    # if key matches with CarDetail() item then process it
    def parse_detail(self, response):
        detail = response.meta['detail']
        car_details = response.xpath(detail['wrapper'])
        item = CarDetail()
        item['car_id'] = response.meta['car_id']
        for k in detail:
            if k in item.fields:
                if k == 'comments':
                        item[k] = response.xpath(detail[k]).extract()
                else:
                        item[k] = response.xpath(detail[k]).extract_first()
            else:
                if k != 'wrapper' and k != 'detail_url':
                    print 'the key: {} is not on CarDetail items'.format(k)
        yield item

        photo = response.meta['photo']
        if photo is not None and photo['wrapper'] is not None and photo['wrapper'] != '':
            images = response.xpath(photo['wrapper'])
            if images is not None:
                car_images = CarImage()
                car_images['car_id'] = response.meta['car_id']
                car_images['image_url'] = images
                yield car_images

    pass
