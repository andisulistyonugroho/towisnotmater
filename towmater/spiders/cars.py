# -*- coding: utf-8 -*-

import scrapy

class CarsSpider(scrapy.Spider):
    name = 'cars'
    allowed_domains = ['carsalesnetwork.com.au']
    start_urls = ['http://csndealers.carsalesnetwork.com.au/listing?dealerId=AGC-SELLER-28894%2BAGC-SELLER-14679%2BAGC-SELLER-51021']
        
    def parse(self, response):
        #--- wrapper search result
        cars = response.xpath('//div[@class="search-results"]')
        for car in cars:
            #---- wrapper car list
            x = car.xpath('.//div[@class="result-item"]')
            for y in x:
                name = y.xpath('.//h4[@class="result-item-title"]/a/text()').extract_first()
                price = y.xpath('.//div[@class="price"]/a/text()').extract_first()
                yield {
                    'name': name,
                    'price': price
                }
        
        next_page = response.xpath('//ul[@class="pagination pull-right"]/li[@class="active"]/following-sibling::li/a/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
            