import scrapy
import re
import json
from scrapy.crawler import CrawlerProcess
from datetime import datetime,timezone
from activityCentral.items import ActivitycentralItem


class EventsgetSpider(scrapy.Spider):
    name = 'eventsget'
    allowed_domains = ['www.eventsget.com']
    urls = [i.strip() for i in open('urls/eventsget_visitedURLs_total.txt').readlines() if len(i.strip()) != 0 and "eventsget.com/events/view" in i]
    us_states = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands':'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }
    
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        item = ActivitycentralItem()
        item['name'] = self.get_activity_name(response)
        item['activity_date'] = self.get_start_timestamp(response)
        if item['activity_date'] == -1:
            print("No Date!!!!!!!!!!!!!!!!!!!!")
            return
        # # remove 'by' and \t
        item['organizer'] = self.get_organizer(response)
        item['description'] = self.get_description(response)
        item['platform'] = "Eventsget"
        item['rating'] = -1
        item['location'] = self.get_location(response)[0]
        item['city'] = str(self.get_location(response)[1]).lower()
        item['state'] = str(self.get_location(response)[2]).upper()
        item['tags'] = []
        item['source'] = response.request.url
        item['price'] = self.get_price(response)
        if str(item['price']) == '-1':
            print("No price!!!!!!!!!!!!!!!")
            return
        item['thumbnail'] = self.get_thumbnail(response)
        return item
    
    def get_activity_name(self, response):
        name_xpath = response.xpath("//h1/text()").extract()
        return name_xpath[0]
    
    def get_start_timestamp(self, response):
        date_xpath = response.xpath("//div[contains(@class, 'event-info')]//div[contains(text(), 'Date')]/following-sibling::div/b/text()").extract()
        if len(date_xpath) == 0 :
            return -1
        else:
            time = date_xpath[0].strip()
            return self.datetime_to_utc(time)
    
    def datetime_to_utc(self, dt):
        # date is a string
        timestamp = datetime.strptime(dt, '%d-%m-%Y').timestamp()
        timestamp += (24+7)*60*60-1
        return int(timestamp)
        
    
    def get_organizer(self, response):
        organizer = response.xpath("//div[@id = 'my-tab-content']//div[@id='section-1']/div[@class='section-list']/div/text()").extract()
        return organizer[1].strip()
    
    def get_description(self,response):
        description = response.xpath("//div[@id = 'my-tab-content']//div[@id='section-2']").extract()
        return description[0]
    
    def get_price(self, response):
        price_xpath = response.xpath("//div[@id = 'my-tab-content']//div[@id='section-3']//div[contains(text(), 'Registration Fees Details')]/following-sibling::div/span/text()").extract()
        if len(price_xpath) == 0:
            return "-1"
        price = price_xpath[0].split("\n")
        temp = []
        for i in price:
            temp += i.split(" ")
        price = []
        for j in temp:
            t = re.sub('[!@#$,./?]', '', j)
            if t.isdigit():
                price.append(float(re.sub('[!@#$,/?]', '', j)))
        if len(price) == 0:
            return "-1"
        min_price = min(price)
        max_price = max(price)
        if min_price == max_price:
            if int(min_price) == 0:
                return "Free"
            else:
                return "$"+str(int(min_price))
        else:
            return "$"+str(int(min_price))+" - "+"$"+str(int(max_price))
    
    def get_location(self, response):
        location_xpath = response.xpath("//div[@id = 'my-tab-content']//div[@id='section-4']//div[contains(text(), 'Address/Venue')]/following-sibling::div/span/text()").extract()
        if "online" in location_xpath[0].lower() or 'webinar' in location_xpath[0].lower() or 'virtual' in location_xpath[0].lower():
            return ["Online Event", "", ""]
        location = location_xpath[0].strip().replace('\n', ', ')
        city_state_xpath = response.xpath("//div[@id = 'my-tab-content']//div[@id='section-1']//div[contains(text(), 'Location')]/following-sibling::div/text()").extract()
        city_state = city_state_xpath[0].strip().split(",")
        return [location, city_state[0].lower(), self.us_states[city_state[1].strip()]]
    
    def get_thumbnail(self, response):
        try:
            img_xpath = response.xpath("//div[contains(@class, 'event-info')]//img/@src").extract()
            return img_xpath[0]
        except:
            return ""
        