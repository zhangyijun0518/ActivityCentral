import scrapy
import json


class TestSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['test.com']
    # start_urls = ['https://www.tripadvisor.com/AttractionProductReview-g33020-d21060936-The_best_of_San_Jose_walking_tour-San_Jose_California.html']
    
    def start_requests(self):
        url = 'https://eventsget.com/events/view/united-states/training-or-development-class/november-2020/MzU3NDc='
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        
        print(response.xpath("//h1/text()").extract())
