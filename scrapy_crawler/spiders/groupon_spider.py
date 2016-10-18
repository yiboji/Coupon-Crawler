import scrapy
from groupon.items import GrouponItem

class GrouponSpider(scrapy.Spider):
	name = "groupon"
	base_url = "https://www.groupon.com/browse/los-angeles?address=Los%20Angeles%2C%20CA&administrative_area=CA&category=beauty-and-spas&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los%20Angeles"
	start_urls = [
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=salons&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=skin-care&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=hair-salons&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=cosmetic-procedures&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=massage&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=hair-removal&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=spa&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=brow-and-lash&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=makeup&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=blow-outs-and-styling&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=tanning&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles",
		"https://www.groupon.com/browse/los-angeles?category=beauty-and-spas&category2=nail-salons&address=Los+Angeles%2C+CA&administrative_area=CA&lat=34.05223&lng=-118.24368&locale=en_US&locality=Los+Angeles"
	]
	type_dict = {
		"salons":"Salons",
		"skin-care":"Face & Skin",
		"hair-salons":"Hair",
		"cosmetic-procedures":"Cosmetic Procedures",
		"massage":"Massages",
		"hair-removal":"Hair Removal",
		"spa":"Spas",
		"brow-and-lash":"Brows & Lashes",
		"makeup":"Makeup",
		"blow-outs-and-styling":"Blowouts & Styling",
		"tanning":"Tanning",
		"nail-salons":"Nails"
	}

	def parse(self, response):
		store_type = response.url.split("category2")[1].split('&')[0].strip("=")
		for content in response.xpath('//div[@class="cui-content"]'):
			subpage_url = content.xpath('a/@href').extract_first()
			merchant_name = content.xpath('a/figcaption/div/div/text()')[0].extract()
			merchant_name = self.removeNewlineSpace(merchant_name)
			sub_request = scrapy.Request(subpage_url,callback=self.detailPage)
			sub_request.meta['merchant_name'] = merchant_name
			sub_request.meta['merchant_type'] = self.type_dict[store_type]
			yield sub_request
		next_page = response.xpath('//li/a[@rel="next"]/@href').extract_first()
		next_page = response.urljoin(next_page)
		if next_page:
			print "next page: "+str(next_page)
			yield scrapy.Request(next_page, callback=self.parse)

	def detailPage(self, response):
		merchant_name = response.meta['merchant_name']
		merchant_type = response.meta['merchant_type']
		options = response.xpath('//div[@itemprop="description"]/ul[1]/li/text()').extract()
		page_title = response.xpath('//h1[@id="deal-title"]/text()').extract()[0].strip()
		address = []
		for addr in response.xpath('//*[contains(normalize-space(@class),"address")]'):
			lines = addr.xpath('p/text()')
			res = ""
			for line in lines:
				newline = self.removeNewlineSpace(line.extract()) 
				if newline:
					res += ", "+newline
			address.append(self.removeNewlineSpace(res))
		coupon_url = response.url
		image_url = response.xpath('//figure[@data-bhw="FeaturedImage"]//img/@src').extract_first()
		coupon_titles = "|".join(filter(None, options))
		for addr in address:
			item = GrouponItem()
			item['merchant_type'] = merchant_type
			item['merchant_name'] = merchant_name
			item['coupon_titles'] = coupon_titles if coupon_titles else page_title
			item['coupon_url'] = coupon_url
			item['image_url'] = image_url
			addr = addr.split('+')
			item['merchant_location'] = addr[0].strip(', ').strip()
			item['merchant_tel'] = addr[-1] if len(addr)>1 else ""
			yield item

	def removeNewlineSpace(self, str):
		return str.replace('\n','').strip()
