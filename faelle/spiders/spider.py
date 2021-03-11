import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FaelleItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FaelleSpider(scrapy.Spider):
	name = 'faelle'
	start_urls = ['https://www.faelleskassen.dk/nyheder/?page=1']

	def parse(self, response):
		post_links = response.xpath('//a[@itemprop="url"]/@href').getall()[:-1]
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@aria-label="Next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//span[@class="date"]/text()').get()
		title = ' '.join(response.xpath('//h1/text() | //h5/text()').getall())
		content = response.xpath('//div[contains(@class,"col-md-8 ")]//text()[not (ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FaelleItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
