# -*- coding: utf-8 -*-

# Define your item pipelines here
# Strip html
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from w3lib.html import remove_tags

class CleanerPipeline(object):
    def process_item(self, item, spider):
        for the_data in item:
            if the_data == 'car_id':
                # split the url to get the car id
                # pattern example:
                # "/details/2014-hyundai-santa-fe-active-dm/OAG-AD-14537324?dealerId=n"
                # expected: OAG-AD-14537324
                url_detail = item['car_id'].rsplit('/',1)[-1]
                url_detail = url_detail.rsplit('?',1)[0]
                item['car_id'] = url_detail
            elif the_data == 'price':
                item['price'] = re.sub('[\r\n\t$*,]', '', remove_tags(item['price'].strip()))
            elif the_data == 'listing_feature':
                the_feature = []
                for list_feature in item['listing_feature']:
                    the_feature.append(list_feature.strip())

                item['listing_feature'] = ','.join(the_feature)
            else:
                if type(item[the_data]) is str or type(item[the_data]) is unicode:
                    item[the_data] = re.sub('[\r\n\t]', '', remove_tags(item[the_data].strip()))
                else:
                    x = type(item[the_data])
                    print "the data: {} not string but {}".format(the_data,x)

        return item