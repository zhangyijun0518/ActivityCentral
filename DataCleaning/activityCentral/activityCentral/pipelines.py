# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


class ActivitycentralPipeline:
    
    def __init__(self, es_index, es_type):
        self.es_index = es_index
        self.es_type = es_type
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            es_index = crawler.settings.get('ELASTICSEARCH_INDEX'),
            es_type = crawler.settings.get('ELASTICSEARCH_TYPE'),
        )
    
    def open_spider(self, spider):
        host = 'search-activitycentral-3ijgjqeqjwhttatbqbhgt445ia.us-east-2.es.amazonaws.com'
        region = 'us-east-2'
        service = 'es'
        ACCESS_KEY = 'AKIAIOMQ5YQ5EIVEFU2A'
        SECRET_KEY = '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'
        awsauth = AWS4Auth(ACCESS_KEY, SECRET_KEY, region, service)
        self.client = Elasticsearch(
            hosts = [{'host': host, 'port': 443}],
            http_auth = awsauth,
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection
        )
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        duplication = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "match": {
                                "name.keyword": adapter.get("name")
                            }
                        }, 
                        {
                            "match": {
                                "organizer.keyword": adapter.get("organizer")
                            }
                        },
                        {
                            "match": {
                                "activity_date": adapter.get("activity_date")
                            }
                        }
                    ]
                }
            }
        }
        check = self.client.search(index=self.es_index, doc_type=self.es_type, body=duplication)
        if check.get("hits").get("total").get("value") == 0:
            self.client.index(index=self.es_index, doc_type=self.es_type, body=adapter.asdict())
        return item

    def close_spider(self, spider):
        pass