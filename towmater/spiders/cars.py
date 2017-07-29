# -*- coding: utf-8 -*-

import scrapy

class CarsSpider(scrapy.Spider):
    name = 'cars'
    allowed_domains = ['carsalesnetwork.com.au']
    start_urls = ['http://csndealers.carsalesnetwork.com.au/listing?dealerId=AGC-SELLER-28894%2BAGC-SELLER-14679%2BAGC-SELLER-51021']
            
    def start_requests(self):
            #-----------------------------------------------------------
            # set user agent, bot goes undercoverimitate browser 
            # remove this then the scraper will be rejected by the target
            headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
            for url in self.start_urls:
                yield scrapy.Request(url, headers=headers)
        
    def parse(self, response):
        #--- wrapper search result
        cars = response.xpath('//div[@class="search-results"]')
        for car in cars:
            #---- wrapper car list
            x = car.xpath('//div[@class="result-item"]')
            for y in x:
                name = y.xpath('//h4[@class="result-item-title"]/a/text()').extract_first()
                yield {'x':name}
