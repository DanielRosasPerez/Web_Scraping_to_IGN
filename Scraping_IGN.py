from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

# Abstractions (Data that I want to retrieve):
class Article(Item):
    title = Field()
    content = Field()
    
class Review(Item):
    title = Field()
    score = Field()
    
class Video(Item):
    title = Field()
    publication_date = Field()
    
# Web scraper:
class IGNcrawler(CrawlSpider):
    name = "ign"
    custom_settings = {
        "USER_AGENT":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/84.0.2",
        #"CLOSESPIDER_PAGECOUNT":500,
        'FEED_EXPORT_ENCODING': 'utf-8',
    }
    
    allowed_domains = ["latam.ign.com"] # To avoid our crawler to go to other pages distinct from those inside the domain "latam.ign.com".
    
    start_urls = ["https://latam.ign.com/se/?model=article&q=Xbox&order_by=-date"] # The SEED URL (The URL where I am going to start. SEED URL doesn't
    # mean to take the pattern we see on every page we want to scrap (To do that, we establish "rules"), it just means, to declare the URL WHERE WE
    # ARE GOING TO START.)
    
    download_delay = 1 # This way, we are going to download wait 1s between extraction and extraction.
    
    rules = (
        
        # For following the TABS (Artículos, Reviews and Video):        
        Rule(
            LinkExtractor(
                allow = r"(type|model)=(article|video|review)&q=Xbox&order_by=(-date&page=\d+|-date)",
                deny = r"^((?!date).)*$"
            ), follow = True
        ),
        
        # To "SCRAP" the ARTICLE SECTION:
        Rule(
            LinkExtractor(
                allow = r"/news/",
                restrict_xpaths = ["//div[@class='tbl']//article[contains(@id, 'content')]//div[@class='m']/h3/a"]
            ), follow = True, callback = "parse_articles"
        ),
        
        # To "SCRAP" the REVIEW SECTION:
        Rule(
            LinkExtractor(
                allow = r"/review/",
                restrict_xpaths = ["//div[@class='tbl']//article[contains(@id, 'content')]//div[@class='m']/h3/a"]
            ), follow = True, callback = "parse_reviews"
        ),
        
        # To "SCARP" the VIDEO SECTION:
        Rule(
            LinkExtractor(
                allow = r"/video/",
                restrict_xpaths = ["//div[@class='tbl']//article[contains(@id, 'content')]//div[@class='m']/h3/a"]
            ), follow = True, callback = "parse_videos"
        ),
        
        # For following the PAGINATION:
        Rule(
            LinkExtractor(
                allow = r"(type|model)=(article|video)&q=Xbox&order_by=-date&page=\d+",
                deny = r"^((?!date).)*$"
            ), follow = True
        ),
    )
    
    # PARSER METHODS FROM THIS CLASS TO EXTRACT/SCRAPE THE DESIRED DATA:
    def parse_articles(self, response):
        item = ItemLoader(Article(), response)
        item.add_xpath("title", '//h1[@id="id_title"]/text()')
        item.add_xpath("content", '//div[@id="id_text"]//*/text()')
        
        yield item.load_item()
    
    def parse_reviews(self, response):
        item = ItemLoader(Review(), response)
        item.add_xpath("title", '//div[@class="article-headline"]/h1/text()')
        item.add_xpath("score", '//div[@class="review"]//span[last()]/text()')
        
        yield item.load_item()
        
    def parse_videos(self, response):
        item = ItemLoader(Video(), response)
        item.add_xpath("title", '//h1[@id="id_title"]/text()')
        item.add_xpath("publication_date", '//span[@class="publish-date"]/text()')
        
        yield item.load_item()
