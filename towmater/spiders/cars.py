# -*- coding: utf-8 -*-

import scrapy
import datetime
from scrapy.loader import ItemLoader
from towmater.items.cars import CarItem
from towmater.items.car_details import CarDetail

class CarsSpider(scrapy.Spider):
    name = 'cars'
    # allowed_domains = ['mabes.dev']
    # start_urls = ['http://mabes.dev/scape_target_detail.html']
    allowed_domains = ['carsalesnetwork.com.au']
    start_urls = ['http://csndealers.carsalesnetwork.com.au/listing?dealerId=AGC-SELLER-28894%2BAGC-SELLER-14679%2BAGC-SELLER-51021']

    def parse(self, response):
        #--- wrapper search result
        cars = response.xpath('//div[@class="search-results"]/div[@class="result-item"]')
        for car in cars:
            item = CarItem()
            item['car_id'] = car.xpath('.//div[@class="view-more"]/a/@href').extract_first()
            item['name'] = car.xpath('.//h4[@class="result-item-title"]/a/text()').extract_first()
            item['price'] = car.xpath('.//div[@class="price"]/b/text()').extract_first()
            item['state'] = car.xpath('.//div[@class="state"]/text()').extract_first()
            item['listing_feature'] = car.xpath('.//ul[@class="listing-features"]/li/text()').extract()
            item['date_collected_to'] = datetime.datetime.utcnow()
            yield item
            detail_page = car.xpath('.//div[@class="view-more"]/a/@href').extract_first()
            if detail_page is not None:
                detail_page = response.urljoin(detail_page)
                detail_request = scrapy.Request(detail_page, callback=self.parse_detail)
                detail_request.meta['car_id'] = item['car_id']
                yield detail_request

        next_page = response.xpath('//ul[@class="pagination pull-right"]/li[@class="active"]/following-sibling::li/a/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    pass

    def parse_detail(self, response):
        car_details = response.xpath('//*[*[*[. = "Vehicle Details"]]]/table/tr')
        item = CarDetail()
        for car_detail in car_details:
            the_key = car_detail.xpath('.//th/text()').extract_first()
            the_value = car_detail.xpath('.//td').extract_first()
            item['car_id'] = response.meta['car_id']
            the_key = the_key.lower().replace(' ','_')
            if the_key in item.fields:
                item[the_key] = the_value
            # else:
                #print "KEY({}) : VALUE({}) not supported on CarDetail()".format(the_key,the_value)

        yield item

    pass
