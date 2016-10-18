# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import unicodecsv as csv
import googleapi
import datetime
import calendar
from scrapy.exceptions import DropItem

class CsvWriterPipeline(object):
	def __init__(self):
		self.file = open("groupon.csv",'wb')
		self.writer = csv.writer(self.file,delimiter=',')
		self.writer.writerow("CompanyID,Type,CompanyName,Location,CompanyCoordinate,Radius,Tel,Title,ExpireDate,CouponSource,CouponSourceURL,CouponSourceLogoURL,ImageURL".split(','))
	def process_item(self,item,spider):
		row = []
		row.append(item['merchant_id'])
		row.append(item['merchant_type'])
		row.append(item['merchant_name'])
		row.append(item['merchant_location'])
		row.append(item['merchant_coord'])
		row.append(item['radius'])
		row.append(item['merchant_tel'])
		row.append(item['coupon_titles'])
		row.append(item['expire_date'])
		row.append(item['coupon_source'])
		row.append(item['coupon_url'])
		row.append(item['coupon_log_url'])
		row.append(item['image_url'])
		self.writer.writerow(row)
		return item

class FilterPipeline(object):
	def process_item(self,item,spider):
		for key in item:
			item[key] = item[key].replace('\n',' ')
		return item

class OrganizePipeline(object):
	def process_item(self,item,spider):
		#item['merchant_type'] = u"Beauty & Spas"
		item['radius'] = u"200"
		item['coupon_log_url'] = u"http://www.cincinnaticents.com/wp-content/uploads/2016/04/groupon-logo.png"
		geoloc = googleapi.getGeoLocation(item['merchant_location'])
		item['merchant_coord'] = str(geoloc['lat'])+','+str(geoloc['lng'])
		#item['merchant_coord'] = ''
		item['coupon_source'] = u"Groupon"
		today = datetime.date.today()
		_, lastday_of_month = calendar.monthrange(today.year,today.month)
		expire_date = datetime.date(today.year,today.month,lastday_of_month)
		item['expire_date'] = str(expire_date.month)+'/'+str(expire_date.day)+'/'+str(expire_date.year)
		item['merchant_id'] = item['merchant_name']+'_'+item['merchant_coord']+'_'+item['expire_date']
		return item
		
class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['merchant_id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['merchant_id'])
            return item
