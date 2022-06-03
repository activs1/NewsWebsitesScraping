import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from itemloaders import ItemLoader
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags
import json

def format_date(value):
    output = value[0:10]
    return output


def clean_text(value):
    tvp_function = "function resizeIframe(obj) {        if(obj.contentWindow) "\
                "{            obj.style.height = "\
                "obj.contentWindow.document.body.scrollHeight + 'px';        "\
                "}    }    var iframe = "\
                "document.querySelector(\'.map-corona\');    "\
                "window.addEventListener(\'resize\', "\
                "resizeIframe.bind(iframe));    @media (min-width: 1024px) "\
                "{        .map-corona {            height: 640px;        }    "\
                "} resizeIframe.bind()); Tweetnij Skomentuj Wyślij Podziel".split(' ')

    items_to_replace = [u'\xa0', u'\xc4', '/', '#'] + tvp_function
    for item in items_to_replace:
        value = value.replace(item, '')

    return value.strip()


#print(clean_text('<h1>Autystyczny chłopiec nie zostanie wydany Holendrom. Jest kolejna decyzja polskiego sądu</h1>'))


class TVPInfoArticleItem(scrapy.Item):
    ArticleTitle = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text), output_processor=TakeFirst())
    ArticleText = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text), output_processor=Join())
    ArticleAuthor = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text), output_processor=TakeFirst())
    ArticleDate = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text, format_date), output_processor=TakeFirst())
    ArticleTags = scrapy.Field(input_processor=MapCompose(remove_tags, clean_text))


class TvpinfoSpider(scrapy.Spider):
    name = 'TVPInfoSpider'
    allowed_domains = ['tvp.info']
    start_urls = ['https://tvp.info/polska']
    page_number = 1
    number_of_articles = 0
    custom_settings = {
        'FEEDS': {'TVPInfoArticles.csv': {
            'format': 'csv',
            'overwrite': True,
        }
        },
        'CLOSESPIDER_ITEMCOUNT': 5000
    }

    def parse(self, response):
        script = ''.join(response.xpath('//script/text()').extract())
        i = script.find("items")
        j = script.find("items_total_count")

        script = script[i+7:j-3]

        j = json.loads(script)
        i = 0
        for item in j:
            article_url = 'https://' + self.allowed_domains[0] + item['url']
            yield response.follow(article_url, callback=self.parse_article)

        self.page_number += 1
        next_page = self.start_urls[0] + f'?page={self.page_number}'
        yield response.follow(next_page, callback=self.parse)


    def parse_article(self, response):
        loader = ItemLoader(item=TVPInfoArticleItem(), selector=response)
        loader.add_css('ArticleTitle', 'h1')
        loader.add_css('ArticleText', '.am-article__heading')
        loader.add_css('ArticleText', '.article-layout')
        loader.add_css('ArticleAuthor', '.name')
        loader.add_css('ArticleDate', '.date')
        loader.add_css('ArticleTags', '.article-tags__tag')

        item = loader.load_item()
        #print(item)
        yield item
