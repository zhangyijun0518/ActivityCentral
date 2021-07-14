# Scrapy settings for activityCentral project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'activityCentral'

SPIDER_MODULES = ['activityCentral.spiders']
NEWSPIDER_MODULE = 'activityCentral.spiders'

ITEM_PIPELINES = {
    'activityCentral.pipelines.ActivitycentralPipeline': 1
}
# # ELASTICSEARCH_CLOUD_ID = 'i-o-optimized-deployment:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDZlMDdiZGFiMjE3NzQ3ZTRiZWIyZjYzNGY3MTkxYWFkJDE5NDE1MWJiNTU4ZTRlNmY5YTZiMjBmZDYzMjUyZWQ4'
# ELASTICSEARCH_HOST = 'https://search-activitycentral-3ijgjqeqjwhttatbqbhgt445ia.us-east-2.es.amazonaws.com'
# ELASTICSEARCH_USERNAME = ''
# ELASTICSEARCH_PASSWORD = ''
# # ELASTICSEARCH_USERNAME = 'elastic'
# # ELASTICSEARCH_PASSWORD = 'cp0L47hjYNuPwv1axfTtRJX4'
ELASTICSEARCH_INDEX = 'ac'
ELASTICSEARCH_TYPE = 'activity'
ELASTICSEARCH_UNIQ_KEY = ['name', 'activity_date', 'organizer']

# # Elasticsearch
# ITEM_PIPELINES = {
#     'scrapyelasticsearch.scrapyelasticsearch.ElasticSearchPipeline': 100
# }
# ELASTICSEARCH_SERVERS = 'https://elastic:zbHuT1P9cPi2N4W9uNYK8SCk@aa918599a5db44da9910ec2d0a8a5b0a.us-east-1.aws.found.io:9243' 
# ELASTICSEARCH_INDEX = 'ac'
# ELASTICSEARCH_TYPE = 'activity'



# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'activityCentral (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'
# Obey robots.txt rules
ROBOTSTXT_OBEY = True
CLOSESPIDER_ERRORCOUNT = 10

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'activityCentral.middlewares.ActivitycentralSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'activityCentral.middlewares.ActivitycentralDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'activityCentral.pipelines.ActivitycentralPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
