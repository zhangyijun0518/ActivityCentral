import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.select import Select
import time
from optparse import OptionParser
import sys
import re
from bs4 import BeautifulSoup

import requests

urlFileName = ""


startURLs = []
startURLs.append('https://www.meetup.com/find/us--ca--san-jose')
startURLs.append('https://www.meetup.com/find/us--ca--san-francisco')
startURLs.append('https://www.meetup.com/find/us--ca--los-angeles')
startURLs.append('https://www.meetup.com/find/us--ny--new-york')
startURLs.append('https://www.meetup.com/find/us--wa--seattle')
startURLs.append('https://www.meetup.com/find/us--or--portland')
startURLs.append('https://www.meetup.com/find/us--fl--miami')
startURLs.append('https://www.meetup.com/find/us--ma--boston')
startURLs.append('https://www.meetup.com/find/us--dc--washington')
startURLs.append('https://www.meetup.com/find/us--nv--las-vegas')

def newGetPage(url):
	global urlFileName
	browser = webdriver.Chrome()
	index = 0
	urlFileName = "/Users/hwen/Downloads/Archive/output/urls/manual_meetup_visitedURLs_{}.txt".format(index)
	browser.get(startURLs[index])
	time.sleep(5)
	currentCount = 0
	while True:
		try:
			result = browser.find_element_by_xpath('//button[text()="Show more events"]')
			result.click()
		except Exception as e:
			print "not able to click more events we continue to next"
			index = index + 1
			urlFileName = "/Users/hwen/Downloads/Archive/output/urls/manual_meetup_visitedURLs_{}.txt".format(index)
			browser.get(startURLs[index])
			time.sleep(10)

		html = browser.page_source
		soup = BeautifulSoup(html, 'html.parser') 
		currentCount = getLinks(soup)
		if currentCount > 2000:
			print "we switch to next wepage"
			index = index + 1
			urlFileName = "/Users/hwen/Downloads/Archive/output/urls/manual_meetup_visitedURLs_{}.txt".format(index)
			# browser.quit()
			# browser = webdriver.Chrome()
			browser.get(startURLs[index])
			time.sleep(10)

def shouldVisit3(url):
	if "meetup.com" not in url:
		return False
	if 'events' in url:
		x = re.search("[0-9]{9}", url)
		if x:
			return True
		trail = url.split("events")[-1]
		if len(trail) > 3:
			return True
	return False

def getLinks(soup):
	urlsToCrawl = []
	for link in soup.findAll('a', href=True):
		#link['href'] = urllib.parse.urljoin(urlsToCrawl[0], link['href'])
		if '.pdf' not in link['href'] and '.jpg' not in link['href']:
			if 'javascript' not in link['href']:
				if 'css' not in link['href']:
					if 'meetup.com' in link['href']:
						urlsToCrawl.append(link['href'])


	with open(urlFileName, 'w') as f:
		for url in urlsToCrawl:
			if not shouldVisit3(url):
				continue
			try:
				nURL = url.encode('utf-8')
				f.write("%s\n" % nURL)
			except Exception as e:
				print "cannot write url"
			
	
	print file_len(urlFileName)
	return file_len(urlFileName)

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

if __name__ == '__main__':


	actualURL = "https://www.meetup.com/find/us--ca--san-jose"

	print "actualURL %s" % actualURL

	newGetPage(actualURL)





