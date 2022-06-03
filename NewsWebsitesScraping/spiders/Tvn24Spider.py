import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from itemloaders import ItemLoader
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags
#import scraper_settings

month_map = {"stycznia": "01",
             "lutego": "02",
             "marca": "03",
             "kwietnia": "04",
             "maja": "05",
             "czerwca": "06",
             "lipca": "07",
             "sierpnia": "08",
             "września": "09",
             "października": "10",
             "listopada": "11",
             "grudnia": "12"}

def format_date(value):
    try:
        date = value.split(' ')
        month = month_map[date[1]]

        return (date[0] + '.' + month + '.' + date[2]).replace(',', '')
    except:
        return value


def clean_text(value):
    tvn_function = 'NA TELEWIZJĘ ŻYWO TVN24 GO &gt; OGLĄDAJ INTERNECIE CZYTAJ WIĘCEJ FAKTY FAKTACH'.split(' ')

    items_to_replace = [u'\xa0', u'\xc4', '/', '#'] + tvn_function
    new_value = value
    for item in items_to_replace:
        new_value = new_value.replace(item, '')

    return new_value


class Tvn24ArticleItem(scrapy.Item):
    ArticleTitle = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text), output_processor=TakeFirst())
    ArticleText = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text), output_process=Join())
    ArticleAuthor = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text), output_processor=TakeFirst())
    ArticleDate = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text, format_date), output_processor=TakeFirst())
    ArticleTags = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text))


class Tvn24Spider(scrapy.Spider):
    name = 'Tvn24Spider'
    allowed_domains = ['tvn24.pl']
    start_urls = ['https://tvn24.pl/polska']
    page_number = 1
    number_of_articles = 0
    custom_settings = {
        'FEEDS': {'Tvn24Articles.csv': {
            'format': 'csv',
            'overwrite': True,
        }
        },
        'CLOSESPIDER_ITEMCOUNT': 5000
    }

    def parse(self, response):
        print(f"Page number: {self.page_number}")
        print('\n\n')
        articles = response.css('.teaser-wrapper')
        for article in articles:
            article_url = article.css('.link__content > a::attr(href)').extract_first()
            if article_url:
                self.number_of_articles += 1
                yield response.follow(article_url, callback=self.parse_article)

        self.page_number += 1
        next_page = self.start_urls[0] + f"/{self.page_number}"
        yield response.follow(next_page.strip(), callback=self.parse)

    def parse_article(self, response):
        loader = ItemLoader(item=Tvn24ArticleItem(), selector=response)
        loader.add_css('ArticleTitle', 'h1')
        loader.add_css('ArticleAuthor', '.author-first-name')
        loader.add_css('ArticleDate', '.article-top-bar__date')
        loader.add_css('ArticleTags', '.article-tag')
        loader.add_css('ArticleText', '.paragraph')

        item = loader.load_item()
        yield item

