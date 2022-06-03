import scrapy


class PolsatnewsspiderSpider(scrapy.Spider):
    name = 'PolsatNewsSpider'
    allowed_domains = ['https://www.polsatnews.pl/wiadomosci/polska/']
    start_urls = ['http://https://www.polsatnews.pl/wiadomosci/polska//']

    def parse(self, response):
        pass
