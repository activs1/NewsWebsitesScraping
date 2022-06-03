import scrapy

class Word(scrapy.Item):
    word = scrapy.Field()

class MostUsedWordsSpider(scrapy.Spider):
    name = 'MostUsedWordsSpider'
    allowed_domains = ['pl.wiktionary.org']
    start_urls = ['https://pl.wiktionary.org/wiki/Indeks:Polski_-_Najpopularniejsze_s%C5%82owa_1-1000_wersja_Jerzego_Kazojcia']

    def parse(self, response):
        parser_output = response.css('.mw-parser-output')
        parser_output = parser_output.css('p')[1]
        words_hrefs = parser_output.css('a')
        words = []
        for href in words_hrefs:
            if href:
                word = href.css('::text').extract_first()
                item = Word()
                item['word'] = word
                words.append(word)
                yield item

