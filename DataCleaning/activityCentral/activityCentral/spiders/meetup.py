import scrapy
import re
from scrapy.crawler import CrawlerProcess
from datetime import datetime,timezone
from activityCentral.items import ActivitycentralItem


class MeetupSpider(scrapy.Spider):
    name = 'meetup'
    allowed_domains = ['meetup.com']
    # urls = [i.strip() for i in open('../../Crawler/output/urls/meetup_visitedURLs_total.txt').readlines() if len(i.strip()) != 0]
    urls = [i.strip() for i in open('urls/meetup_visitedURLs_total.txt').readlines() if len(i.strip()) != 0 and "www.meetup.com" in i]
    
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        item = ActivitycentralItem()
        if self.is_event_page(response) == 0:
            print("not a event page!!!!")
            return
        if self.is_past_event(response) != 0:
            print("is a past event!!!!")
            return
        if self.is_private_card(response) != 0:
            print("is a private event!!!")
            return
        item['name'] = self.get_activity_name(response)
        item['activity_date'] = self.get_start_timestamp(response)
        if item['activity_date'] == 0:
            return
        item['organizer'] = self.get_organizer(response)
        item['description'] = self.get_description(response)
        item['location'] = self.get_location(response)[0]
        item['city'] = str(self.get_location(response)[1]).lower()
        item['state'] = str(self.get_location(response)[2]).upper()
        item['platform'] = "Meetup"
        item['rating'] = -1
        item['tags'] = []
        item['source'] = response.request.url
        item['price'] = self.get_price(response)
        item['thumbnail'] = self.get_thumbnail(response)
        return item
    
    def is_private_card(self, response):
        private_path = response.xpath("//div[contains(@class, 'eventContent')]//div[contains(@class, 'privateCard')]")
        return len(private_path)
    
    def is_event_page(self, response):
        event_home_path = response.xpath("//div[contains(@class, 'event-home')]").extract()
        return len(event_home_path)
    
    def is_past_event(self, response):
        # True is past event
        # False is not past event
        return len(response.xpath("//div[contains(@class, 'sticky--bottom')]//span[contains(text(), 'Past event')]"))
    
    def get_activity_name(self, response):
        return response.xpath("//h1/text()").extract()[0]
    
    def get_start_timestamp(self, response):
        try:
            return int(response.xpath("//time/@datetime").extract()[0])//1000
        except:
            return 0
    
    def get_location(self, response):
        # Return a list with 3 elements
        # The first element is the location details
        # The second element is the city
        # The third element is the state
        is_online_event = response.xpath("//address/p/text()").extract()
        if len(is_online_event) == 0:
            return ["No address provided", "", ""]
        if str(is_online_event[0]).lower() == "online event":
            return ["Online Event", "", ""]
        # avenue = response.xpath("//address/p[contains(@class, 'venueDisplay-venue-address text--secondary')]/text()").extract()
        avenue = response.xpath("//address/p/text()").extract()
        avenue = [i.strip() for i in avenue if bool(re.search('[a-zA-Z]', i))]
        city_state = response.xpath("//address/p[contains(@class, 'venueDisplay-venue-address text--secondary')]/span/text()").extract()
        city_state = [i.strip() for i in city_state if bool(re.search('[a-zA-Z]', i))]
        location = [", ".join(avenue+city_state), city_state[0], city_state[1]]
        return location
        
    def get_organizer(self, response):
        return response.xpath("//span[contains(text(), 'Hosted by')]/span/text()").extract()[0]   
    
    def get_description(self, response):
        return response.xpath("//div[contains(@class, 'event-description runningText')]/p").extract()[0]
    
    def get_price(self, response):
        price_path = response.xpath("//div[contains(@class, 'sticky--bottom')]//span[contains(@data-e2e, 'event-footer--price-label')]/span/text()").extract()[0]
        if str(price_path).lower() == "free":
            return "Free"
        return price_path
    
    def get_thumbnail(self, response):
        thumb_path = response.xpath("//div[@class='eventContent']//div[contains(@class, 'photoCarousel-photoContainer keepAspect--16-9')]//@style").extract()
        if len(thumb_path) == 0:
            return ""
        else:
            url = thumb_path[0].split(":")[2][:-1]
            return "https:"+url
    
        
        
        
