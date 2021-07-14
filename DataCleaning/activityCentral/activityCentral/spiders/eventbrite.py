import scrapy
import re
import json
from scrapy.crawler import CrawlerProcess
from datetime import datetime,timezone
from activityCentral.items import ActivitycentralItem

class EventbriteSpider(scrapy.Spider):
    name = 'eventbrite'
    allowed_domains = ['eventbrite.com']
    urls = [i.strip() for i in open('urls/eventbrite_visitedURLs_total.txt').readlines()]
    data = {}
    
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        item = ActivitycentralItem()
        size = self.check_event_page(response)
        event_ended = self.check_event_end(response)
        # the url page is not an eventbrite event details page
        # Or the event has been ended
        if size == 0 or event_ended:
            return
        # Parse application json data
        self.data = self.get_json_data(response)
        activity_ts = self.get_start_timestamp(response)
        if activity_ts == -1:
            return
        else:
            item['activity_date'] = activity_ts
        item['price'] = self.get_price(response)
        if str(item['price']).lower() == "donation":
            return
        if len(item['price']) == 0:
            return
        item['name'] = self.get_activity_name(response)
        # remove 'by' and \t
        item['organizer'] = self.get_organizer(response)
        item['description'] = self.get_description(response)
        item['platform'] = "Eventbrite"
        item['rating'] = -1
        item['location'] = self.get_location(response)[0]
        item['city'] = str(self.get_location(response)[1]).lower()
        item['state'] = str(self.get_location(response)[2]).upper()
        item['tags'] = self.get_tags(response)
        item['source'] = response.request.url
        item['price'] = self.get_price(response)
        item['thumbnail'] = self.get_thumbnail(response)
        return item
    
    def check_event_page(self, response):
        size = len(response.xpath("//body[contains(@id, 'event-page')]"))
        return size
        
    def check_event_end(self, response):
        end_xpath = '//*[@id="event-page"]/main//div[contains(@class, "has-corner-object")]/span[contains(@class, "badge")]/text()'
        is_end = response.xpath(end_xpath).extract()
        if len(is_end) != 0 and response.xpath(end_xpath).extract()[0] == 'event ended':
            return True
        return False
    
    def get_json_data(self, response):
        try:
            data_xpath = response.xpath("//script[contains(@type, 'application/ld+json')]/text()").extract()
            if len(data_xpath) == 0:
                return {'error': 'no data'}
            else:
                return json.loads(data_xpath[0].strip())
        except:
            return {'error': 'exception'}
    
    def get_activity_name(self, response):
        if "name" in self.data:
            return self.data["name"]
        else:
            activity_name = response.xpath("//h1[contains(@class, 'listing-hero-title')]/text()").extract()
            if len(activity_name) == 0:
                return ""
            return activity_name[0]
    
    def get_start_timestamp(self, response):
        if "startDate" in self.data:
            return self.datetime_to_utc(self.data["startDate"])
        else:
            date_header = response.xpath("//time[contains(@class, 'listing-hero-date')]/p/text()").extract()
            time_header = response.xpath("//div[contains(@class, 'listing-info__body')]//div[contains(@class, 'event-details')]//h3[contains(text(), 'Date and Time')]/following-sibling::div/meta/@content").extract()
            if len(date_header) != 0 and date_header[0] == "Multiple Dates":
                # -1 means the activity date is "Multiple Dates", we are unable to get the tiemstamp, so gonna ignore this
                print("Multiple event!!!!!!!!!!!")
                return -1
            elif len(time_header) == 0:
                # -1 means we can not get activity time at "Date And Time" section, we will ignore this activity
                return -1
            else:
                # Acticity Start Timestamp by UTC time zone
                return self.datetime_to_utc(time_header[0])
    
    def datetime_to_utc(self, dt):
        # date is a string
        timestamp = datetime.strptime(dt, '%Y-%m-%dT%X%z').timestamp()
        return int(timestamp)
        
    def get_organizer(self, response):
        try:
            return self.data["organizer"]["name"]
        except:
            organizer = response.xpath("//a[contains(@class, 'listing-organizer-name')]/text()").extract()
            if len(organizer) == 0:
                return ""
            return organizer[0].strip()[3:]   
    
    def get_description(self, response):
        about = response.xpath("//h2[contains(text(), 'About this Event')]//following-sibling::div").extract()
        desc = response.xpath("//h3[contains(text(), 'Description')]//following-sibling::div").extract()
        if len(about) == 0 and len(desc) == 0:
            return ""
        return desc[0] if len(about) == 0 else about[0]
    
    def get_location(self, response):
        # Return a list with 3 elements
        # The first element is the location details
        # The second element is the city
        # The third element is the state
        try:
            if "location" in self.data and "@type" in self.data["location"]:
                if self.data["location"]["@type"] == "VirtualLocation":
                    return ["Online Event", "", ""]
                elif self.data["location"]["@type"] == "Place":
                     return [self.data["location"]["name"]+","+self.data["location"]["streetAddress"], self.data["location"]["addressLocality"], self.data["location"]["addressRegion"]]
        except:
            location = response.xpath("//div[contains(@class, 'listing-info__body')]//div[contains(@class, 'event-details')]//h3[contains(text(), 'Location')]/following-sibling::div/p/text()").extract()
            if len(location) == 0:
                return ["", "", ""]
            location = [i.strip() for i in location if bool(re.search('[a-zA-Z]', i))]
            if str(location[0]).lower() == "online event":
                # Online Event
                return [location[0], "", ""]
            else:
                return [", ".join(location), location[-1].split(",")[0].strip(), location[-1].split(",")[1].strip().split(" ")[0]]
  
    def get_tags(self, response):
        res = response.xpath("//a[contains(@class, 'listing-tag')]/span/text()").extract()
        if len(res) == 0:
            return []
        else:
            tags = [i[1:] for i in res if str(i).startswith("#")]
            return tags
    
    def get_price(self, response):
        price = response.xpath("//div[contains(@class, 'js-display-price')]/text()").extract()
        if len(price) == 0:
            return ""
        return price[1].strip()
    
    def get_thumbnail(self, response):
        if "image" in self.data:
            return self.data["image"]
        else:
            thumbnail = response.xpath("//picture/@content").extract()
            if len(thumbnail) == 0:
                return ""
            return thumbnail[0]